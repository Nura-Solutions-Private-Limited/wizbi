import os
# sys.path.append('.')
from sqlalchemy import ForeignKey, MetaData, create_engine, inspect, true, Enum, types, sql
from sqlalchemy.dialects.mysql import SET, ENUM
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
import sqlalchemy as sa
from db.auth.dbconnection import DatabaseConnection
import json
import collections
import constants


class SourceJson:
    def __init__(self,
                 connection,
                 db_type,
                 databaseName,
                 engine=None,
                 tenant_id=None) -> None:
        self.connection = connection
        self.db_type = db_type
        self.databaseName = databaseName
        self.tenant_id = tenant_id
        self.engine = engine
        self.output_json_file = os.path.join(os.path.join(os.getcwd(),
                                                          constants.JSON_FILE_PATH),
                                             constants.SOURCE_JSON_FILE)

    def generate_source_json(self):
        metadata_obj = MetaData()
        # metadata_obj.bind(self.engine)
        session = Session(self.engine)
        schema_list = []
        headr = collections.OrderedDict()
        metadata_obj.bind = self.engine
        if self.db_type == "sqlserver":
            metadata_obj.schema = self.databaseName
        metadata_obj.reflect()

        # headr['dbytype']=engine
        headr['Table_schema'] = self.databaseName

        # print("Metabdata %s", metadata_obj.tables)

        # print("######## before keys ##########")
        table_list = []
        for table in metadata_obj.tables:
            # Get table object for getting row count
            _table = metadata_obj.tables[table]
            table_row_count = session.query(_table).count()

            # print("######## key start##########")
            table_dict = collections.OrderedDict()
            table_dict['TableName'] = table.removeprefix(str(self.databaseName + '.'))
            table_dict['RowCount'] = table_row_count
            # table_dict['TableName']=table
            tablewithcols = metadata_obj.tables[table]
            index_column = None
            index_column_dtype = None

            non_pk_index_column = None
            non_pk_index_column_dtype = None

            col_list = []
            for col in tablewithcols.columns:
                col_dict = collections.OrderedDict()
                col_dict['ColumnName'] = col.name
                col_dict['ColumnType'] = str(col.type)
                col_dict['isPrimaryKey'] = col.primary_key

                if col.primary_key:
                    if isinstance(col.type, sa.Integer):
                        index_column = col.name
                        index_column_dtype = str(col.type)

                if col.foreign_keys:
                    print(col.foreign_keys, col.name, col.type)
                    if isinstance(col.type, sa.Integer):
                        non_pk_index_column = col.name
                        non_pk_index_column_dtype = str(col.type)
                else:
                    if isinstance(col.type, sa.Integer):
                        non_pk_index_column = col.name
                        non_pk_index_column_dtype = str(col.type)                    

                fk_list = []
                for key in col.foreign_keys:
                    # fk_dict=collections.OrderedDict()
                    # fk_dict['ForeignKeyFrom']=key.target_fullname
                    fk_list.append(key.target_fullname)
                    # col_dict['Constraints']= col.constraints
                col_dict['ForeignKey'] = fk_list
                # print("columntype is ",col.type)
                if isinstance(col.type, Enum):
                    enum_values = col.type.enums
                    # print(enum_values)
                    col_dict['ColumnType'] = col_dict['ColumnType'] + \
                        str(enum_values).replace('[', '(').replace(']', ')')
                elif isinstance(col.type, SET):
                    set_values = col.type.compile(self.connection.dialect)

                    col_dict['ColumnType'] = str(set_values).replace('[', '(').replace(']', ')')
                elif str(col.type).upper() == 'BYTEA':
                    col_dict['ColumnType'] = 'LONGBLOB'

                col_list.append(col_dict)

                if isinstance(col.type, sql.sqltypes.NullType):
                    col_dict.clear()
                    col_list.pop()

            table_dict['Columns'] = col_list
            if index_column:
                table_dict['index_column'] = index_column
                table_dict['index_column_dtype'] = index_column_dtype
            else:
                table_dict['index_column'] = non_pk_index_column
                table_dict['index_column_dtype'] = non_pk_index_column_dtype                
            table_list.append(table_dict)
        headr['Tables'] = table_list
        schema_list.append(headr)
        # print(schema_list)
        out_file = open(self.output_json_file, "w")

        json.dump(schema_list, out_file, indent=6)

        out_file.close()

        return self.output_json_file, schema_list


if __name__ == '__main__':
    mysqldatbase = DatabaseConnection(database_type='mysql',
                                      username='root',
                                      password='password',
                                      host='localhost',
                                      port='3306',
                                      database='sakila')
    connection = mysqldatbase.get_connection()
    sourceJson = SourceJson(connection=connection, databaseName="sakila")
    sourceJson.generate_source_json()
