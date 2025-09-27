from db.dbutils.datawarehouse import Datawarehouse
from db.views.metadata import Metadata
from db.auth.dbconnection import DatabaseConnection
from schemas.database import DatabaseConn
import sys
sys.path.append('d:\\dev\\WizBI\\rebiz\\backend\\')


def generate_metadata():
    '''
    Generate metadata from source database
    '''
    databaseConn = DatabaseConnection(database_type="mysql",
                                      username="root",
                                      password="password",
                                      host="192.168.1.8",
                                      port="3306",
                                      schemas="classicmodels")
    engine = databaseConn.get_engine()
    metadata = Metadata(engine=engine)
    data = metadata.get_db_metadata()
    return data


def generate_timedim():
    '''
    Generate metadata from source database
    '''
    databaseConn = DatabaseConnection(database_type="mysql",
                                      username="root",
                                      password="password",
                                      host="192.168.1.8",
                                      port="3306",
                                      schemas="Rebiz_classicmodels_DW")

    datawarehouse = Datawarehouse(databaseConn, databaseConn.get_raw_connection(), 'test')

    # datawarehouse.create_database_with_obj()
    datawarehouse.create_time_dimension()
    datawarehouse.populate_time_dim('2023-12-01 11:00', '2023-12-31 11:59')


if __name__ == "__main__":
    generate_timedim()
