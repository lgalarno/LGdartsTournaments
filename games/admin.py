from django.contrib import admin

from .models import GameType, Tournament, Game, Participant


class ParticipantInline(admin.TabularInline):
    model = Participant


class GameAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline]


# Register your models here.
admin.site.register(GameType)
admin.site.register(Tournament)
admin.site.register(Game, GameAdmin)
admin.site.register(Participant)
