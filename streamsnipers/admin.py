from django.contrib import admin

from .models import Games, StreamSniper, Score


# Register your models here.
admin.site.register(Games)
admin.site.register(StreamSniper)
admin.site.register(Score)
