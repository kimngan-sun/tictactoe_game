import random
from channels.generic.websocket import AsyncJsonWebsocketConsumer 
from django.core.cache import cache
from game.helpers import checkWin, isDraw

class GameConsumer(AsyncJsonWebsocketConsumer):

    # ===== SỬA: Đổi int keys thành string keys =====
    board_template = {
        '0': '', '1': '', '2': '',
        '3': '', '4': '', '5': '',
        '6': '', '7': '', '8': '',
    }

    def get_cache_key(self, suffix):
        """Helper để tạo cache key"""
        return f"room_{self.room_id}_{suffix}"

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['id']
        self.group_name = f"group_{self.room_id}"

        players_key = self.get_cache_key('players')
        players = cache.get(players_key, [])
        
        if self.channel_name in players:
            players.remove(self.channel_name)
        
        print(f"[DEBUG] Room {self.room_id}: Current players = {len(players)}")
        print(f"[DEBUG] Players list: {players}")
        print(f"[DEBUG] New connection: {self.channel_name}")
        
        if len(players) >= 2:
            await self.accept()
            await self.send_json({"event": "show_error", "error": "Phòng đã full"})
            await self.close()
            print(f"[DEBUG] Room full, rejecting connection")
            return

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        players.append(self.channel_name)
        cache.set(players_key, players, timeout=7200)
        
        print(f"[DEBUG] After adding: {len(players)} players")

        if len(players) == 1:
            await self.send_json({
                "event": "waiting",
                "message": "Đang chờ đối thủ..."
            })
            print(f"[DEBUG] Player 1 waiting...")
        
        elif len(players) == 2:
            print(f"[DEBUG] Starting game with 2 players")
            await self.start_game(players)

    async def start_game(self, players):
        """Bắt đầu game mới"""
        first_player = random.choice(players)
        
        game_state_key = self.get_cache_key('state')
        cache.set(game_state_key, {
            'board': self.board_template.copy(),
            'current_turn': first_player,
            'players': players
        }, timeout=7200)
        
        print(f"[DEBUG] Game started. First player: {first_player}")
        
        for channel_name in players:
            await self.channel_layer.send(channel_name, {
                "type": "game_data",
                "data": {
                    "event": "game_start",
                    "board": self.board_template,
                    "myTurn": channel_name == first_player,
                    "symbol": "X" if channel_name == first_player else "O"
                }
            })

    async def receive_json(self, content, **kwargs):
        event = content.get("event")
        board = content.get("board", self.board_template)

        if event == "boardData_send":
            game_state_key = self.get_cache_key('state')
            game_state = cache.get(game_state_key)
            
            if game_state and game_state['current_turn'] != self.channel_name:
                await self.send_json({
                    "event": "error",
                    "message": "Chưa đến lượt của bạn!"
                })
                return

            winner = checkWin(board)
            if winner:
                await self.channel_layer.group_send(self.group_name, {
                    "type": "game_data",
                    "data": {
                        "event": "won",
                        "board": board,
                        "winner": winner,
                        "myTurn": False
                    }
                })
                return

            if isDraw(board):
                await self.channel_layer.group_send(self.group_name, {
                    "type": "game_data",
                    "data": {
                        "event": "draw",
                        "board": board,
                        "myTurn": False
                    }
                })
                return

            players_key = self.get_cache_key('players')
            players = cache.get(players_key, [])
            
            next_player = [p for p in players if p != self.channel_name][0] if len(players) == 2 else None
            
            if game_state and next_player:
                game_state['board'] = board
                game_state['current_turn'] = next_player
                cache.set(game_state_key, game_state, timeout=7200)
            
            for channel_name in players:
                await self.channel_layer.send(channel_name, {
                    "type": "game_data",
                    "data": {
                        "event": "boardData_send",
                        "board": board,
                        "myTurn": channel_name == next_player
                    }
                })

        elif event == "restart":
            players_key = self.get_cache_key('players')
            players = cache.get(players_key, [])
            
            if len(players) == 2:
                await self.start_game(players)

    async def disconnect(self, code):
        print(f"[DEBUG] Player disconnected: {self.channel_name}")
        
        players_key = self.get_cache_key('players')
        players = cache.get(players_key, [])
        
        if self.channel_name in players:
            players.remove(self.channel_name)
            print(f"[DEBUG] Removed player. Remaining: {len(players)}")
            
            if players:
                cache.set(players_key, players, timeout=7200)
            else:
                print(f"[DEBUG] Room empty, clearing cache")
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