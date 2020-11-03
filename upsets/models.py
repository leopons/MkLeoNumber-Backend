from django.db import models
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class Player(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    tag = models.CharField(max_length=1000)


class Tournament(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    start_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=1000)

    class Meta:
        indexes = [
            models.Index(fields=['-start_date']),
        ]


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


class UpsetTreeNode(models.Model):
    '''
    Given a target player, say MKLeo, we want to create a tree structure to get
    easily the shortest upset path for any player, to the target player.
    The root node represents MKLeo, the first level of child nodes the players
    who have beaten him, the second level the ones that have beaten the first
    level players, etc.
    This structure won't allow to determine the path between any couple of
    players, but in the case of a fixed target player it makes the processing
    simpler but mainly faster, for quick enduser results.
    '''
    player = models.OneToOneField(
        Player, on_delete=models.CASCADE, primary_key=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    upset = models.ForeignKey(
        Set, on_delete=models.CASCADE, null=True, blank=True)
    node_depth = models.IntegerField()

    def get_root_path(self):
        logger.info(self)
        if self.parent is None:
            return [self]
        else:
            return self.parent.get_root_path() + [self]

    def __str__(self):
        if self.upset is None:
            return 'ROOT'
        else:
            return ("%s %s - %s %s @ %s %s - %s" % (
                self.upset.winner.tag,
                self.upset.winner_score,
                self.upset.looser_score,
                self.upset.looser.tag,
                self.upset.tournament.name,
                self.upset.round_name,
                self.upset.tournament.start_date
            ))
