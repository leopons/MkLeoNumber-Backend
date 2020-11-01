from django.db import models


class Player(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    tag = models.CharField(max_length=1000)


class Tournament(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    start_date = models.DateField()
    name = models.CharField(max_length=1000)


class Set(models.Model):
    id = models.BigIntegerField(primary_key=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='winner')
    looser = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='looser')
    winner_score = models.IntegerField()
    looser_score = models.IntegerField()
    round_name = models.CharField(max_length=1000)
    best_of = models.IntegerField(null=True, blank=True)
