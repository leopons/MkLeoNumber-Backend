from django.db import models
from main.settings import TWITTER_BEARER_TOKEN
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
import requests
from datetime import datetime
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

    class Meta:
        indexes = [
            models.Index(fields=['tag', '-played_sets_count']),
        ]

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

    def update_last_tournament(self):
        '''
        This will be called on players with prefetched wins and loses, that's
        why we proceed with these to make our calculation instead of directly
        using a Tournament query like below. The Tournament query would indeed
        perform a useless extra call to the DB. (even thougt it might have been
        better if the wins and loses weren't prefetech already)

        tournament = Tournament.objects \
            .filter(Q(sets__winner=self) | Q(sets__loser=self)) \
            .order_by('-start_date') \
            .first()
        '''
        tournaments = \
            [set.tournament for set in self.wins.all()] + \
            [set.tournament for set in self.loses.all()]
        if tournaments:
            self.last_tournament = max(tournaments, key=lambda k: k.start_date)

    def update_played_sets_count(self):
        '''
        This is useful to order the results of the player search. We do not
        compute it on the fly for each call because that would drastically
        increase DB workload

        This will be called on players with prefetched wins and loses, that's
        why we proceed with these to make our calculation instead of directly
        using a Set query like below. The Set query would indeed perform a
        useless extra call to the DB. (even thougt it might have been
        better if the wins and loses weren't prefetech already)

        self.played_sets_count = Set.objects \
            .filter(Q(winner=self) | Q(loser=self)) \
            .count()
        '''
        count = len(self.wins.all()) + len(self.loses.all())
        self.played_sets_count = count


class TwitterTag(models.Model):
    '''
    We keep track of all the twitter tags given by the sqlite db file.
    '''
    tag = models.CharField(max_length=1000)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    obsolete = models.BooleanField(default=False)
    date_last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('tag', 'player',)
        indexes = [
            models.Index(fields=['player']),
        ]

    def is_valid(self):
        if self.obsolete:
            return False
        if self.date_last_checked:
            secs = (datetime.now() -
                    self.date_last_checked.replace(tzinfo=None)) \
                .total_seconds()
            # If already has been checked the last 24h
            if secs < (60 * 60 * 24):
                return True
        # default case
        return self.check_validity()

    def check_validity(self):
        # Make an API call to twitter to check the existence of the account
        twitter_search = \
                'https://api.twitter.com/1.1/users/show.json?screen_name='
        headers = {'authorization': 'Bearer '+TWITTER_BEARER_TOKEN}
        r = requests.get(twitter_search+self.tag, headers=headers)
        if r.ok:
            # If the account exists, we return True and store the date, as we
            # want to remember that for a day only.
            self.date_last_checked = datetime.now()
            self.save()
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


class BatchUpdate(models.Model):
    '''
    We can't make iterative updates for the Sets (no pk available) and the
    Upset Tree Nodes (change the structure of the tree, doable but more
    complex, maybe later) so we use this intermediate model to create all the
    new objects separately while conserving the old ones to avoid downtime
    '''
    update_date = models.DateTimeField(auto_now_add=True)
    ready = models.BooleanField(default=False)


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
    # batch update intermediate model
    batch_update = models.ForeignKey(BatchUpdate, on_delete=models.CASCADE)


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
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    # Sets and TreeNodes will be deleted all together by deleting the
    # associated BatchUpdate object. We use DO_NOTHING to avoid a deluge of
    # useless DB request performing the successive cascade operations
    parent = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING, null=True, blank=True)
    upset = models.ForeignKey(
        Set, on_delete=models.DO_NOTHING, null=True, blank=True)
    node_depth = models.IntegerField()
    # batch update intermediate model
    batch_update = models.ForeignKey(BatchUpdate, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'batch_update',)
        indexes = [
            models.Index(fields=['batch_update', 'player']),
        ]

    def get_root_path(self):
        logger.info(self)
        if self.parent is None:
            # We do not return the last node as it is empty and useless
            return []
        else:
            return [self] + self.parent.get_root_path()
