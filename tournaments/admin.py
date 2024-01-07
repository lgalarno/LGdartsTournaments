from django.contrib import admin

from .models import Game, Participant, Tournament


class ParticipantInline(admin.TabularInline):
    model = Participant


class GameAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline]


# Register your models here.
admin.site.register(Game, GameAdmin)
admin.site.register(Participant)
admin.site.register(Tournament)
