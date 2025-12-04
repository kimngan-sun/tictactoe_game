from django.contrib import admin
from .models import Room, GameRecord
# Register your models here.
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'player_x', 'player_o', 'created_at')
    search_fields = ('code', 'player_x__username', 'player_o__username')
    list_filter = ('status', 'created_at')  # Lọc theo trạng thái và ngày tạo

@admin.register(GameRecord)
class GameRecordAdmin(admin.ModelAdmin):
    list_display = ('room', 'result', 'winner', 'duration_seconds', 'created_at')
    search_fields = ('room__code', 'winner__username')
    list_filter = ('result', 'created_at')  # Lọc theo kết quả và ngày tạo
