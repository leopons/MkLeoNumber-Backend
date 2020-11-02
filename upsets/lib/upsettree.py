from datetime import datetime
from upsets.models import Set, UpsetTreeNode
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

    def create_from_scratch(self):
        """Clean existing and create the upset tree from scratch
        """
        UpsetTreeNode.objects.all().delete()
        root = UpsetTreeNode(player_id=self._root_player_id, node_depth=0)
        root.save()

        cont = True
        current_depth = 0

        while cont:
            target_players = [
                x.player for x in
                UpsetTreeNode.objects.filter(node_depth=current_depth)]
            seen_players = [x.player for x in UpsetTreeNode.objects.all()]
            upsets = Set.objects.all() \
                                .exclude(winner__in=seen_players) \
                                .filter(looser__in=target_players) \
                                .order_by('winner_id',
                                          '-tournament__start_date') \
                                .distinct('winner_id')
            # .distinct('col_name') works only on postgres and select the
            # first row given the order_by placed before (see django doc)
            # Here, we keep the most recent upset of all the possible ones

            if upsets:
                current_depth += 1
                to_bulk_create = []
                for upset in upsets:
                    elt = UpsetTreeNode(
                        player=upset.winner,
                        parent=upset.looser.upsettreenode,
                        upset=upset,
                        node_depth=current_depth)
                    to_bulk_create.append(elt)
                UpsetTreeNode.objects.bulk_create(to_bulk_create)
            else:
                cont = False

            # pistes d'ameliorations :
            # prefect related upset tree node
            # seen player and target players store differently
