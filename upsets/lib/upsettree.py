from upsets.models import Set, UpsetTreeNode, TreeContainer
from utils.decorators import time_it
from django.db.models import Q, Prefetch
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
        Create the upset tree from scratch for the given tree_container
    update_tree()
        Update the upset tree using a container to assure zero downtime
    update_all_trees()
        Update both online and offline upset trees
    """

    def __init__(self, root_player_id):
        self._root_player_id = root_player_id

    @time_it(logger)
    def create_from_scratch(self, tree_container):
        """Create the upset tree from scratch for the given tree_container
        """
        root = UpsetTreeNode(
            player_id=self._root_player_id,
            node_depth=0,
            tree_container=tree_container)
        root.save()

        cont = True
        current_depth = 0
        target_players_ids = [self._root_player_id]
        seen_players_ids = [self._root_player_id]

        sets = Set.objects.all()
        if tree_container.offline_only:
            sets = sets.exclude(tournament__online=True)

        while cont:
            logger.info(
                'Processing Upset Tree layer #%s...' % (current_depth+1))
            upsets = sets \
                .exclude(winner_id__in=seen_players_ids) \
                .filter(loser_id__in=target_players_ids) \
                .exclude(Q(winner_score=-1) | Q(loser_score=-1)) \
                .exclude(Q(winner_score=0) & Q(loser_score=0)) \
                .order_by('winner_id', '-tournament__start_date') \
                .distinct('winner_id') \
                .prefetch_related(Prefetch(
                    'loser__upsettreenode_set',
                    queryset=UpsetTreeNode.objects.filter(
                        tree_container_id=tree_container.id),
                    to_attr='matching_nodes'))
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
                        parent=upset.loser.matching_nodes[0],
                        upset=upset,
                        node_depth=current_depth,
                        tree_container=tree_container)
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

    def update_tree(self, offline_only=False):
        """Update the upset tree using a container to assure zero downtime
        """
        str_type = "Offline" if offline_only else "Online"
        logger.info("Building new %s Upset Tree." % str_type)

        container = TreeContainer.objects.create(offline_only=offline_only)
        self.create_from_scratch(container)
        # When all the data is built, switch the container to ready and
        # delete the past container (the cascade will delete the related
        # update tree nodes)
        container.ready = True
        container.save()
        logger.info("The new Tree data is ready, deleting the old data...")
        TreeContainer.objects.filter(offline_only=offline_only) \
                             .exclude(id=container.id) \
                             .delete()
        logger.info("Successfully deleted old %s Tree data." % str_type)

    def update_all_trees(self):
        """Update both online and offline upset trees
        """
        self.update_tree(offline_only=False)
        self.update_tree(offline_only=True)
