from django.shortcuts import redirect, render, HttpResponse
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from game.models import *
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import F, ExpressionWrapper, IntegerField

from .tictactoe import TicTacToe
from .tictactoe9 import TicTacToe9
from .tictactoe15 import TicTacToe15
from .humanvshuman import HvsH

User = get_user_model()

active_games = {}

@login_required
def menu(request):
    return render(request, "game/menu.html")

@login_required
def game_page(request, size):
    if size == 3:
        return render(request, "game/index.html")
    elif size == 9:
        return render(request, "game/gomoku.html")
    elif size == 15:
        return render(request, "game/gomoku15.html")
    elif size == 0:
        return render(request, "game/gomoku_H.html")
    else:
        return JsonResponse({'error': 'Invalid board size'}, status=400)

@csrf_exempt
def new_game(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    difficulty = data.get('difficulty', 'medium')
    size = data.get('size', 3)

    if size == 3:
        game = TicTacToe(difficulty)
    elif size == 9:
        game = TicTacToe9(difficulty)
    elif size == 15:
        game = TicTacToe15(difficulty)
    elif size == 0:
        game = HvsH()
    else:
        return JsonResponse({'error': 'Invalid game size'}, status=400)

    active_games[size] = game

    return JsonResponse({'board': game.board})


def make_move(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body.decode("utf-8"))

    row = data.get('row')
    col = data.get('col')
    size = data.get('size', 3)

    game = active_games.get(size)
    if not game:
        return JsonResponse({'error': 'Game not found for this size'}, status=400)

    if game.make_move(row, col):
        # Check player win
        if game.winner:
            return JsonResponse({
                'board': game.board,
                'winner': game.winner,
                'game_over': True
            })

        # Check tie
        if game.game_over:
            return JsonResponse({
                'board': game.board,
                'game_over': True,
                'tie': True
            })

        # AI move
        ai_row, ai_col = game.get_best_move()
        game.make_move(ai_row, ai_col)

        return JsonResponse({
            'board': game.board,
            'ai_move': {'row': ai_row, 'col': ai_col},
            'winner': game.winner,
            'game_over': game.game_over,
            'tie': game.game_over and not game.winner
        })

    return JsonResponse({'error': 'Invalid move'}, status=400)


def make_move_hvsh(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    row = data.get('row')
    col = data.get('col')

    # Human vs Human game is size 15
    game = active_games.get(9)
    if not game:
        return JsonResponse({'error': 'Game not found'}, status=400)

    if game.make_move(row, col):
        response = {
            'board': game.board,
            'game_over': game.game_over,
            'winner': game.winner
        }
        if game.game_over and not game.winner:
            response['tie'] = True
        return JsonResponse(response)

    return JsonResponse({'error': 'Invalid move'}, status=400)

@csrf_exempt
def create_room(request):
    if request.method == 'GET':
        return render(request, "game/create_room.html")
    
    elif request.method == 'POST':
        room_code = request.POST.get('room_code', '').strip().upper()
        player_name = request.POST.get('player_name', 'Unknown').strip()

        # Validate code
        if room_code:
            if len(room_code) != 6 or not room_code.isalnum():
                messages.error(request, "Mã phòng phải gồm 6 ký tự chữ hoặc số!")
                return redirect("create_room")

            room, created = Room.objects.get_or_create(code=room_code)
            # created = True nếu vừa tạo mới
            return redirect(f'/game/{room.code}/{player_name}/')

        else:
            # Tự generate
            room = Room.objects.create()
            return redirect(f"/game/{room.code}/{player_name}/")

def play_onl_game(request, room_code, name):
    try:
        room = Room.objects.get(code = room_code.upper())
        return render(request, 'game/play_onl_game.html',{'room': room, 'name': name})
    except Room.DoesNotExist:
        messages.error(request, "Có lỗi rồi !! Phòng này không tồn tại.")
        return redirect("create_room")
    
def leaderboard_view(request):
    users = (
        User.objects.annotate(
            score=ExpressionWrapper(
                F('wins') * 3 + F('draws'),
                output_field=IntegerField()
            ),
            games_played=F('wins') + F('losses') + F('draws')
        )
        .order_by('-score', '-wins')  
    )

    return render(request, "game/leaderboard.html", {"users": users})