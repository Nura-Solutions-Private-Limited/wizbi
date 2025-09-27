import gc
import traceback
import warnings
import pandas as pd
# import dask.dataframe as dd
import numpy as np
import json
from datetime import datetime
import logging

import wizbi_dataload.constants as constants
from wizbi_dataload.db.models.models import Job, Audit, Pipeline
from wizbi_dataload.db.dbutils.hashing import add_md5_hash_column
from wizbi_dataload.db.views.job import add_update_job_status
from wizbi_dataload.db.dbutils.datamapping import DataMapping

logger = logging.getLogger(__name__)


class EtlLoad:
    '''
    Read ETLJSON.json file, connect source and target database, generate etl script and load data
    '''

    def __init__(self,
                 source_con,
                 source_schema,
                 source_db_type,
                 target_con,
                 dest_schema,
                 dest_db_type,
                 source_engine,
                 target_engine,
                 pipeline_id,
                 db,
                 user_name,
                 etl_json_file=None,
                 etl_json_data=None,
                 json_data_yn=False) -> None:
        warnings.filterwarnings('ignore')

        self.source_con = source_con
        self.source_db_type = source_db_type
        self.source_schema = source_schema
        self.target_con = target_con
        self.dest_schema = dest_schema
        self.dest_db_type = dest_db_type
        self.source_engine = source_engine
        self.target_engine = target_engine
        self.etl_json_file = etl_json_file
        self.etl_json_data = etl_json_data
        self.json_data_yn = json_data_yn
        self.pipeline_id = pipeline_id
        self.user_name = user_name
        self.db = db
        self.read_size = constants.BATCH_SIZE

    def get_table_data(self,
                       table,
                       engine,
                       schema,
                       dbtype,
                       table_type=None,
                       load_id=None,
                       col_name=None,
                       filter_val=None,
                       query=None):
        '''
        read table, load data into dataframe and return it
        :param table: table name
        :type: str
        :param engine: sqlalchemy engine
        :type: sqlalchemy engine
        '''
        try:
            connection = engine.connect().execution_options(stream_results=True)

            # Set the default schema for the connection
            if dbtype == "sqlserver":
                schema = schema
                schema1 = schema + '.'
            else:
                schema = None
                schema1 = ""

            if query:
                for df in pd.read_sql_query(query, connection, chunksize=self.read_size):
                    yield df
            else:
                if table_type is not None and load_id is not None:
                    logger.info("running query to get data after load id : {}".format(load_id))
                    sql_query = (f"select * from {schema1}{table} where load_id >= {load_id}")
                    logger.info(sql_query)
                    for df in pd.read_sql_query(sql_query, connection, chunksize=self.read_size):
                        yield df
                elif col_name is not None and filter_val is not None:
                    sql_query = (f"select * from {schema1}{table} where {col_name} > '{filter_val}'")
                    logger.info(f"query :- {sql_query}")
                    for df in pd.read_sql_query(sql_query, connection, chunksize=self.read_size):
                        yield df
                else:
                    for df in pd.read_sql_table(table, connection, schema=schema, chunksize=self.read_size):
                        yield df

        except Exception as ex:
            logger.error("Error in reading table data:", ex)
            raise Exception("Error in reading table:-{} data. Error:- {}".format(table, ex))
        return df

    def read_etl_json(self, file_name):
        '''
        Read etl json file and return data
        :param file_name: etl json file name
        :type: str
        '''
        try:
            with open(file_name) as f:
                data = json.loads(f.read())
        except Exception as ex:
            logger.error("Error in reading file:-{} data. Error:- {}".format(file_name, ex))
            raise Exception("Error in reading file:-{} data. Error:- {}".format(file_name, ex))
        return data

    def add_update_load_status(self, job_id, load_start_time):
        '''
        Add or update job status
        '''
        job = self.db.query(Job).filter(Job.job_id == job_id).first()

        audit = self.db.query(Audit).filter(Audit.job_id == job.id).first()

        # if audit:
        #     pass
        # else:
        #     audit = Audit(pipeline_id=self.pipeline_id,
        #                   job_id=job.id,
        #                   load_date=load_start_time)
        #     self.db.add(audit)
        # self.db.commit()
        # self.db.refresh(audit)
        return audit.id

    def update_record_count(self, audit_id, fact_row_count):
        '''
        Update fact data load record count in audit table
        '''
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if audit:
            audit.inserts = fact_row_count
            self.db.commit()
            self.db.refresh(audit)
        else:
            logger.error("Error in updating record count")
            raise Exception("Error in updating record count")

    def get_last_load_id(self):
        all_audits = self.db.query(Audit).filter(Audit.pipeline_id == self.pipeline_id).all()
        audit = self.db.query(Audit).filter(Audit.pipeline_id == self.pipeline_id).order_by(Audit.id.desc()).first()
        logger.info(f"audit row count {len(all_audits)}")
        if len(all_audits) == 1:
            return None, None
        elif audit and len(all_audits) > 1:
            return audit.id, audit.load_date
        else:
            return None, None

    def get_delta(self, old_df, new_df):
        '''
        Compare old dataframe and new dataframe and return delta
        '''
        if not old_df.empty:
            old_df_data = add_md5_hash_column(old_df)
            old_df_data = old_df_data.loc[:, ['md5_hash']]

        if not new_df.empty:
            new_df_data = add_md5_hash_column(new_df)

        new_df_data = new_df_data.merge(old_df_data, indicator=True, how='left')

        delta_df = new_df_data[new_df_data['_merge'].isin(['left_only'])]
        delta_df = delta_df.drop(columns=['md5_hash', '_merge'], axis=1)

        return delta_df

    def get_matches(self, old_df, new_df):
        '''
        Compare old dataframe and new dataframe and return delta
        '''
        old_df_data = add_md5_hash_column(old_df)
        old_df_data = old_df_data.loc[:, ['md5_hash']]
        new_df_data = add_md5_hash_column(new_df)
        new_df_data = new_df_data.merge(old_df_data, indicator=True, how='inner')
        new_df_data = new_df_data.drop(columns=['md5_hash', '_merge'], axis=1)
        return new_df_data

    def load_dim(self, load_id, data, load_table):
        '''
        Load dimension tables
        '''
        dataMapping = DataMapping()
        dim_row_count = 0
        for schema in data:

            # Get table data
            tables = schema.get('Tables')
            for table in tables:
                gc.collect()
                # Get all column data
                columns = table.get('Columns')
                table_type = table.get('type')
                target_table = table.get('TargetTable')
                source_table = table.get('SourceTable')

                # dimension tables
                # if table_type == 'dim' and source_table == 'customers':
                if table_type == 'dim' and source_table == load_table:

                    dim_dfs = []
                    # read table data
                    all_source_df = self.get_table_data(table=source_table,
                                                        engine=self.source_engine,
                                                        schema=self.source_schema,
                                                        dbtype=self.source_db_type)
                    # source_set = 1
                    first_load = False
                    for source_df in all_source_df:
                        source_columns = list()
                        target_columns = list()
                        # prepare source dataframe
                        for column in columns:
                            # prepare list of source columns
                            if column.get('SourceColumn'):
                                source_columns.append(column.get('SourceColumn'))
                            if column.get('TargetColumn'):
                                target_columns.append(column.get('TargetColumn'))
                        source_df = source_df[source_columns]
                        # convert data types
                        source_df = dataMapping.convert_df_dtypes(engine=self.source_engine,
                                                                  dbtype=self.source_db_type,
                                                                  table=source_table,
                                                                  columns=source_df.columns.tolist(), # NOQA
                                                                  df=source_df)

                        # hash change start
                        all_target_df = self.get_table_data(table=target_table,
                                                            engine=self.target_engine,
                                                            schema=self.dest_schema,
                                                            dbtype=self.dest_db_type)
                        chunk_comp = 0
                        delta_data_df = pd.DataFrame()
                        # Loop through all target data chunks one by one to compare with source chunks
                        for target_df in all_target_df:
                            # If target table is empty then set the status and exit the target
                            # table loop to avoid comparison and proceed with data load
                            if target_df.empty:
                                first_load = True
                                break
                            target_df = target_df[source_columns]

                            # convert data types
                            target_df = dataMapping.convert_df_dtypes(engine=self.target_engine,
                                                                      dbtype=self.dest_db_type,
                                                                      table=target_table,
                                                                      columns=target_df.columns.tolist(), # NOQA
                                                                      df=target_df)

                            # print(existing_data.columns)
                            # source_data = source_df[source_columns]

                            if chunk_comp == 0:
                                # compare source data chunk with all target data chunks one by one
                                match_data_df = self.get_matches(target_df, source_df)
                            else:
                                match_data_df = self.get_matches(target_df, delta_data_df)

                            # if matched data rows are empty, that means all rows are new
                            if match_data_df.empty:
                                delta_data_df = source_df
                            # in case match data rows are not empty,
                            # that means delta -> source data minus match data rows
                            else:
                                delta_data_df = self.get_delta(match_data_df, source_df)
                            if delta_data_df.empty:
                                break
                            # print('delta shape', delta_data_df.shape)
                            chunk_comp = chunk_comp + 1
                            # target_set = target_set + 1

                        if first_load:
                            logger.info(f'First data load, loading {source_df.shape[0]} rows in table - {target_table}') # NOQA
                            source_df.to_sql(target_table,
                                             con=self.target_engine,
                                             index=False,
                                             if_exists="append")
                            dim_row_count = dim_row_count + source_df.shape[0]
                            del source_df
                        else:
                            dim_dfs.append(delta_data_df)
                        # source_set = source_set + 1
                    if not first_load:
                        delta_df = pd.concat(dim_dfs)
                        logger.info(f'Delta rows - {delta_df.shape[0]} for table - {target_table}')
                        if not delta_df.empty:
                            logger.info(f'Loading delta {delta_df.shape[0]} rows in table - {target_table}')
                            delta_df.to_sql(target_table,
                                            con=self.target_engine,
                                            index=False,
                                            if_exists="append")
                            dim_row_count = dim_row_count + delta_df.shape[0]
                            del delta_df
        return dim_row_count

    def load_fact(self, load_id, last_load_id, last_load_date, data, fact_key):
        '''
        Load fact table
        '''
        dataMapping = DataMapping()
        first_load = False
        fact_row_count = 0
        for schema in data:

            # Get table data
            tables = schema.get('Tables')
            for table in tables:
                # Get all column data
                columns = table.get('Columns')
                table_type = table.get('type')
                target_table = table.get('TargetTable')
                # source_table = table.get('SourceTable')

                # fact_load_checks = self.get_table_data(table=target_table,
                #                                        engine=self.target_engine,
                #                                        schema=self.dest_schema,
                #                                        dbtype=self.source_db_type,
                #                                        table_type='fact',
                #                                        load_id=None)

                audit = self.db.query(Audit).filter(Audit.pipeline_id == self.pipeline_id).all()
                if len(audit) == 1:
                    first_load = True
                else:
                    first_load = False
                # for load_check in fact_load_checks:
                #     if load_check.empty:
                #         first_load = True
                #     else:
                #         first_load = False
                #     break

                # dimension tables
                # if table_type == 'dim' and source_table == 'customers':
                if table_type == 'fact':
                    for column in columns:
                        source_columns = list()
                        source_columns.append(column.get('TargetColumn'))
                        if column.get('LookupColumn') == fact_key:  # 'creditLimit':
                            logger.info(f'Load started for metric: {fact_key}')
                            # get ETLKeys values
                            sub = column.get('ETLKeys')
                            insert_columns = list()
                            # prepare insert column list
                            insert_columns.append(column.get('TargetColumn'))
                            select_columns = column.get('LookupColumn')  # noqa
                            look_up_table = column.get('LookupTable')

                            timeids = column.get('TimeIDs')
                            # timeid_columns = list()
                            # if time id source is table data
                            time_id_table = timeids.get('TimeIDTable')
                            time_id_join_column = timeids.get('TimeIDLookupkey')
                            time_id_target_column = timeids.get('TimeIDTargetColumn')
                            time_id_column = timeids.get('TimeIDColumn')
                            insert_columns.append(time_id_target_column)
                            source_columns.append(time_id_target_column)
                            dim_columns = list()
                            for s in sub:
                                # merge source time dim table with source look up table
                                # generate sql statement to run once for each fact key
                                if time_id_table:
                                    # TODO add date filter based on last load date
                                    if last_load_date:
                                        source_look_up_query = (f"select {look_up_table}a.*, {time_id_table}b.{time_id_column} as {time_id_target_column} " # NOQA
                                                                f"from {look_up_table} as {look_up_table}a join {time_id_table} as {time_id_table}b on " # NOQA
                                                                f"{look_up_table}a.{time_id_join_column} = {time_id_table}b.{time_id_join_column} " # NOQA
                                                                f"where {time_id_table}b.{time_id_column} >= '{last_load_date}' ") # NOQA
                                    else:
                                        source_look_up_query = (f"select {look_up_table}a.*, {time_id_table}b.{time_id_column} as {time_id_target_column} " # NOQA
                                                                f"from {look_up_table} as {look_up_table}a join {time_id_table} as {time_id_table}b on " # NOQA
                                                                f"{look_up_table}a.{time_id_join_column} = {time_id_table}b.{time_id_join_column}") # NOQA                                                                                            
                                    # print(source_look_up_query)
                                    all_source_look_up_df = self.get_table_data(table=look_up_table,
                                                                                engine=self.source_engine,
                                                                                schema=self.source_schema,
                                                                                dbtype=self.source_db_type,
                                                                                query=source_look_up_query)
                                else:
                                    # get look up table dataframe
                                    all_source_look_up_df = self.get_table_data(table=look_up_table,
                                                                                engine=self.source_engine,
                                                                                schema=self.source_schema,
                                                                                dbtype=self.source_db_type)

                                # loop through source look up dataframe in chunks
                                # for each chunk, find the matching dimension table
                                # data by merging source look up dataframe chunk
                                etl_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
                                for source_look_up_df in all_source_look_up_df:
                                    if time_id_table:
                                        source_look_up_df['TimeID'] = pd.to_datetime(source_look_up_df['TimeID']).dt.strftime('%Y%m%d%H%M%S').astype(int) # NOQA
                                    else:
                                        source_look_up_df['TimeID'] = int(etl_datetime)

                                    # convert data types
                                    source_look_up_df = dataMapping.convert_df_dtypes(engine=self.source_engine,
                                                                                      dbtype=self.source_db_type,
                                                                                      table=look_up_table,
                                                                                      columns=source_look_up_df.columns.tolist(), # NOQA
                                                                                      df=source_look_up_df)

                                    insert_columns.append(s.get('FactKey'))
                                    dim_look_up_table = s.get('LookupDim')
                                    dim_key = s.get('DimKey')
                                    fact_key = s.get('FactKey')
                                    source_columns.append(s.get('FactKey'))

                                    dest_join_key = list()
                                    source_join_key = list()
                                    dest_join_key.append(s.get('DestLookupKey'))
                                    source_join_key.append(s.get('SourceLookupKey'))

                                    dim_columns.append(s.get('DestLookupKey'))
                                    dim_columns.append(s.get('FactKey'))

                                    # get dimension table dataframe
                                    all_dim_look_up_df = self.get_table_data(table=dim_look_up_table,
                                                                             engine=self.target_engine,
                                                                             schema=self.dest_schema,
                                                                             dbtype=self.dest_db_type)
                                    counter = 1
                                    dim_matches = []
                                    # loop through dim look up table in chunks and
                                    # find matches for the source look up chunks
                                    # collect all matches for comparing it with existing fact table data load
                                    for dim_look_up_df in all_dim_look_up_df:
                                        counter = counter + 1
                                        # rename look up dimension table column with fact table column
                                        dim_look_up_df.rename(columns={dim_key: fact_key}, inplace=True)

                                        dim_look_up_df = dim_look_up_df[dim_columns]

                                        # convert data types
                                        dim_look_up_df = dataMapping.convert_df_dtypes(engine=self.target_engine,
                                                                                       dbtype=self.dest_db_type,
                                                                                       table=dim_look_up_table,
                                                                                       columns=dim_look_up_df.columns.tolist(), # NOQA
                                                                                       df=dim_look_up_df)

                                        match_lookup_df = pd.merge(source_look_up_df,
                                                                   dim_look_up_df,
                                                                   indicator=True,
                                                                   how='inner',
                                                                   right_on=dest_join_key,
                                                                   left_on=source_join_key)
                                        dim_matches.append(match_lookup_df)
                                        # break

                                    dim_columns.clear()
                                    dim_matches_df = pd.concat(dim_matches)
                                    dim_matches_df = dim_matches_df[source_columns]
                                    # logger.info('dim look up size ', dim_matches_df.shape)

                                    # load existing fact table, if there is any data
                                    # then compare the above chunk of data with fact table
                                    # and load delta in fact table
                                    # In case of empty fact table, skip comparison and load into fact table
                                    all_fact_df = self.get_table_data(table=target_table,
                                                                      engine=self.target_engine,
                                                                      schema=self.dest_schema,
                                                                      dbtype=self.dest_db_type,
                                                                      table_type='fact',
                                                                      load_id=last_load_id)
                                    if first_load:
                                        logger.info(f"First load, loading {dim_matches_df.shape[0]} rows into fact table") # NOQA
                                        logger.info(dim_matches_df.shape)
                                        dim_matches_df['load_id'] = load_id
                                        fact_row_count = fact_row_count + dim_matches_df.shape[0]
                                        dim_matches_df.to_sql(target_table,
                                                              con=self.target_engine,
                                                              index=False,
                                                              if_exists="append")
                                    else:
                                        for fact_df in all_fact_df:
                                            fact_df = fact_df[insert_columns]
                                            # fact_df = fact_df.convert_dtypes()
                                            # convert data type
                                            fact_df = dataMapping.convert_df_dtypes(engine=self.target_engine,
                                                                                    dbtype=self.dest_db_type,
                                                                                    table=target_table,
                                                                                    columns=fact_df.columns.tolist(),
                                                                                    df=fact_df)
                                            # compare dim_matches dataframe with
                                            # fact dataframe chunks one by one and find matches
                                            match_data_df = self.get_matches(fact_df, dim_matches_df)
                                            # if matched data rows are empty, that means all rows are new
                                            # logger.info("dim table shape", dim_matches_df.shape)
                                            if not match_data_df.empty:
                                                dim_matches_df = self.get_delta(match_data_df, dim_matches_df)
                                            # logger.info(match_data_df.shape, dim_matches_df.shape)

                                            if dim_matches_df.empty:
                                                break
                                        dim_matches_df['load_id'] = load_id
                                        logger.info(f'Delta load -- {dim_matches_df.shape[0]} rows')

                                        if not dim_matches_df.empty:
                                            fact_row_count = fact_row_count + dim_matches_df.shape[0]
                                            logger.info(f'Loading delta - {dim_matches_df.shape[0]} rows in fact table')
                                            dim_matches_df.to_sql(target_table,
                                                                  con=self.target_engine,
                                                                  index=False,
                                                                  if_exists="append")
                                        logger.info(datetime.now())

                                    # Remove factkey from source_column list
                                    source_columns.remove(s.get('FactKey'))

                                    # remove factkey from insert column list
                                    insert_columns.remove(s.get('FactKey'))
        return fact_row_count

    def update_dim_fsk(self):
        data = self.etl_json_data
        try:
            for schema in data:
                # Get table data
                tables = schema.get('Tables')
                for table in tables:

                    # Get all column data
                    columns = table.get('Columns')
                    table_type = table.get('type')
                    target_table = table.get('TargetTable')
                    source_table = table.get('SourceTable')

                    # dimension tables
                    if table_type == 'dim1':
                        source_columns = list()
                        target_columns = list()
                        # prepare source dataframe
                        for column in columns:
                            # prepare list of source columns
                            if column.get('SourceColumn'):
                                source_columns.append(column.get('SourceColumn'))
                            if column.get('TargetColumn'):
                                target_columns.append(column.get('TargetColumn'))
                            if column.get('ForeignKey'):
                                # print(column.get('SourceColumn'))
                                # print(target_table)
                                # print(column.get('ForeignKey'))
                                for fk_data in column.get('ForeignKey'):
                                    source_col = column.get('SourceColumn')
                                    source_table = fk_data.get('SourceFkey').split('.')[0]
                                    # update_sql = 'UPDATE ' + target_table + ' set ' + fk_data.get('DestFkey') + \
                                    #     ' = ( select ' + fk_data.get('SourceFkey') + ' from ' + source_table + \
                                    #         ' where ' + source_table + '.' + fk_data.get('TargetJoinColumn') + \
                                    #             ' = ' + target_table + '.' + source_col + ')' + \
                                    #             ' where 1=1 and ' + target_table + '.' + fk_data.get('DestFkey') + \
                                    #             ' is null and ' + target_table + '.' + source_col + ' is not null'
                                    try:
                                        update_sql = 'UPDATE ' + target_table + ' tt' + \
                                            ' join ( select * from ' + source_table + ' ) it' + ' on  tt.' \
                                            + source_col + ' = ' + ' it.' + fk_data.get('TargetJoinColumn') + \
                                            ' set ' + 'tt.' + source_col + ' = ' + 'it.' + \
                                            fk_data.get('TargetJoinColumn') + ' where 1=1 and ' + \
                                            'tt.' + source_col + ' is null ' + 'and it.' + \
                                            fk_data.get('TargetJoinColumn') + ' is not null'
                                        try:
                                            _ = self.target_con.exec_driver_sql(update_sql)
                                        except Exception as ex:
                                            logger.error(f'Error while executing : {update_sql} with errors :{str(ex)}')
                                    except Exception as ex:
                                        logger.error(f'Error while generating sql for updating pk/fk \
                                                     relationship: {str(ex)}')
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error("Error in updating fks :{}".format(str(ex)))
            raise ex

    def load_data(self, job_id, load_type, load_key):
        '''
        Generate etl script and load data
        '''
        logger.info('Json/Data:- {}'.format(self.json_data_yn))

        # Update job status to running
        # job_status = 'Running'
        current_time = datetime.now()

        last_load_id, last_load_date = self.get_last_load_id()
        logger.info(f'last load details load_id: {last_load_id} load_date: {last_load_date}')

        load_id = self.add_update_load_status(job_id=job_id, load_start_time=current_time)

        if self.json_data_yn:
            data = self.etl_json_data
        else:
            data = self.read_etl_json(self.etl_json_file)

        if load_type == 'dim':
            # load dimension table
            logger.info("Dimension tables load started")
            dim_row_count = self.load_dim(load_id=load_id, data=data, load_table=load_key)
            logger.info("Dimension tables load ended")
            return dim_row_count
        elif load_type == 'fact':
            # load fact table
            logger.info("Fact table load started")
            fact_row_count = None
            fact_row_count = self.load_fact(load_id=load_id,
                                            last_load_id=last_load_id,
                                            last_load_date=last_load_date,
                                            data=data,
                                            fact_key=load_key)
            logger.info("Fact table load ended")
            return fact_row_count
            # update row loaded of fact in audit table
            # self.update_record_count(audit_id=load_id, fact_row_count=fact_row_count)
        elif load_type == 'fks':
            logger.info("Dimension fk update started")
            _ = self.update_dim_fsk()
            logger.info("Dimension fks update ended")
            return None


if __name__ == '__main__':
    etlload = EtlLoad()
    etlload.load_data()
