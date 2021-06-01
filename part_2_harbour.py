"""
Build main components for harbour management and ships movements tracking.
Connect with Preligens (fake) Db and REST API.

Classes:
    Api: connect to Preligens API, get credentials and ships positions
    Berth: create Berth object
    Db: connect to Preligens database, select and insert data
    Harbour: create Harbour object
    Movements: create Movements object to track ships positions
    Pier: create Pier object
    Ship: create Ship object
"""
from datetime import datetime, timedelta
import requests
import pandas as pd
import mysql.connector


class Api:
    """
    Connector with Preligens (fake) API
    """
    def __init__(self, user, password):
        self.username = user
        self.password = password
        self.api_key = None


    def _extract_response_values(self, response):
        """
        Extract response values

        Args:
            response: api response

        Returns:
            Response (str) or None in case of error
        """
        status = self._interpret_status_code(response)

        if status == 'OK':
            response = response.text
        else:
            response = None

        return response


    def _get_api_key(self, response):
        """
        Retrieve API key

        Args:
            response: api response
        """
        response_values = self._extract_response_values(response)
        if response_values:
            try:
                self.api_key = response_values['APIkey']
            except:
                raise ValueError


    def _get_ships_positions(self, response):
        """
        Retrieve ships positions

        Args:
            response: api response

        Returns:
            DataFrame of ships positions
        """
        response_values = self._extract_response_values(response)
        if response_values:
            try:
                ships_pos = response_values['ship_positions']
                ships_pos = pd.DataFrame(ships_pos)
                return ships_pos
            except:
                raise ValueError


    @staticmethod
    def _interpret_status_code(response, verbose=False):
        """ Interpret Preligens API status code """
        if response.status_code == 200:
            status = 'OK'
        elif response.status_code == 400:
            status = 'Incorrect request'
        elif response.status_code == 401:
            status = 'Unkown credentials'
        else:
            status = 'Unknown error'

        if verbose:
            print(status)
        return status


    def get_api_key(self):
        """ Retrieve API key from Preligens API """

        URL = "https://preligens.com/marineapi/vfake/auth/getAPIkey"
        payload = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(URL, params=payload)
        self._get_api_key(response)


    def get_ships_positions(self, port_id, start_time, end_time=None):
        """
        Retrieve ships positions from Preligens API

        Args:
            port_id (str): id of the port
            start_time (datetime): request start time
            end_time (datetime): request end time
        """
        if not end_time:
            end_time = datetime.now()

        URL = "https://preligens.com/marineapi/vfake/auth/getShipPositions"
        headers = {'API Key': self.api_key}
        payload = {
            "port_ID": port_id,
            "Start time": start_time,
            "End time": end_time,
        }
        response = requests.get(URL, headers=headers, params=payload)
        ships_pos = self._get_ships_positions(response)
        return ships_pos



class Berth:
    """
    Berth object with its properties and availability
    """
    def __init__(self, length, equipements={}, is_empty=None):
        self.length = length
        self.equipements = equipements
        self.is_empty = is_empty



class Db:
    """
    Connector with Preligens (fake) database

    Args:
        user: database user name
        password: database user password
        db_name: database to connect to
        host: name of server hosting the database
    """
    def __init__(self, user, password, db_name='HarbourDB', host='localhost'):
        self._cur = None
        self._db = None
        self.db_name = db_name
        self.host = host
        self.pssd = password
        self.user = user


    def _build_query(self, table, data, insert=True):
        """
        Build sql query by incorporating data in a formatted string
        (only option implemented)

        Args:
            data (dict): data to insert in a dict format, e.g.:
            {
                'lat': 3.1415,
                'lon': 8.325,
                'timestamp': '2019-06-17T14:30:00Z',
                'ship_id': 95125
            }
            table (str): name of table to query
            insert (bool): type of query to build
        """
        assert insert is True

        # Extract fields names
        fields = list(data.columns)
        pre_vals = ["%(" + field + ")s" for field in data.columns]

        # Build query
        query = f"INSERT INTO {table}(" + ", ".join(fields) + ") "
        query += "VALUES (" + ", ".join(pre_vals) + ")"
        return query


    def _connect(self):
        """
        Initiate connection to Preligens database

        Note: make this a public function to enable open connection throughout
        multiple transactions
        """
        con_phrase = f'host="{self.host}", \
                       user="{self.user}", \
                       password="{self.pssd}", \
                       database="{self.db_name}"'

        self._db = mysql.connector.connect(con_phrase)


    def _disconnect(self):
        """
        Kill connection with db

        Note: make this a public function to enable open connection throughout
        multiple transactions
        """
        try:
            del self._cur
            del self._db
            self._cur = None
            self._db = None
        except:
            self._cur = None
            self._db = None


    def get_data(self, table=None, query=None, limit=100):
        """
        Retrieve data from Preligens REST API

        Args:
            query (str): sql query
            table (str): table to query
            limit (int): sql limit query selection

        Note:
            If get_data is called frequently, keep the connection opened,
            otherwise, reopen a new connection for each call.
        """
        self._connect()

        # Build query
        if not query:
            query = f"SELECT * FROM {table} LIMIT {limit}"

        # Retrieve data from db
        self._cur = self._db.cursor()
        self._cur.execute(query)
        result = self._cur.fetchall()

        self._disconnect()
        return result


    def push_data(self, table, data):
        """
        Insert data into Preligens Database using its REST API

        Args:
            data (dict): data to insert into Preligens db. Should contain one
                         row only (implement DataFrames for multiple inserts)
            table (str): table to insert data into

        Note:
            Could be simplified using SQLAlchemy
            Could be simplified using a decorator for connection start & stop
        """
        self._connect()

        # Build query
        query = self._build_query(table, data, insert=True)
        records = data.values.tolist()

        # Execute insert query
        self._cur = self._db.cursor()
        self._cur.executemany(query, records)
        self._db.commit()

        self._disconnect()



class Harbour:
    """
    Class defining the harbour

    Can have 0 or multiple initial piers.
    """
    def __init__(self, piers=[]):
        self.piers = piers



class Movements:
    """
    Keep track of ships movements and share data with the
    Preligens REST API
    """
    def __init__(self):
        self.movements = []



class Pier:
    """
    Pier object with its berths
    """
    def __init__(self, berths=[]):
        self.berths = berths



class Ship:
    """
    Ship object with standard properties
    """
    def __init__(self, name, ship_id, ship_type, length):
        self.name = name
        self.id = ship_id
        self.type = ship_type
        self.length = length




if __name__ == "__main__":
    # Get ships positions from API
    api = Api(user="alexis", password="pssd_test_api")
    api.get_api_key()
    ships_positions = api.get_ships_positions(port_id='port_1',
                                              start_time=timedelta(weeks=-2))

    # Push to Database
    TABLE = 'ship-positions-table-to-be-populated-in-exercice'
    db = Db(user="alexis", password="pssd_test_db")
    db.push_data(TABLE, ships_positions)
