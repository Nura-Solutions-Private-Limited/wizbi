import collections
import json
from datetime import datetime

import structlog
from fastapi import HTTPException, status
from sqlalchemy import MetaData, text
from sqlalchemy_schemadisplay import create_schema_graph

from db.models.models import Pipeline
from db.views.report import create_report
from schemas.report import CreateReport

logger = structlog.getLogger(__name__)


class Datawarehouse:
    def __init__(self,
                 pipeline_id,
                 db,
                 user,
                 connection,
                 raw_connection,
                 dimfact_json_file,
                 etl_json_file,
                 dw_name) -> None:
        self.pipeline_id = pipeline_id
        self.db = db
        self.user = user
        self.connection = connection
        self.raw_connection = raw_connection
        self.dimfact_json_file = dimfact_json_file
        self.etl_json_file = etl_json_file
        self.dw_name = dw_name

    def createDW(self, dwName):
        existing_databases = self.connection.execute("Show DATABASES;").fetchall()
        # existing_databases=mycursor.fetchall()
        existing_databases = [d[0] for d in existing_databases]

        if dwName not in existing_databases:
            self.connection.execute("CREATE DATABASE " + dwName + ";")
            logger.info("Database schema:-{} created".format(dwName))
        else:
            logger.info("Using the existing data warehouse. \
                        Database schema with name:- {} exits in database".format(dwName))
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            # detail="Database schema with name:- {} exits in database".format(dwName))

    def createTimeid(self, dW, table):
        self.connection.execute("USE " + dW + ';')
        # record = self.connection.execute("select database();").fetchone()
        # record = mycursor.fetchone()
        self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                ' ADD COLUMN( TimeID BIGINT not null , load_id BIGINT not null)  ;')

    def createTable(self, dW, table, columnName, columnType, Pkey, Fkey):
        # print(dW," bbbbbbbbbb")
        # con =getConn()
        # mycursor = con.cursor()
        self.connection.execute("USE " + dW + ';')
        # record = self.connection.execute("select database();").fetchone()
        # record = self.connection.fetchone()
        # print("You're connected to database: ", record)

        existing_tables = self.connection.execute('show tables;').fetchall()
        # existing_tables = self.connection.fetchall()

        existing_tables = [d[0] for d in existing_tables]
        """  if Fkey:
            refTable=Fkey.removesuffix('.ID')
            refColumn=Fkey.removeprefix(refTable+'.')
            foreignKey=refTable+'_'+refColumn """
        if table in existing_tables:
            logger.info("Altering Table:-{} ".format(table))

            # print("In table ", table)
            existing_columns = self.connection.execute('desc ' + dW + '.' + table + ';').fetchall()
            # existing_columns = self.connection.fetchall()

            existing_columns = [c[0] for c in existing_columns]
            if columnName not in (existing_columns):
                logger.info("Adding Column:-{} ".format(columnName))

                # print(columnName)
                self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                        ' ADD `' + columnName + '` ' + columnType + ';')

                if Pkey:
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                            ' ADD CONSTRAINT PRIMARY KEY (`' + columnName + '`);')
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' modify `' +
                                            columnName + '` ' + columnType + ' auto_increment ;')
                if Fkey:
                    for key in Fkey:
                        refTable = key.split('.')[0]
                        if refTable not in existing_tables:
                            # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                            self.connection.execute('CREATE TABLE ' + dW + '.' + refTable +
                                                    ' (RBID INT auto_increment,PRIMARY KEY (RBID));')

                        refColumn = key.removeprefix(refTable + '.')
                        foreignKey = refTable + '_' + refColumn
                        if foreignKey not in (existing_columns):
                            self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' ADD `' + foreignKey + '` INT;')
                            self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' ADD CONSTRAINT  FOREIGN KEY (`' +  # noqa
                                                    foreignKey + '`) REFERENCES `' + refTable + '`(RBID);')

        else:
            # print(dW,'blahblah')
            # pdb.set_trace()
            logger.info("Creating Table:-{} ".format(table))

            self.connection.execute('CREATE TABLE ' + dW + '.' + table + ' (`' + columnName + '` ' + columnType + ');')
            if Pkey:
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                            ' ADD CONSTRAINT PRIMARY KEY (`' + columnName + '`);')
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' modify `' +
                                            columnName + '` ' + columnType + ' auto_increment ;')
            if Fkey:
                for key in Fkey:
                    refTable = key.split('.')[0]
                    if refTable not in existing_tables:
                        # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                        self.connection.execute('CREATE TABLE ' + dW + '.' + refTable +
                                                '(RBID INT auto_increment ,PRIMARY KEY (RBID));')

                    refColumn = key.removeprefix(refTable + '.')
                    foreignKey = refTable + '_' + refColumn
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' ADD `' + foreignKey + '` INT;')
                    self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' ADD CONSTRAINT  FOREIGN KEY (`' +
                                            foreignKey + '`) REFERENCES `' + refTable + '`(RBID);')
        # closeConnection(con)

    def drawERdiagram(self, dWName, clientschema):
        graph = create_schema_graph(metadata=MetaData('mysql://root:password@localhost/' + dWName))
        graph.write_png('./' + clientschema + '_DW_erd.png')

    def create_time_dimension(self, dW):
        self.connection.execute("USE " + dW + ';')
        existing_tables = self.connection.execute('show tables;').fetchall()
        # existing_tables = self.connection.fetchall()

        existing_tables = [d[0] for d in existing_tables]
        """  if Fkey:
            refTable=Fkey.removesuffix('.ID')
            refColumn=Fkey.removeprefix(refTable+'.')
            foreignKey=refTable+'_'+refColumn """
        if "time_dim" not in existing_tables:
            time_dim_table_sql = "CREATE TABLE time_dim (time_id BIGINT  NOT NULL, fulltime datetime, "
            time_dim_table_sql = time_dim_table_sql + "day int, month int, year int, hour int, minute int,"
            time_dim_table_sql = time_dim_table_sql + "second int, ampm varchar(2),  PRIMARY KEY(time_id))"
            self.connection.execute(text(time_dim_table_sql))

            sp_text = """
                        CREATE PROCEDURE timedimbuild (IN start_time VARCHAR(16), IN end_time VARCHAR(16) )
                            BEGIN
                                DECLARE v_full_date DATETIME;
                                DELETE FROM time_dim;
                                SET v_full_date = start_time;
                                WHILE v_full_date <= end_time DO
                                    INSERT INTO time_dim (
                                        time_id,
                                        fulltime ,
                                        day,
                                        month,
                                        year,
                                        hour ,
                                        minute ,
                                        second ,
                                        ampm
                                    ) VALUES (
                                        cast(timestamp(v_full_date) as unsigned),
                                        TIMESTAMP(v_full_date),
                                        DAY(v_full_date),
                                        MONTH(v_full_date),
                                        YEAR(v_full_date),
                                        HOUR(v_full_date),
                                        MINUTE(v_full_date),
                                        SECOND(v_full_date),
                                        DATE_FORMAT(v_full_date,'%p')
                                    );
                                    set v_full_date = DATE_ADD(v_full_date, INTERVAL 1 MINUTE);
                                END WHILE;
                            END;
                """
            self.connection.execute(text(sp_text))

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
        # self.drawERdiagram(dWName)
        self.create_time_dimension(dWName)
        self.populate_time_dim(dWName)

    def populate_time_dim(self, dW):
        startDate = datetime.now().date().replace(month=1, day=1)
        endDate = datetime.now().date().replace(month=12, day=31)
        startDate = startDate.strftime('%Y-%m-%d %H:%M')
        endDate = endDate.strftime('%Y-%m-%d 23:59')
        # startDate, endDate = '2023-01-01 00:00','2023-12-31 23:59'
        cursor = self.raw_connection.cursor()
        cursor.execute("USE " + dW + ';')
        # print(startDate)
        # print(endDate)
        cursor.callproc("timedimbuild", [startDate, endDate])
        self.raw_connection.commit()
        cursor.close()

    def time_based_report(self, dw, clientschema, attrs, metric, lookupDim, periodcity):
        query_template = "SELECT {column_list} FROM {table_list} WHERE {conditions} GROUP BY {group_by_list};"
        if periodcity == 'Daily':
            period = 'day'
        elif periodcity == 'Monthly':
            period = 'month'
        else:
            period = 'year'
        # Define the replacement values
        column_names = attrs + " ,sum(" + metric + "), " + dw + ".time_dim." + period
        table_names = dw + "." + str(clientschema) + "_fact fact, " + dw + "." + lookupDim + ", " + dw + ".time_dim"
        conditions = dw + "." + lookupDim + ".RBID = fact." + lookupDim + \
            "_RBID AND round(" + dw + ".time_dim.time_id/100) = round(fact.timeID/100)"
        group_by_names = attrs + ", " + dw + ".time_dim." + period

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
                        str_list.append(str(dw) + '.' + tName["TargetTable"] + '.' + cName["TargetColumn"])
                        count = +1
                    elif cName["TargetColumn"] != "RBID":
                        nonstr_list.append(str(dw) + '.' + tName["TargetTable"] + '.' + cName["TargetColumn"])
                if count > 0:
                    attr_dict[str(dw + '.' + tName["TargetTable"])].extend(str_list)
                else:
                    attr_dict[str(dw + '.' + tName["TargetTable"])].extend(nonstr_list)

        for tName in schema_dict['Tables']:
            if tName.get('type') == 'fact':
                for cName in tName['Columns']:
                    for keys in cName['ETLKeys']:
                        # print("Metric ",cName["TargetColumn"],
                        # "is associated with this attribut e",keys["FactKey"],"
                        # to be looked up in dim ",keys["LookupDim"]," with the dim key ",keys["DimKey"])

                        # Define the replacement values
                        attrs = ','.join(attr_dict[dw + '.' + keys.get("LookupDim")])
                        metric = cName["TargetColumn"]
                        lookupDim = keys.get("LookupDim")
                        # Daily report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Daily')
                        # Monthly report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Monthly')
                        # Yearly report
                        self.time_based_report(dw, clientschema, attrs, metric, lookupDim, 'Yearly')


if __name__ == '__main__':
    datawarehouse = Datawarehouse('test')
    # datawarehouse.create_database_with_obj()
    datawarehouse.create_time_dimension()
    datawarehouse.populate_time_dim('2023-12-01 11:00', '2023-12-31 11:59')