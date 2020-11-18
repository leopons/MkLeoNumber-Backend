from django.db import models
from main.settings import TWITTER_BEARER_TOKEN
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
import requests
# LOGGING
import logging
logger = logging.getLogger('data_processing')


# Needed for django ArrayField defaults
def empty_array():
    return []


class Tournament(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    start_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=1000)

    class Meta:
        indexes = [
            models.Index(fields=['-start_date']),
        ]


class Player(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    tag = models.CharField(max_length=1000)
    main_character = models.CharField(max_length=100, null=True, blank=True)
    last_tournament = models.ForeignKey(
        Tournament, on_delete=models.SET_NULL, null=True, blank=True)
    played_sets_count = models.IntegerField(default=0)

    def update_main_character(self):
        character_counts = {}
        for set in self.wins.all():
            for char in set.winner_characters:
                character_counts[char] = 1 if char not in character_counts \
                    else character_counts[char]+1
        for set in self.loses.all():
            for char in set.loser_characters:
                character_counts[char] = 1 if char not in character_counts \
                    else character_counts[char]+1
        if character_counts:
            self.main_character = max(
                character_counts, key=character_counts.get)
            self.save()

    def update_last_tournament(self):
        tournament = Tournament.objects \
            .filter(Q(sets__winner=self) | Q(sets__loser=self)) \
            .order_by('-start_date') \
            .first()
        if tournament:
            self.last_tournament = tournament
            self.save()

    # This is useful to order the results of the player search. We do not
    # compute it on the fly for each call because that would drastically
    # increase DB workload
    def update_played_sets_count(self):
        self.played_sets_count = Set.objects \
            .filter(Q(winner=self) | Q(loser=self)) \
            .count()
        self.save()


class TwitterTag(models.Model):
    '''
    We keep track of all the twitter tags given by the sqlite db file.
    '''
    tag = models.CharField(max_length=1000)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    obsolete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tag', 'player',)

    def check_validity(self):
        # Make an API call to twitter to check the existence of the account
        twitter_search = \
                'https://api.twitter.com/1.1/users/show.json?screen_name='
        headers = {'authorization': 'Bearer '+TWITTER_BEARER_TOKEN}
        r = requests.get(twitter_search+self.tag, headers=headers)
        if r.ok:
            # If the account exists, we return True but do not store anything
            # as we DO want to check again the next times
            return True
        elif r.status_code == 404:
            # If the account does not exists we mark the tag as obsolete to
            # save some time in the future and do not check again
            self.obsolete = True
            self.save()
            return False
        else:
            # If we got an error which isn't a 404, we do not mark the tag
            # as obsolete as this may be a temporary error
            return False


class Set(models.Model):
    original_id = models.CharField(max_length=1000)
    # (not primary key cause there's duplicates in the player database export)
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name='sets')
    winner = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='wins')
    winner_characters = ArrayField(
        models.CharField(max_length=100), default=empty_array)
    loser = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='loses')
    loser_characters = ArrayField(
        models.CharField(max_length=100), default=empty_array)
    winner_score = models.IntegerField(null=True, blank=True)
    loser_score = models.IntegerField(null=True, blank=True)
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
            return [self] + self.parent.get_root_path()
