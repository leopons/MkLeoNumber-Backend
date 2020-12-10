from datetime import datetime
import ast
import sqlite3
from upsets.models import Tournament, Player, Set, TwitterTag, TreeContainer
from utils.orm_operators import BulkBatchManager
from upsets.lib.upsettree import UpsetTreeManager
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class SqliteArchiveReader:
    """A reader to import data from a PlayerDatabase sqlite export.

    This class provide an interface to import the data available
    in sqlite exports coming from The Player Satabase website
    https://github.com/smashdata/ThePlayerDatabase

    Attributes
    ----------
    _connection: sqlite3.Connection object
        The connection object used to fetch data from the db file

    Methods
    -------
    update_players()
        Query all rows in the player table and save them in our DB
    update_tournaments()
        Query all rows in the tournament_info table and save them in our DB
    create_sets()
        Query all rows in the sets table and save them in our DB
    batch_update_sets_tree ()
        Update all sets and tree nodes using the batch update method
    update_all_data()
        Query the db file and update all the data in our db
    """

    def __init__(self, db_file):
        # Setup connection object
        conn = sqlite3.connect(db_file)
        self._connection = conn

    def update_players(self):
        """Query all rows in the player table and save them in our DB
        """
        cur = self._connection.cursor()
        cur.execute("SELECT player_id, tag, social FROM players")
        rows = cur.fetchall()
        logger.info('Successfully fetched players data from db file, '
                    + 'handling players and twitter tags updates...')

        players_generator = (Player(id=row[0], tag=row[1]) for row in rows)
        batcher = BulkBatchManager(
            Player, ignore_conflicts=True, logger=logger)
        batcher.bulk_update_or_create(players_generator, ['tag'])
        logger.info('Successfully updated players from db file.')

        # Create new twitter tags on the go
        def twitter_tag_generator(data):
            for row in data:
                twitters = ast.literal_eval(row[2])['twitter']
                for twitter in twitters:
                    tag = TwitterTag(tag=twitter, player_id=row[0])
                    yield tag
        batcher = BulkBatchManager(
            TwitterTag, ignore_conflicts=True, logger=logger)
        batcher.bulk_create(twitter_tag_generator(rows))
        logger.info('Successfully added new twitter tags from db file.')

    def update_tournaments(self):
        """Query all rows in the tournament_info table and save them in our DB
        """
        cur = self._connection.cursor()
        cur.execute("SELECT key, cleaned_name, start FROM tournament_info")
        rows = cur.fetchall()
        logger.info('Successfully fetched tournament data from db file, '
                    + 'handling tournaments updates...')

        tournaments_generator = (Tournament(
            id=row[0],
            name=row[1],
            start_date=datetime.fromtimestamp(row[2]).date()
        ) for row in rows)

        batcher = BulkBatchManager(
            Tournament, ignore_conflicts=True, logger=logger)
        batcher.bulk_update_or_create(
            tournaments_generator, ['name', 'start_date'])
        logger.info('Successfully updated tournaments from db file.')

    def update_sets(self):
        """
        Query all rows in the sets table and save them in our DB
        """
        cur = self._connection.cursor()
        # The sets table presents some player id values that are not in the
        # player table. This cause some integrity errors in our bulk create
        # operations. To handle this we inner join the sets table with
        # the player table when requesting the sqlite file, which takes a
        # little more time but solves the integrity problem upstream
        cur.execute("""
            SELECT
                sets.key,
                sets.tournament_key,
                sets.winner_id,
                sets.p1_id,
                sets.p2_id,
                sets.p1_score,
                sets.p2_score,
                sets.location_names,
                sets.best_of,
                sets.game_data
            FROM sets
            INNER JOIN players as p1
            ON sets.p1_id = p1.player_id
            INNER JOIN players as p2
            ON sets.p2_id = p2.player_id
            WHERE key IS NOT NULL
                AND sets.tournament_key IS NOT NULL
                AND sets.winner_id IS NOT NULL
            """)

        rows = cur.fetchall()
        logger.info('Successfully fetched sets data from db file, '
                    + 'handling sets updates...')

        def sets_generator(data):
            for row in data:
                set = Set(id=row[0], tournament_id=row[1])
                if row[2] == row[3]:
                    # winner is player 1
                    set.winner_id = row[3]
                    set.loser_id = row[4]
                    set.winner_score = row[5]
                    set.loser_score = row[6]
                elif row[2] == row[4]:
                    # winner is player 2
                    set.winner_id = row[4]
                    set.loser_id = row[3]
                    set.winner_score = row[6]
                    set.loser_score = row[5]
                else:
                    logger.warning(
                        'winner_id does not match p1_id or p2_id on set %s'
                        % row[0])
                set.round_name = ast.literal_eval(row[7])[-1]
                set.best_of = row[8]
                set.winner_characters = []
                set.loser_characters = []
                try:
                    for gamedata in ast.literal_eval(row[9]):
                        (game_winner_char, game_loser_char) = (
                            (gamedata['winner_char'].replace('ultimate/', '')),
                            (gamedata['loser_char'].replace('ultimate/', '')))
                        if str(gamedata['winner_id']) == str(set.winner_id):
                            set_winner_char = game_winner_char
                            set_loser_char = game_loser_char
                        else:
                            set_winner_char = game_loser_char
                            set_loser_char = game_winner_char
                        if set_winner_char not in set.winner_characters:
                            set.winner_characters.append(set_winner_char)
                        if set_loser_char not in set.loser_characters:
                            set.loser_characters.append(set_loser_char)
                except ValueError as ex:
                    # Ignore the malformed values when doing literal_eval
                    logger.debug(ex)
                yield set

        batcher = BulkBatchManager(
            Set, ignore_conflicts=True, logger=logger)
        batcher.bulk_update_or_create(
            sets_generator(rows),
            ['tournament_id', 'winner_id', 'loser_id', 'winner_score',
             'loser_score', 'round_name', 'best_of', 'winner_characters',
             'loser_characters'])
        logger.info('Successfully updated sets from db file.')

    def batch_update_tree(self):
        batch_update = TreeContainer.objects.create()
        upset_tree_manager = UpsetTreeManager('222927', batch_update)
        upset_tree_manager.create_from_scratch()
        # When all the data is built, switch the batch update to ready and
        # delete the past batch update (the cascade will delete the related
        # sets and update tree nodes)
        batch_update.ready = True
        batch_update.save()
        logger.info(
            "The new Sets and Tree data is ready, deleting the old data...")
        TreeContainer.objects.exclude(id=batch_update.id).delete()
        logger.info("Successfully deleted old Sets and Tree data.")

    def update_all_data(self):
        """Query the db file and update all the data in our db
        """
        self.update_tournaments()
        self.update_players()
        self.update_sets()
        self.batch_update_tree()
