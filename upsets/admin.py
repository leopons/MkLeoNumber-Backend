from django.contrib import admin
from upsets.models import Player, TwitterTag


class TwitterTagAdmin(admin.StackedInline):
    model = TwitterTag


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    inlines = [TwitterTagAdmin]
