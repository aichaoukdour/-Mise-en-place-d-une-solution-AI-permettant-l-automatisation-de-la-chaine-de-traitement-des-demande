
import psycopg2
from dotenv import dotenv_values

conf_file  = ".env"
from AutomatisationDemandesAnalytiquesApp.Db_handler.models import User ,EmailRecord,UserRole
class EmailDatabase:
    def __init__(self, config_file=conf_file):
        if config_file is None:
            config_file = config_file
        self.config = dotenv_values(config_file)
        self.conn = self._connect()

    def _connect(self):
        try:
            conn = psycopg2.connect(
                host=self.config["host"],
                database=self.config["db_name"],
                user=self.config["user"],
                password=self.config["Password"],
                port=self.config["port"]
            )
            print("Database connection successful.")
            return conn
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return None
