from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url


class DatabaseConnection:

    def __init__(self, database_type, username, password, host, port, schemas=None):
        self.database_type = str(database_type).lower()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.schemas = schemas
        self.driver = None
        self.url_object = None
        self.connection = None
        self.connection_args = None

    def get_driver_name(self):
        if self.database_type == 'mysql':
            return 'mysql+pymysql'
        elif self.database_type == 'postgres':
            return 'postgresql+psycopg2'
        elif self.database_type == 'sqlserver':
            return 'mssql+pymssql'
        elif self.database_type == 'sqlite':
            return 'sqlite'
        elif self.database_type == 'mongodb':
            return 'mongodb'
        elif self.database_type == 'redshift':
            return 'redshift+redshift_connector'
        elif self.database_type == 'oracle':
            return 'oracle+oracledb'
        elif self.database_type == 'oracle11g':
            return 'oracle+cx_oracle'

    def get_conn_args(self):
        if self.database_type == 'redshift':
            return "{'sslmode': 'verify-ca'}"

    def get_url(self):
        driver = self.get_driver_name()
        if self.database_type == 'oracle':
            return f"{driver}://{self.username}:{self.password}@{self.host}:{self.port}/?service_name={self.schemas}" # noqa
        elif self.database_type == 'oracle11g':
            dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={self.host})(PORT={self.port}))(CONNECT_DATA=(SID={self.schemas})))" # noqa
            return f"{driver}://ORION:ORION@{dsn}"
        else:
            return URL.create(
                driver,
                host=self.host,
                port=self.port,
                database=self.schemas,
                username=self.username,
                password=self.password,
            )

    def get_connection(self):
        self.url_object = self.get_url()
        print(self.url_object)
        engine = create_engine(self.url_object,
                               pool_recycle=1800)
        return engine.connect()

    def get_engine(self):
        self.url_object = self.get_url()
        return create_engine(self.url_object,
                             pool_recycle=18000)


if __name__ == '__main__':
    from sqlalchemy import text

    # Example usage for different databases
    # MySQL
    mysqldatabase = DatabaseConnection(database_type='mysql',
                                       username='root',
                                       password='password',
                                       host='localhost',
                                       port='3306',
                                       schemas='sakila')
    connection = mysqldatabase.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # PostgreSQL
    postgresdatabase = DatabaseConnection(database_type='postgres',
                                          username='postgres',
                                          password='password',
                                          host='localhost',
                                          port='5432',
                                          schemas='your_database_name')
    connection = postgresdatabase.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # SQL Server
    sqldatabase = DatabaseConnection(database_type='sqlserver',
                                     username='user',
                                     password='password',
                                     host='localhost',
                                     port='1433',
                                     schemas='your_database_name')
    connection = sqldatabase.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # SQLite
    sqlitedatabase = DatabaseConnection(database_type='sqlite',
                                        username=None,
                                        password=None,
                                        host=None,
                                        port=None,
                                        schemas='your_database_name.db')
    connection = sqlitedatabase.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # MongoDB
    mongodb = DatabaseConnection(database_type='mongodb',
                                 username='user',
                                 password='password',
                                 host='localhost',
                                 port='27017',
                                 schemas='your_database_name')
    connection = mongodb.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # Redshift
    redshiftdatabase = DatabaseConnection(database_type='redshift',
                                          username='user',
                                          password='password',
                                          host='your-redshift-cluster-url',
                                          port='5439',
                                          schemas='your_database_name')
    connection = redshiftdatabase.get_connection()
    res = connection.execute(text("SELECT * FROM address"))
    print(res.fetchone())
    connection.close()

    # Oracle
    oracledatabase = DatabaseConnection(database_type='oracle',
                                        username='system',
                                        password='oracle',
                                        host='localhost',
                                        port='1539',
                                        schemas='xepdb1')
    connection = oracledatabase.get_connection()
    res = connection.execute(text("SELECT * FROM todoitem"))
    print(res.fetchone())
    connection.close()

