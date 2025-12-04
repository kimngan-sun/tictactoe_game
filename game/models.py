import uuid
from django.db import models
from django.conf import settings

def generate_room_code():
    return uuid.uuid4().hex[:6].upper()

class Room(models.Model):
    code = models.CharField(max_length=20, unique=True, default=generate_room_code)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('waiting','Waiting'), ('playing','Playing'), ('finished','Finished')],
        default='waiting'
    )
    player_x = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rooms_as_x',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    player_o = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rooms_as_o',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.code

class GameRecord(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='records')
    result = models.CharField(max_length=10)  # 'X', 'O', 'draw'
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room.code} - Result: {self.result}"

