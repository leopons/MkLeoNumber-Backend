from datetime import datetime
import ast
import sqlite3
from upsets.models import Tournament, Player, Set


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
    update_sets()
        Query all rows in the sets table and save them in our DB
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
        cur.execute("SELECT player_id, tag FROM players")

        rows = cur.fetchall()
        for row in rows:
            try:
                player, created = Player.objects.get_or_create(id=row[0])
                player.tag = row[1]
                player.save()
                if created:
                    print('Successfully created new player with id %s'
                          % row[0])
                else:
                    print('Successfully updated existing player with id %s'
                          % row[0])
            except Exception as ex:
                print(ex)

    def update_tournaments(self):
        """Query all rows in the tournament_info table and save them in our DB
        """
        cur = self._connection.cursor()
        cur.execute("SELECT key, cleaned_name, start FROM tournament_info")

        rows = cur.fetchall()
        for row in rows:
            try:
                tournament, created = \
                    Tournament.objects.get_or_create(id=row[0])
                tournament.name = row[1]
                tournament.start_date = datetime.fromtimestamp(row[2]).date()
                tournament.save()
                if created:
                    print('Successfully created new tournament with id %s'
                          % row[0])
                else:
                    print('Successfully updated existing tournament with id %s'
                          % row[0])
            except Exception as ex:
                print(ex)

    def update_sets(self):
        """Query all rows in the sets table and save them in our DB
        """
        cur = self._connection.cursor()
        cur.execute("""
            SELECT
                key,
                tournament_key,
                winner_id,
                p1_id,
                p2_id,
                p1_score,
                p2_score,
                location_names,
                best_of
            FROM sets
            WHERE key IS NOT NULL
                AND tournament_key IS NOT NULL
                AND winner_id IS NOT NULL
                AND p1_id IS NOT NULL
                AND p2_id IS NOT NULL
            """)

        rows = cur.fetchall()

        # Temporary solution as there are key duplicates in the player database
        # export. We just remove all the sets and recreate them.

        Set.objects.all().delete()

        for row in rows:
            try:
                set = Set(original_id=row[0], tournament_id=row[1])
                if row[2] == row[3]:
                    # winner is player 1
                    set.winner_id = row[3]
                    set.looser_id = row[4]
                    set.winner_score = row[5]
                    set.looser_score = row[6]
                elif row[2] == row[4]:
                    # winner is player 2
                    set.winner_id = row[4]
                    set.looser_id = row[3]
                    set.winner_score = row[6]
                    set.looser_score = row[5]
                else:
                    raise Exception('winner_id does not match p1_id or p2_id')
                set.round_name = ast.literal_eval(row[7])[-1]
                set.best_of = row[8]
                set.save()
                print('Successfully created new set with id %s' % row[0])
            except Exception as ex:
                print(ex)

    def update_all_data(self):
        """Query the db file and update all the data in our db
        """
        self.update_tournaments()
        self.update_players()
        self.update_sets()
