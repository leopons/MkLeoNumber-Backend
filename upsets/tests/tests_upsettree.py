from datetime import datetime
from django.test import TestCase
from upsets.models import Player, Tournament, Set, UpsetTreeNode, TreeContainer
from upsets.lib.upsettree import UpsetTreeManager


class UpsetTree_GeneralTestCase(TestCase):
    def setUp(self):
        Player.objects.bulk_create([
            Player(id='1', tag='player1'),
            Player(id='2', tag='player2'),
            Player(id='3', tag='bestplayer'),
            Player(id='4', tag='player4'),
            Player(id='5', tag='player5'),
            Player(id='6', tag='player6')
        ])
        Tournament.objects.bulk_create([
            Tournament(
                id='1',
                start_date=datetime.strptime('01/01/20', '%d/%m/%y').date(),
                name='recent-tournament'),
            Tournament(
                id='2',
                start_date=datetime.strptime('01/01/19', '%d/%m/%y').date(),
                name='old-tournament')
        ])
        sets_to_bulk_create = [
            # The best player lose once to 2 (2019) and twice to 1 (2019, 2020)
            Set(tournament_id='2', winner_id='1', loser_id='3'),
            Set(tournament_id='2', winner_id='2', loser_id='3'),
            Set(tournament_id='2', winner_id='3', loser_id='4'),
            Set(tournament_id='2', winner_id='3', loser_id='5'),
            Set(tournament_id='1', winner_id='1', loser_id='3'),
            Set(tournament_id='1', winner_id='3', loser_id='2'),
            Set(tournament_id='1', winner_id='3', loser_id='4'),
            Set(tournament_id='1', winner_id='3', loser_id='5'),
            # Player 4 beat player 1 (2020) and 2 (2019)
            Set(tournament_id='2', winner_id='1', loser_id='4'),
            Set(tournament_id='2', winner_id='4', loser_id='2'),
            Set(tournament_id='2', winner_id='5', loser_id='4'),
            Set(tournament_id='1', winner_id='4', loser_id='1'),
            Set(tournament_id='1', winner_id='2', loser_id='4'),
            Set(tournament_id='1', winner_id='5', loser_id='4'),
            # Player 5 beat player 2 once (2020)
            Set(tournament_id='2', winner_id='1', loser_id='5'),
            Set(tournament_id='2', winner_id='2', loser_id='5'),
            Set(tournament_id='1', winner_id='1', loser_id='5'),
            Set(tournament_id='1', winner_id='5', loser_id='2'),
            # Player 6 never won
            Set(tournament_id='1', winner_id='1', loser_id='6'),
            Set(tournament_id='1', winner_id='2', loser_id='6'),
            Set(tournament_id='1', winner_id='3', loser_id='6')
        ]
        id = 1
        for set in sets_to_bulk_create:
            set.id = str(id)
            id += 1
        Set.objects.bulk_create(sets_to_bulk_create)
        batch_update = TreeContainer.objects.create()
        self.manager = UpsetTreeManager('3', batch_update)

    def test_create_from_scratch(self):
        self.manager.create_from_scratch()
        nodes = UpsetTreeNode.objects.all()
        # 5 nodes (player 6 never won)
        self.assertEqual(nodes.count(), 5)
        # player 3 is root
        node3 = nodes.get(player_id='3')
        self.assertIsNone(node3.upset)
        self.assertIsNone(node3.parent)
        self.assertEqual(node3.node_depth, 0)
        # player 1 and 2 are level 1
        node1 = nodes.get(player_id='1')
        node2 = nodes.get(player_id='2')
        self.assertEqual(node1.parent, node3)
        self.assertEqual(node2.parent, node3)
        self.assertEqual(node1.node_depth, 1)
        self.assertEqual(node2.node_depth, 1)
        # player 2 upseted on 2019 and most recent upset for 1 is 2020
        self.assertEqual(node1.upset.tournament_id, '1')
        self.assertEqual(node2.upset.tournament_id, '2')
        # player 4 and 5 are level 2
        node4 = nodes.get(player_id='4')
        node5 = nodes.get(player_id='5')
        self.assertEqual(node4.node_depth, 2)
        self.assertEqual(node5.node_depth, 2)
        # player 4 most recent upset is against player 1 in 2020
        self.assertEqual(node4.parent, node1)
        self.assertEqual(node4.upset.tournament_id, '1')
        # player 5 most recent upset is against player 2 in 2020
        self.assertEqual(node5.parent, node2)
        self.assertEqual(node5.upset.tournament_id, '1')
