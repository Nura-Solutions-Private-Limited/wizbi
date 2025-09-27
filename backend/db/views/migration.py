import collections
import re

import structlog
from fastapi import HTTPException, status
from sqlalchemy import Enum, MetaData, inspect, sql, types
from sqlalchemy.dialects.mysql import ENUM, SET
from sqlalchemy.types import (
    BIGINT,
    DATE,
    DECIMAL,
    NUMERIC,
    SMALLINT,
    TIME,
    TIMESTAMP,
    BigInteger,
    Date,
    DateTime,
    Float,
    Integer,
    SmallInteger,
)

from db.models.models import Pipeline, Source_Db_Mapping

logger = structlog.getLogger(__name__)


class MigrationMetadata:
    def __init__(self,
                 pipeline_id=None,
                 db=None,
                 chosen_schema=None,
                 database_type=None,
                 engine=None,
                 ) -> None:
        self.engine = engine
        self.pipeline_id = pipeline_id
        self.db = db
        self.schema = chosen_schema
        self.database_type = database_type
        if engine:
            self.inspector = inspect(engine)

    def add_metadata_entry(self, output_dict, table_name, column, datatype, length):
        entry_dict = {}
        if table_name not in output_dict.keys():
            output_dict[table_name] = []
        entry_dict["table_name"] = table_name
        entry_dict["column_name"] = column
        entry_dict["datatype"] = f"{datatype}"
        tmp = f"'{length}'"
        pattern = r'(\d+)'
        match = re.search(pattern, tmp)
        if match:
            entry_dict["length"] = match.group(1)
        else:
            entry_dict["length"] = ''
        output_dict[table_name].append(entry_dict)

    def get_datatypes(self):
        '''
        Get all supported data types in mysql
        '''
        if self.database_type =='postgres':
            datatype_list  =[
                               "integer",  "bigint", "smallint", "numeric", "real","double precision","character varying","character",
                               "text","bytea","boolean","timestamp","timestamptz","date","time","timetz","interval","enum","bit",
                               "bit varying","integer[]","json","jsonb","uuid","inet","cidr","macaddr","point","line""lseg",
                               "box","path","polygon","circle","hstore","xml","tsvector","tsquery"
                           ]
        elif self.database_type == 'mysql':

            datatype_query = "SELECT distinct data_type FROM INFORMATION_SCHEMA.COLUMNS"
            rs = self.db.execute(datatype_query)
            rs_data = rs.fetchall()
            # column_names = [col for col in rs_data.keys()]
            # column_names = ["data_type"]
            # print([row[0] for row in rs_data])
            # datatype_list = [dict(zip(column_names, row)) for row in rs_data]
            datatype_list = [row[0] for row in rs_data]
        return datatype_list

    def get_migrate_db_metadata(self):
        '''
        Get database metadata if already exist then from source_db_mapping table
        otherwise generate from database and return it
        '''
        # output = ''

        pipeline = self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()

        source_db_mapping = None

        if pipeline:
            source_db_mapping = self.db.query(Source_Db_Mapping).filter(
                Source_Db_Mapping.pipeline_id == self.pipeline_id).first()

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

        if source_db_mapping:
            return source_db_mapping.user_input
        else:
            if self.database_type == "mysql"  or self.database_type == "postgres":
                schema = None
            elif self.database_type == "sqlserver":
                schema = self.schema
            # schema= "Person"
               
            #table_list = self.inspector.get_table_names(schema=schema)
        
            #logger.info(f'Table List : {table_list} in Schema : {schema}')
            metadata_obj = MetaData()
            metadata_obj.reflect(bind=self.engine,schema=schema)
            table_list=metadata_obj.tables
            logger.info(f'Table List : {table_list} in Schema : {schema}')

            """  insp=inspect(engine)
            for table in metadata_obj.tables:
                tables=insp.reflect_table(metadata_obj.tables[table],None)
            print(tables)
            """
            schema_list = []
            headr=collections.OrderedDict()
            #headr['dbytype']=engine
            headr['Table_schema']=self.schema
            #print("Metabdata %s", metadata_obj.tables)

            #print("######## before keys ##########")
            new_table_list=[]
            for table in metadata_obj.tables:
        
            #for table in table_list:
                #print("######## key start##########")
                table_dict=collections.OrderedDict()
                tablename=table.removeprefix(str(self.schema+'.'))
                print (tablename)
                table_dict.key=tablename
                print(table_dict)
                #tablewithcols = self.inspector.get_columns(table_name=tablename, schema=schema)

                tablewithcols = metadata_obj.tables[table]
                col_list=[]
                for col in tablewithcols.columns:
                #for col in tablewithcols:
                    print(col)
                    col_dict=collections.OrderedDict()
                    col_dict['ColumnName']=col.name
                    col_dict['ColumnType']=str(col.type)
                    col_dict['isPrimaryKey']=col.primary_key
                    fk_list=[]
                    #if col.get("foreign_keys"):
                    for key in col.foreign_keys:
                            target_table = key.column.table.name
                            target_column = key.column.name

                            fk_list.append(f"{target_table}.{target_column}")
                            #fk_list.append(key.target_fullname)

                            #col_dict['Constraints']= col.constraints
                    col_dict['ForeignKey']=fk_list
                    #print("columntype is ",col.type)
                    if isinstance(col.type,Enum) :               
                        enum_values = col.type.enums
                        #print(enum_values)
                        col_dict['ColumnType']=col_dict['ColumnType']+str(enum_values).replace('[','(').replace(']',')')
                    elif  isinstance(col.type,SET):
                        set_values = col.type.compile(self.engine.dialect)

                        col_dict['ColumnType']=str(set_values).replace('[','(').replace(']',')') 
                    
                    col_list.append(col_dict)
                    
                    if  isinstance(col.type,sql.sqltypes.NullType):
                        col_dict.clear()
                        col_list.pop()
                    
                
                table_dict[tablename]=col_list
                new_table_list.append(table_dict)
            #headr['Tables']=table_list
            #schema_list.append(headr)
  
            #return schema_list
            return new_table_list

    def save_user_input(self, user_input):
        # Query source database mapping againt pipeline id to check if already exist
        source_db_mapping = self.db.query(Source_Db_Mapping).filter(
            Source_Db_Mapping.pipeline_id == self.pipeline_id).first()

        # If source database mapping exist then update
        if source_db_mapping:
            source_db_mapping.user_input = user_input

        # If source database mapping does not exist then create new
        else:
            source_db_mapping = Source_Db_Mapping(pipeline_id=self.pipeline_id,
                                                  user_input=user_input)
            self.db.add(source_db_mapping)
        pipeline = self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        pipeline.status = 'Saved'

        # Commit changes to database and return the dataset
        self.db.commit()
        self.db.refresh(source_db_mapping)
        self.db.refresh(pipeline)

        return source_db_mapping