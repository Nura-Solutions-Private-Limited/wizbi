import structlog

# import pandas as pd
# import modin.pandas as pd
from sqlalchemy import inspect

logger = structlog.getLogger(__name__)

mysql_data_mappings = {
    "TINYINT": "Int8",
    "SMALLINT": "Int16",
    "MEDIUMINT": "Int32",
    "INT": "Int32",
    "INTEGER": "Int32",
    "BIGINT": "Int64",
    "DECIMAL": "float64",
    "FLOAT": "float32",
    "DOUBLE": "float64",
    "DATE": "datetime64[s]",
    "DATETIME": "datetime64[us]",
    "TIMESTAMP": "datetime64[ns]",
    "VARCHAR": "string",
    "TEXT": "string",
    "CHAR": "string",
    "BINARY": "bytes",
    "VARBINARY": "bytes",
    "BLOB": "bytes",
}


class DataMapping:
    def __init__(self) -> None:
        pass

    def get_data_type(self,
                      engine,
                      dbtype,
                      table,
                      columns=None):
        '''
        Get data type of given table from database and map with pandas data type
        '''
        try:
            insp = inspect(engine)
            columns_table = insp.get_columns(table)
            data_dict = {}
            if columns:
                data_dict = dict((c['name'], str(c['type']).split('(')[0])
                                 for c in columns_table if c['name'] in columns)
            else:
                data_dict = dict((c['name'], str(c['type']).split('(')[0]) for c in columns_table)

            if dbtype == 'mysql':
                if data_dict:
                    return dict((k, mysql_data_mappings.get(v)) for k, v in data_dict.items())
                else:
                    return None
            else:
                return None
        except Exception as ex:
            logger.error(f"Exception in get_data_type :{ex}")
            raise (f"Exception in get_data_type :{ex}")

    def convert_df_dtypes(self,
                          engine,
                          dbtype,
                          table,
                          columns,
                          df):
        '''
        Convert a dataframe data type based on data type mapping,
        if mapping does not exist then use default data type inference
        '''

        col_map = self.get_data_type(engine=engine,
                                     dbtype=dbtype,
                                     table=table,
                                     columns=columns)
        if col_map:
            df = df.astype(col_map)
        else:
            df = df.convert_dtypes()

        return df
