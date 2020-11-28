from upsets.models import Set, UpsetTreeNode
from utils.decorators import time_it
from django.db.models import Q
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class UpsetTreeManager:
    """A manager to create and update the upset tree

    Given a target player, say MKLeo, we want to create a tree structure to get
    easily the shortest upset path for any player, to the target player.
    The root node represents MKLeo, the first level of child nodes the players
    who have beaten him, the second level the ones that have beaten the first
    level players, etc.
    This structure won't allow to determine the path between any couple of
    players, but in the case of a fixed target player it makes the processing
    simpler but mainly faster, for quick enduser results.

    Attributes
    ----------
    _root_player_id: str
        The id of the player to use as the target player

    Methods
    -------
    create_from_scratch()
        Clean existing and create the upset tree from scratch
    """

    def __init__(self, root_player_id):
        self._root_player_id = root_player_id

    @time_it(logger)
    def create_from_scratch(self):
        """Clean existing and create the upset tree from scratch
        """
        UpsetTreeNode.objects.all().delete()
        root = UpsetTreeNode(player_id=self._root_player_id, node_depth=0)
        root.save()

        cont = True
        current_depth = 0
        target_players_ids = [self._root_player_id]
        seen_players_ids = [self._root_player_id]

        while cont:
            logger.info(
                'Processing Upset Tree layer #%s...' % (current_depth+1))
            upsets = Set.objects \
                .all() \
                .exclude(winner_id__in=seen_players_ids) \
                .filter(loser_id__in=target_players_ids) \
                .exclude(Q(winner_score=-1) | Q(loser_score=-1)) \
                .order_by('winner_id', '-tournament__start_date') \
                .distinct('winner_id') \
                .select_related('loser__upsettreenode')
            # .distinct('col_name') works only on postgres and select the
            # first row given the order_by placed before (see django doc)
            # Here, we keep the most recent upset of all the possible ones.
            # .select_related to pretetch the upset nodes needed later

            if upsets:
                current_depth += 1
                to_bulk_create = []
                players_ids = []
                for upset in upsets:
                    elt = UpsetTreeNode(
                        # directly use winner_id to avoid fetching the player
                        # object related to the upset
                        player_id=upset.winner_id,
                        # We prefetched the upsettreenode of the loser
                        parent=upset.loser.upsettreenode,
                        upset=upset,
                        node_depth=current_depth)
                    to_bulk_create.append(elt)
                    players_ids.append(upset.winner_id)

                seen_players_ids += players_ids
                target_players_ids = players_ids
                UpsetTreeNode.objects.bulk_create(to_bulk_create)
                logger.info(
                    'Processed %s Players in layer #%s'
                    % (len(to_bulk_create), current_depth))
            else:
                cont = False
                logger.info(
                    'No players in layer #%s, the tree is now completed.'
                    % current_depth)