from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Các field hiển thị khi edit user
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('description',)}),
    )

    # Các field hiển thị khi thêm user mới
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('description',)}),
    )

    # Cột hiển thị trong bảng danh sách user
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

    # Filter ở cột bên phải
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # Tìm kiếm theo các trường này
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Sắp xếp mặc định theo username
    ordering = ('username',)

# Đăng ký CustomUser vào admin
admin.site.register(CustomUser, CustomUserAdmin)