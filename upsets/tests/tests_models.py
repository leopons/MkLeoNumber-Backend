from datetime import datetime
from django.test import TestCase
from upsets.models import Player, Tournament, Set


class Models_GeneralTestCase(TestCase):
    def setUp(self):
        Player.objects.bulk_create([
            Player(id='1', tag='player1'),
            Player(id='2', tag='player2'),
            Player(id='3', tag='player3'),
            Player(id='4', tag='player4'),
            Player(id='5', tag='player5'),
        ])
        Tournament.objects.bulk_create([
            Tournament(
                id='1',
                start_date=datetime.strptime('01/01/20', '%d/%m/%y').date(),
                name='recent-tournament',
                online=False),
            Tournament(
                id='2',
                start_date=datetime.strptime('01/01/19', '%d/%m/%y').date(),
                name='old-tournament',
                online=False)
        ])
        sets_to_bulk_create = [
            # players 2 & 3 haven't played in most recent tournament
            # player 1 mains joker, 4 mains mario, 5 we don't know
            Set(id='1', tournament_id='1', winner_id='1', loser_id='4',
                winner_characters=['joker'],
                loser_characters=['mario', 'bowser']),
            Set(id='2', tournament_id='1', winner_id='4', loser_id='5',
                winner_characters=['mario'],
                loser_characters=[]),
            Set(id='3', tournament_id='1', winner_id='1', loser_id='5',
                winner_characters=['luigi'],
                loser_characters=[]),
            # player 3 & 4 haven't played in older tournament
            # player 2 mains peach
            Set(id='4', tournament_id='2', winner_id='2', loser_id='1',
                winner_characters=['mario', 'peach'],
                loser_characters=['joker']),
            Set(id='5', tournament_id='2', winner_id='5', loser_id='2',
                winner_characters=[],
                loser_characters=['peach']),
            Set(id='6', tournament_id='2', winner_id='5', loser_id='1',
                winner_characters=[],
                loser_characters=['joker']),
        ]
        Set.objects.bulk_create(sets_to_bulk_create)

    def test_update_main_character(self):
        for player in Player.objects.all():
            player.update_main_character()
            player.save()
        self.assertEqual(Player.objects.get(id='1').main_character, 'joker')
        self.assertEqual(Player.objects.get(id='2').main_character, 'peach')
        self.assertEqual(Player.objects.get(id='3').main_character, None)
        self.assertEqual(Player.objects.get(id='4').main_character, 'mario')
        self.assertEqual(Player.objects.get(id='5').main_character, None)

    def test_update_last_tournament(self):
        for player in Player.objects.all():
            player.update_last_tournament()
            player.save()
        self.assertEqual(Player.objects.get(id='1').last_tournament_id, '1')
        self.assertEqual(Player.objects.get(id='2').last_tournament_id, '2')
        self.assertEqual(Player.objects.get(id='3').last_tournament_id, None)
        self.assertEqual(Player.objects.get(id='4').last_tournament_id, '1')
        self.assertEqual(Player.objects.get(id='5').last_tournament_id, '1')

    def test_update_played_sets_count(self):
        for player in Player.objects.all():
            player.update_played_sets_count()
            player.save()
        self.assertEqual(Player.objects.get(id='1').played_sets_count, 4)
        self.assertEqual(Player.objects.get(id='2').played_sets_count, 2)
        self.assertEqual(Player.objects.get(id='3').played_sets_count, 0)
        self.assertEqual(Player.objects.get(id='4').played_sets_count, 2)
        self.assertEqual(Player.objects.get(id='5').played_sets_count, 4)
