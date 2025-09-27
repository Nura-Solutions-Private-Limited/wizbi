import collections
import json
from datetime import datetime, timedelta

import structlog
from fastapi import HTTPException, status
from sqlalchemy import Column, Integer, MetaData, String, Table, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy_utils import create_database, database_exists, get_tables

from db.models.models import Pipeline
from db.views.report import create_report
from schemas.report import CreateReport

logger = structlog.getLogger(__name__)


class PostGresDatawarehouse:
    def __init__(self,
                 pipeline_id,
                 db,
                 user,
                 connection,
                 raw_connection,
                 engine,
                 dimfact_json_file,
                 etl_json_file,
                 dw_name) -> None:
        self.pipeline_id = pipeline_id
        self.db = db
        self.user = user
        self.connection = connection
        self.raw_connection = raw_connection
        if engine:
            self.engine=engine
            self.inspector = inspect(engine)
        self.Session = sessionmaker(bind=self.engine)

        self.dimfact_json_file = dimfact_json_file
        self.etl_json_file = etl_json_file
        self.dw_name = dw_name

    def createDW(self, dwName):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        # existing_databases=mycursor.fetchall()
            logger.info("Database schema:-{} created".format(dwName))
        else:
            logger.info("Using the existing data warehouse. \
                        Database schema with name:- {} exits in database".format(dwName))
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            # detail="Database schema with name:- {} exits in database".format(dwName))

    def createTimeid(self, dW, table):
        # record = self.connection.execute("select database();").fetchone()
        # record = mycursor.fetchone()
       self.connection.execute('ALTER TABLE "{}" ADD COLUMN "TimeID" BIGINT NOT NULL, ADD COLUMN load_id BIGINT NOT NULL;'.format (table))


    def createTable(self, dW, table, columnName, columnType, Pkey, Fkey):
          
        metadata=MetaData(bind=self.engine)
        metadata.reflect()
        existing_tables = metadata.tables.keys()
        #print('dsafdasdfedfdgdfgdfd',existing_tables)
        
        if table in existing_tables:
            logger.info("Altering Table:-{} ".format(table))

            # print("In table ", table)
            your_table = Table(table, metadata,autoLoad= True)

            # print("In table ", table)
            existing_columns =  your_table.columns.keys()
            if columnName not in (existing_columns):
                logger.info("Adding Column:-{} ".format(columnName))

                # print(columnName)
                self.connection.execute('ALTER TABLE "{}" ADD "{}" {};'.format( table, columnName, columnType))


                """ if Pkey:
                    # Adding a primary key constraint
                    # Add primary key constraint
                    self.connection.execute('ALTER TABLE "{}" ADD CONSTRAINT {}_pk PRIMARY KEY ("{}");'.format(table, table, columnName))

                    # Alter column to set data type to serial with auto-increment
                    self.connection.execute('ALTER TABLE "{}" ALTER COLUMN "{}" SERIAL;'.format(table, columnName))
 """
                if Fkey:
                    for key in Fkey:
                        refTable = key.split('.')[0]
                        if refTable not in existing_tables:
                            # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                            self.connection.execute('CREATE TABLE "{}" ("RBID" SERIAL PRIMARY KEY);'.format( refTable))


                        refColumn = key.removeprefix(refTable + '.')
                        foreignKey = refTable + '_' + refColumn
                        if foreignKey not in (existing_columns):
                            # Adding the foreign key column
                            self.connection.execute('ALTER TABLE "{}" ADD COLUMN "{}" INT'.format(table, foreignKey))

                            # Adding the foreign key constraint
                            self.connection.execute('ALTER TABLE "{}" ADD CONSTRAINT {}_{}_fk FOREIGN KEY ("{}") REFERENCES "{}"("RBID");'.format(table, table, foreignKey, foreignKey, refTable))

        else:
            # print(dW,'blahblah')
            # pdb.set_trace()
            logger.info("Creating Table:-{} ".format(table))

            self.connection.execute('CREATE TABLE "{}" ("RBID" SERIAL PRIMARY KEY ,"{}" {});'.format(table, columnName, columnType))
            if Fkey:
                for key in Fkey:
                    refTable = key.split('.')[0]
                    if refTable not in existing_tables:
                        # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                        self.connection.execute('CREATE TABLE "{}" ("RBID" SERIAL PRIMARY KEY);'.format(refTable))

                    refColumn = key.removeprefix(refTable + '.')
                    foreignKey = refTable + '_' + refColumn
                    self.connection.execute('ALTER TABLE "{}" ADD COLUMN "{}" INT'.format(table, foreignKey))

                    # Adding the foreign key constraint
                    self.connection.execute('ALTER TABLE "{}" ADD CONSTRAINT {}_{}_fk FOREIGN KEY ("{}") REFERENCES "{}"("RBID");'.format(table, table, foreignKey, foreignKey,refTable))

        # closeConnection(con)

    def drawERdiagram(self, dWName, clientschema):
        graph = create_schema_graph(metadata=MetaData('mysql://root:password@localhost/' + dWName))
        graph.write_png('./' + clientschema + '_DW_erd.png')

    def create_time_dimension(self, dW):
        metadata=MetaData(bind=self.engine)
        existing_tables = self.inspector.get_table_names(schema=dW)

        if "time_dim" not in existing_tables:
            time_dim_table = Table(
                'time_dim',
                metadata,
                Column('time_id', Integer, primary_key=True),
                Column('fulltime', Integer),
                Column('day', Integer),
                Column('month', Integer),
                Column('year', Integer),
                Column('hour', Integer),
                Column('minute', Integer),
                Column('second', Integer),
                Column('ampm', String(2)),
            )
            metadata.create_all()
    def create_database_with_obj(self):
        with open(self.dimfact_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        clientschema = schema_dict.get('Source_schema')
        
        if self.dw_name:
            dWName = self.dw_name
        else:
            schemaName = schema_dict.get('Table_schema')
            dWName = str(schemaName)

        self.createDW(dWName)
        
        for tName in schema_dict['Tables']:
            for cName in tName['Columns']:
                newTable = tName['TableName']
                self.createTable(dWName, newTable, cName['ColumnName'], cName['ColumnType'], cName.get(
                    'isPrimaryKey'), cName.get('ForeignKey'))
        self.createTimeid(dWName, clientschema + '_fact')
        self.create_time_dimension(dWName)
        #self.populate_time_dim(dWName)
        # self.drawERdiagram(dWName)
        

    def populate_time_dim(self, dW):
        startDate = datetime.now().replace(month=1, day=1, hour=0, minute=0)
        endDate = datetime.now().replace(month=12, day=31,hour=23, minute=59)
        """ startDate = startDate.strftime('%Y-%m-%d %H:%M')
        endDate = endDate.strftime('%Y-%m-%d 23:59')
        startDate = datetime.strptime(startDate, '%Y-%m-%d %H:%M')  # Convert string to datetime
        endDate = datetime.strptime(endDate, '%Y-%m-%d %H:%M')  # Convert string to datetime
 """
        # startDate, endDate = '2023-01-01 00:00','2023-12-31 23:59'
        session = self.Session()
        metadata = MetaData(bind=self.engine)
        time_dim = Table("time_dim", metadata, autoload=True)
        current_time = startDate
        while current_time <= endDate:
                time_data = {
                    'time_id': int(current_time.timestamp()),
                    'fulltime': int((current_time.timestamp())),
                    'day': current_time.day,
                    'month': current_time.month,
                    'year': current_time.year,
                    'hour': current_time.hour,
                    'minute': current_time.minute,
                    'second': current_time.second,
                    'ampm': current_time.strftime('%p')
                }

                session.execute(time_dim.insert().values(time_data))

                current_time += timedelta(minutes=1)

        session.commit()
        session.close()

    def time_based_report(self, dw, clientschema, attrs, metric, lookupDim, periodcity):
        query_template = "SELECT {column_list} FROM {table_list} WHERE {conditions} GROUP BY {group_by_list};"
        if periodcity == 'Daily':
            period = 'day'
        elif periodcity == 'Monthly':
            period = 'month'
        else:
            period = 'year'
        # Define the replacement values
        column_names = attrs + " ,SUM(" + metric + ") AS sum_" + metric + " ,time_dim." + period
        table_names =  str(clientschema) + "_fact fact, " + lookupDim + " ,time_dim"
        conditions =  lookupDim + ".RBID = fact." + lookupDim + "_RBID AND ROUND(time_dim.time_id/100) = ROUND(fact.timeID/100)"
        group_by_names = attrs + " ,time_dim." + period

        # Replace the placeholders in the template
        query = query_template.format(column_list=column_names, table_list=table_names,
                                      conditions=conditions, group_by_list=group_by_names)

        new_report = CreateReport(id=1,
                                  pipeline_id=self.pipeline_id,
                                  type='auto-generated',
                                  name=periodcity + ' report for ' + metric +
                                  ' based on ' + attrs.split(',')[0].split('.')[-1],
                                  sql_query=query
                                  )
        create_report(new_report, self.db, self.user)

    def create_sqlquery_for_reports(self):
        with open(self.etl_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        attr_dict = collections.defaultdict(list)
        dw = self.dw_name
        clientschema = schema_dict.get("SourceSchema")

        for tName in schema_dict['Tables']:
            if tName.get('type') == 'dim':
                str_list = []
                nonstr_list = []
                count = 0
                for cName in tName['Columns']:

                    if str('varchar').lower() in cName["TargetColumnType"].lower():
                        # attr_dict[str(tName["TargetTable"])].append(cName["TargetColumn"])
                        str_list.append(tName["TargetTable"] + '.' + cName["TargetColumn"])
                        count = +1
                    elif cName["TargetColumn"] != "RBID":
                        nonstr_list.append( tName["TargetTable"] + '.' + cName["TargetColumn"])
                if count > 0:
                    attr_dict[str( tName["TargetTable"])].extend(str_list)
                else:
                    attr_dict[str(tName["TargetTable"])].extend(nonstr_list)

        for tName in schema_dict['Tables']:
            if tName.get('type') == 'fact':
                for cName in tName['Columns']:
                    for keys in cName['ETLKeys']:
                        # print("Metric ",cName["TargetColumn"],
                        # "is associated with this attribut e",keys["FactKey"],"
                        # to be looked up in dim ",keys["LookupDim"]," with the dim key ",keys["DimKey"])

                        # Define the replacement values
                        attrs = ','.join(str(attr_dict[keys.get("LookupDim")]))
                        metric = cName["TargetColumn"]
                        lookupDim = keys.get("LookupDim")
                        # Daily report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Daily')
                        # Monthly report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Monthly')
                        # Yearly report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Yearly')


if __name__ == '__main__':
    datawarehouse = PostGresDatawarehouse('test')
    # datawarehouse.create_database_with_obj()
    datawarehouse.create_time_dimension()
    datawarehouse.populate_time_dim('2023-12-01 11:00', '2023-12-31 11:59')