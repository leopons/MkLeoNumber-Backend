from django.db import models


class Player(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    tag = models.CharField(max_length=1000)


class Tournament(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    start_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=1000)


class Set(models.Model):
    original_id = models.CharField(max_length=1000)
    # (not primary key cause there's duplicates in the player database export)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='winner')
    looser = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='looser')
    winner_score = models.IntegerField(null=True, blank=True)
    looser_score = models.IntegerField(null=True, blank=True)
    round_name = models.CharField(max_length=1000, null=True, blank=True)
    best_of = models.IntegerField(null=True, blank=True)
