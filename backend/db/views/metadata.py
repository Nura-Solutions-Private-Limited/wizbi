import re

import structlog
from fastapi import HTTPException, status
from sqlalchemy import and_, inspect
from sqlalchemy.sql import text
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

from db.enums import DbType
from db.models.models import ConnectorType, Db_Conn, Pipeline, Source_Db_Mapping

logger = structlog.getLogger(__name__)


class Metadata:
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

    def add_metadata_entry(self, output_dict, table_name, column, type, datatype, length):
        entry_dict = {}
        if table_name not in output_dict.keys():
            output_dict[table_name] = []
        entry_dict["table_name"] = table_name
        entry_dict["column_name"] = column
        entry_dict["type"] = type
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
        if self.database_type == 'postgres':
            datatype_list = ["integer", "bigint", "smallint", "numeric", "real", "double precision",
                             "character varying", "character", "text", "bytea", "boolean", "timestamp",
                             "timestamptz", "date", "time", "timetz", "interval", "enum", "bit",
                             "bit varying", "integer[]", "json", "jsonb", "uuid", "inet", "cidr",
                             "macaddr", "point", "line", "lseg", "box", "path", "polygon", "circle",
                             "hstore", "xml", "tsvector", "tsquery"]
        elif self.database_type == 'mysql':

            datatype_query = text("SELECT distinct data_type FROM INFORMATION_SCHEMA.COLUMNS")
            rs = self.db.execute(datatype_query)
            rs_data = rs.fetchall()
            # column_names = [col for col in rs_data.keys()]
            # column_names = ["data_type"]
            # print([row[0] for row in rs_data])
            # datatype_list = [dict(zip(column_names, row)) for row in rs_data]
            datatype_list = [row[0] for row in rs_data]
        return datatype_list

    def get_db_metadata(self):
        '''
        Get database metadata if already exist then from source_db_mapping table
        otherwise generate from database and return it
        '''
        # output = ''
        output_dict = {}

        pipeline = self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()

        source_db_mapping = None

        if pipeline:
            source_db_mapping = self.db.query(Source_Db_Mapping).filter(
                Source_Db_Mapping.pipeline_id == self.pipeline_id).first()

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

        if str(self.database_type).upper() in [DbType.S3.value,
                                               'Amazon S3',
                                               'AMAZON S3',
                                               DbType.LFS.value,
                                               'Local System',
                                               'LOCAL SYSTEM',
                                               DbType.RESTAPI.value]:
            # return user saved mapping if there is any
            if source_db_mapping:
                return source_db_mapping.user_input
            # in case no mapping saved and source is restapi connection,
            # check if it has extra saved, if yes then return
            elif str(self.database_type).upper() == DbType.RESTAPI.value:
                extras = self.db.query(ConnectorType.extra).join(Db_Conn,
                                                                 and_(Db_Conn.db_type == ConnectorType.connector_type,
                                                                      Db_Conn.sub_type == ConnectorType.sub_type)
                                                                 ).first()
                if extras.extra:
                    return extras.extra
                return {}
            else:
                return {}
        else:
            if source_db_mapping:
                return source_db_mapping.user_input
            else:
                if self.database_type != "sqlserver":
                    schema = None
                else:
                    schema = self.schema
                # schema= "Person"
                table_list = self.inspector.get_table_names(schema=schema)
                logger.info(f'Table List : {table_list} in Schema : {schema}')
                for table_name in table_list:
                    logger.info(f'Table : {table_name}')
                    pk_consts = self.inspector.get_pk_constraint(table_name=table_name, schema=schema)
                    # print("table : " + table_name + "  val : " + str(cons))
                    fk_consts = self.inspector.get_foreign_keys(table_name=table_name, schema=schema)
                    fk_consts_cols = []
                    for fkcol in fk_consts:
                        for c in fkcol['constrained_columns']:
                            fk_consts_cols.append(c)
                    tbl_cols = self.inspector.get_columns(table_name=table_name, schema=schema)
                    time_cols = []
                    for col in tbl_cols:
                        if isinstance(col['type'], (Date, DateTime, TIMESTAMP, TIME, DATE)):
                            time_cols.append(col['name'])
                    for column in self.inspector.get_columns(table_name=table_name, schema=schema):
                        if column['name'] in pk_consts['constrained_columns']:
                            # output_list[table_name + '.' + column['name']] = 'attr'
                            self.add_metadata_entry(output_dict,
                                                    table_name,
                                                    column['name'],
                                                    'attr',
                                                    column['type'],
                                                    column['type'])

                        if column['name'] in fk_consts_cols:
                            for fkconst in fk_consts:
                                if fkconst['constrained_columns'][0] == column['name']:
                                    if fkconst['referred_schema'] == schema:
                                        self.add_metadata_entry(output_dict, table_name, column['name'],
                                                                'attr(' + fkconst['referred_table'] + '.' +
                                                                fkconst['referred_columns'][0] + ')',
                                                                column['type'],
                                                                column['type'])
                                    elif column['name'] not in pk_consts['constrained_columns']:
                                        self.add_metadata_entry(output_dict, table_name, column['name'],
                                                                'attr',
                                                                column['type'],
                                                                column['type'])
                                    # output_dict[table_name + '.' + column['name']] = \
                                    # 'attr(' + fkconst['referred_table'] + '.' + fkconst['referred_columns'][0] + ')'
                        elif isinstance(column['type'], (Integer, Float, BigInteger, BIGINT,
                                                         DECIMAL, SmallInteger, NUMERIC, SMALLINT)) \
                                and column['name'] not in pk_consts['constrained_columns']:
                            fkcons_for_mtrc = []
                            pkcons_for_mtrc = []
                            mtrc = "mtrc("
                            if len(fk_consts) > 0:
                                for fk in fk_consts:
                                    referred_tbl = fk['referred_table']
                                    for pk_col in fk['referred_columns']:
                                        for fk_col in fk['constrained_columns']:
                                            if fk['referred_schema'] == schema:
                                                fkcons_for_mtrc.append(table_name + '.' + fk_col + '(' +
                                                                       referred_tbl + '.' + pk_col + ')')
                            if len(pk_consts) > 0:
                                for pk in pk_consts['constrained_columns']:
                                    pkcons_for_mtrc.append(table_name + '.' + pk)

                            for pk in pkcons_for_mtrc:
                                mtrc = mtrc + pk + ','
                            for fk in fkcons_for_mtrc:
                                mtrc = mtrc + fk + ','

                            timedim_val = ""
                            if len(time_cols) > 0 and len(pkcons_for_mtrc) > 0:
                                timedim_lookup_tbl = "lookuptable=" + table_name
                                timedim_lookup_key = "lookupkey=" + pkcons_for_mtrc[0].split('.')[1]
                                timedim_time_col = "time=" + time_cols[0]
                                timedim_val = 'timedim(' + timedim_lookup_tbl + ',' + timedim_lookup_key \
                                    + ',' + timedim_time_col + ')'
                            elif len(fkcons_for_mtrc) > 0:
                                for fk in fk_consts:
                                    if fkconst['referred_schema'] == schema:
                                        referred_tbl_for_timedim = fk['referred_table']
                                        referred_col_for_timedim = fk['referred_columns'][0]
                                        timedim_lookup_tbl = "lookuptable=" + referred_tbl_for_timedim
                                        timedim_lookup_key = "lookupkey=" + referred_col_for_timedim

                                        tbl_cols = self.inspector.get_columns(referred_tbl_for_timedim)
                                        referred_time_cols = []
                                        for col in tbl_cols:
                                            if isinstance(col['type'], (Date, DateTime, TIMESTAMP, TIME, DATE)):
                                                referred_time_cols.append(col['name'])
                                        if len(referred_time_cols) > 0:
                                            timedim_time_col = "time=" + referred_time_cols[0]
                                            timedim_val = 'timedim(' + timedim_lookup_tbl + ',' + timedim_lookup_key \
                                                + ',' + timedim_time_col + ')'
                                            break
                            print(time_cols)
                            print("Table : " + table_name)
                            print("Column : " + column['name'])
                            # print (mtrc)
                            # print (pk_consts)
                            # print (fkcons_for_mtrc)
                            # print("===end===")
                            if timedim_val == "":
                                timedim_val = "timedim(time=systemtime)"
                            mtrc = mtrc + timedim_val + ')'
                            # output_dict[table_name + '.' + column['name']] = mtrc
                            self.add_metadata_entry(output_dict, table_name, column['name'],
                                                    mtrc,
                                                    column['type'],
                                                    column['type'])
                        else:
                            # output_dict[table_name + '.' + column['name']] = 'attr'
                            self.add_metadata_entry(output_dict, table_name, column['name'],
                                                    'attr',
                                                    column['type'],
                                                    column['type'])
                            # output = output + table_name + '.' + column['name'] + '=' + \
                            #        output_dict[table_name + '.' + column['name']] + '\n'

            return output_dict

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
