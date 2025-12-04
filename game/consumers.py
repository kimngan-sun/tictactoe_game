import random
import time
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
from game.helpers import checkWin, isDraw
from game.models import GameRecord, Room

# ========== ASYNC HELPERS ==========
@sync_to_async
def get_room_by_code(code):
    return Room.objects.select_related('player_x', 'player_o').get(code=code)

@sync_to_async
def save_room(room):
    room.save()

@sync_to_async
def get_room_players(room):
    return {
        'player_x': room.player_x,
        'player_o': room.player_o
    }

@sync_to_async
def create_game_record(room, result, winner_user, duration):
    return GameRecord.objects.create(
        room=room,
        result=result,
        winner=winner_user,
        duration_seconds=duration,
    )

@sync_to_async
def update_user_stats(user_x, user_o, winner_user, loser_user, is_draw=False):
    if is_draw:
        if user_x:
            user_x.draws += 1
            user_x.save()
        if user_o:
            user_o.draws += 1
            user_o.save()
    else:
        if winner_user:
            winner_user.wins += 1
            winner_user.save()
        if loser_user:
            loser_user.losses += 1
            loser_user.save()


class GameConsumer(AsyncJsonWebsocketConsumer):
    board_template = {str(i): '' for i in range(9)}

    def get_cache_key(self, suffix):
        return f"room_{self.room_code}_{suffix}"

    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['code']
        
        try:
            self.room = await get_room_by_code(self.room_code)
        except Room.DoesNotExist:
            await self.accept()
            await self.send_json({"event": "error", "message": "Room không tồn tại!"})
            await self.close()
            return
            
        self.group_name = f"group_{self.room_code}"

        players_key = self.get_cache_key('players')
        players = cache.get(players_key, [])
        if players is None:
            players = []

        if self.channel_name in players:
            players.remove(self.channel_name)

        if len(players) >= 2:
            await self.accept()
            await self.send_json({"event": "show_error", "error": "Phòng đã full"})
            await self.close()
            return

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        players.append(self.channel_name)
        cache.set(players_key, players, timeout=7200)

        # Lưu tạm user vào cache (chờ đủ 2 người
        temp_users_key = self.get_cache_key('temp_users')
        temp_users = cache.get(temp_users_key, [])
        temp_users.append(self.scope['user'])
        cache.set(temp_users_key, temp_users, timeout=7200)

        if len(players) == 1:
            # Chờ đối thủ
            self.room.status = 'waiting'
            await save_room(self.room)
            await self.send_json({"event": "waiting", "message": "Đang chờ đối thủ..."})
        elif len(players) == 2:
            # Khi đủ 2 người → lưu DB, cập nhật player_x / player_o
            self.room.player_x = temp_users[0]
            self.room.player_o = temp_users[1]
            self.room.status = 'playing'
            await save_room(self.room)
            cache.delete(temp_users_key)
            await self.start_game(players)

    async def start_game(self, players):
        first_player = random.choice(players)
        game_state_key = self.get_cache_key('state')
        cache.set(game_state_key, {
            'board': self.board_template.copy(),
            'current_turn': first_player,
            'players': players,
            'start_time': time.time()
        }, timeout=7200)

        for ch_name in players:
            await self.channel_layer.send(ch_name, {
                "type": "game_data",
                "data": {
                    "event": "game_start",
                    "board": self.board_template,
                    "myTurn": ch_name == first_player,
                    "symbol": "X" if ch_name == first_player else "O"
                }
            })

    async def receive_json(self, content, **kwargs):
        event = content.get("event")
        board = content.get("board", self.board_template)

        if event == "boardData_send":
            await self.handle_board_update(board)
        elif event == "restart":
            players_key = self.get_cache_key('players')
            players = cache.get(players_key, [])
            if len(players) == 2:
                await self.start_game(players)

    async def handle_board_update(self, board):
        game_state_key = self.get_cache_key('state')
        game_state = cache.get(game_state_key)
        players_key = self.get_cache_key('players')
        players = cache.get(players_key, [])

        if not game_state or game_state['current_turn'] != self.channel_name:
            await self.send_json({"event": "error", "message": "Chưa đến lượt của bạn!"})
            return

        winner_symbol = checkWin(board)
        is_draw = isDraw(board)
        end_game = winner_symbol or is_draw

        if end_game:
            # ✅ FIX: Lấy players qua helper async
            players_data = await get_room_players(self.room)
            user_x = players_data['player_x']
            user_o = players_data['player_o']
            
            # ✅ Logic rõ ràng hơn
            winner_user = None
            loser_user = None
            
            if winner_symbol == 'X':
                winner_user = user_x
                loser_user = user_o
            elif winner_symbol == 'O':
                winner_user = user_o
                loser_user = user_x
            # Nếu hòa: cả 2 đều None
            
            duration_seconds = int(time.time() - game_state.get('start_time', time.time()))

            # Lưu game record
            await create_game_record(
                room=self.room,
                result='draw' if is_draw else winner_symbol,
                winner_user=winner_user,
                duration=duration_seconds
            )
            
            # ✅ FIX: Cập nhật stats đúng
            await update_user_stats(
                user_x=user_x,
                user_o=user_o,
                winner_user=winner_user,
                loser_user=loser_user,
                is_draw=is_draw
            )

            self.room.status = 'finished'
            await save_room(self.room)

            await self.channel_layer.group_send(self.group_name, {
                "type": "game_data",
                "data": {
                    "event": "won" if winner_symbol else "draw",
                    "board": board,
                    "winner": winner_symbol if winner_symbol else "draw",
                    "myTurn": False
                }
            })
            
            # ✅ Clear cache sau khi game kết thúc
            cache.delete(game_state_key)
            cache.delete(players_key)
            return

        # Nếu chưa kết thúc, chuyển lượt
        next_player = [p for p in players if p != self.channel_name][0] if len(players) == 2 else None
        if next_player:
            game_state['board'] = board
            game_state['current_turn'] = next_player
            cache.set(game_state_key, game_state, timeout=7200)

        for ch_name in players:
            await self.channel_layer.send(ch_name, {
                "type": "game_data",
                "data": {
                    "event": "boardData_send",
                    "board": board,
                    "myTurn": ch_name == next_player
                }
            })

    async def disconnect(self, code):
        players_key = self.get_cache_key('players')
        players = cache.get(players_key, [])

        if self.channel_name in players:
            players.remove(self.channel_name)
            if players:
                cache.set(players_key, players, timeout=7200)
            else:
                cache.delete(players_key)
                cache.delete(self.get_cache_key('state'))

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        await self.channel_layer.group_send(self.group_name, {
            "type": "game_data",
            "data": {
                "event": "opponent_left",
                "board": self.board_template,
                "myTurn": False
            }
        })

    async def game_data(self, event):
        await self.send_json(event["data"])