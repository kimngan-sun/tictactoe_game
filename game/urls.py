from django.urls import path
from game import views

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('game/<int:size>/', views.game_page, name='game_page'),
    path('new_game/', views.new_game, name='new_game'),
    path('make_move/', views.make_move, name='make_move'),
    path('make_move_hvsh/', views.make_move_hvsh, name='make_move_hvsh'),
    path('create_room/',views.create_room, name='create_room'),
    path('game/<str:room_code>/<str:name>/',views.play_onl_game, name='play_onl_game'),
    path("leaderboard/", views.leaderboard_view, name="leaderboard")
]