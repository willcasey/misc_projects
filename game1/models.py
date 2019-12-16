import sqlite3
import datetime
import pandas as pd

class Database:
    def __init__(self, log_table_name, game_id):
        self.conn = sqlite3.connect('game.db')
        self.game_id = game_id
        self.log_table_name = log_table_name
        self.create_unit_table()

    def save(self, query):
        self.conn.execute(query)
        self.conn.commit()

    def drop_game_log_table(self):
        query = "DROP TABLE IF EXISTS {};".format(self.log_table_name)
        self.save(query)

    def create_game_log_table(self):
        query = """
              CREATE TABLE IF NOT EXISTS "{}" (
              id INTEGER PRIMARY KEY,
              game_id INTEGER,
              action TEXT,
              details JSON,
              created Timstamp DEFAULT CURRENT_TIME);
               """.format(self.log_table_name)
        self.save(query)

    def append_game_log_table(self, **values):
        """
        values:
            action: the action that was done
                i.e. create_unit, create_nation, attack, etc
            details: a dictionary of the details of the action
                i.e. {"nation": "R", "name": "m1_100", ....}

        """
        timestamp = datetime.datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        INSERT INTO {log_table_name} (game_id, action, details, created)
        VALUES ('{game_id}', '{action}',"{details}", '{timestamp}');
        """.format(  log_table_name = self.log_table_name
                   , game_id = self.game_id
                   , action = values['action']
                   , details = values['details']
                   , timestamp = timestamp)
        self.save(query)

    def create_unit_table(self):
        drop_query = 'DROP TABLE IF EXISTS "units";'
        query = """
              CREATE TABLE IF NOT EXISTS "units" (
              id INTEGER PRIMARY KEY,
              game_id INTEGER,
              name TEXT,
              nation TEXT,
              unit_type TEXT,
              position  TEXT,
              status  INTEGER,
              base_mu INTEGER ,
              base_sigma  INTEGER,
              training TEXT,
              leadership TEXT,
              terrain TEXT,
              morale TEXT,
              experience TEXT,
              attacking TEXT,
              defending TEXT
              );
        """
        for q in [drop_query, query]:
            self.save(q)

    def append_unit_table(self, **values):
        query = """
        INSERT INTO "units"
        (game_id, name, nation, unit_type, position, status, base_mu, base_sigma, training, leadership, terrain, morale, experience, attacking, defending)
        VALUES ('{game_id}', '{name}', '{nation}', "{unit_type}","{position}", {status}, {base_mu}, {base_sigma}, '{training}', '{leadership}', '{terrain}', '{morale}', '{experience}', '{attacking}', '{defending}');
        """.format(  game_id = self.game_id
                    , name = values['name']
                    , nation = values['nation']
                    , position = values['position']
                    , unit_type = values['unit_type']
                    , status = values['status']
                    , base_mu = values['base_mu']
                    , base_sigma = values['base_sigma']
                    , training = values['training']
                    , leadership = values['leadership']
                    , terrain = values['terrain']
                    , morale = values['morale']
                    , experience = values['experience']
                    , attacking = values['attacking']
                    , defending = values['defending']

                    )
        self.save(query)
    def update_unit_table(self, unit_name, unit_nation, update_column, update_value):
        query = f'UPDATE "units"' \
                f'SET {update_column} = "{update_value}"' \
                f'WHERE name = "{unit_name}" and nation = "{unit_nation}"'
        self.save(query)

    def query(self, query, return_as_df=True):
        if return_as_df:
            return pd.read_sql_query(query, self.conn)





