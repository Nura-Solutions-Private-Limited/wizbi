import collections
import json
from datetime import datetime

import structlog
from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, text
from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy_utils import create_database, database_exists, get_tables

from db.models.models import Pipeline
from db.views.report import create_report
from schemas.report import CreateReport

logger = structlog.getLogger(__name__)


class MySQLDatabase:
    def __init__(self,
                 pipeline_id,
                 db,
                 user,
                 connection,
                 engine,
                 migrate_json_file,
                 dw_name) -> None:
        self.pipeline_id = pipeline_id
        self.db = db
        self.user = user
        self.connection = connection
        self.engine = engine
        self.migrate_json_file = migrate_json_file
        #self.etl_json_file = etl_json_file
        self.dw_name = dw_name

    def createDW(self, dwName):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        # existing_databases=mycursor.fetchall()
            logger.info("Database schema:-{} created".format(dwName))
        else:
            logger.info("Using the existing data warehouse. \
                        Database schema with name:- {} exits in database".format(dwName))
    def findRefColumnType(self,reftable,refcolumn):
        for tName in self.schema_dict['Tables']:
            if tName['TableName']== reftable :
                for cName in tName['Columns']:
                    if cName['ColumnName']== refcolumn:
                        return (cName['ColumnType'])
   
    
    def addPrimaryKey(self,dW,table,pk_list):
        metadata=MetaData(bind=self.engine)
        metadata.reflect()
        your_table = Table(table, metadata,autoLoad= True)
        if not your_table.primary_key:
            pk_string= ', '.join([f"`{element}`" for element in pk_list])
            self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                            ' ADD CONSTRAINT PRIMARY KEY (' + pk_string + ');')
        
    def createTable(self, dW, table, columnName, columnType, Fkey):
        metadata=MetaData(bind=self.engine)
        metadata.reflect()
        existing_tables = metadata.tables.keys()
        if table in existing_tables:
            logger.info("Altering Table:-{} ".format(table))

            # print("In table ", table)
            your_table = Table(table, metadata,autoLoad= True)

            # print("In table ", table)
            existing_columns =  your_table.columns.keys()
            if columnName not in (existing_columns):
                logger.info("Adding Column:-{} ".format(columnName))

                # print(columnName)
                self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                                        ' ADD `' + columnName + '` ' + columnType + ';')

                #if Pkey:
                    #self.connection.execute('ALTER TABLE ' + dW + '.' + table +
                     #                       ' ADD CONSTRAINT PRIMARY KEY (`' + columnName + '`);')
                    #self.connection.execute('ALTER TABLE ' + dW + '.' + table + ' modify `' +
                    #                        columnName + '` ' + columnType + ' auto_increment ;')
                if Fkey:
                    for key in Fkey:
                        refTable , refKey = key.split('.')
                        refcolumnType=self.findRefColumnType(refTable,refKey)
                        if refTable not in existing_tables:
                        # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                            self.connection.execute('CREATE TABLE `' + dW + '`.`' + refTable +
                                                '` (`'+ refKey+'` '+refcolumnType+' ,PRIMARY KEY (`'+ refKey+'`));') 
                        self.connection.execute('ALTER TABLE `' + dW + '`.`' + table + 
                                                    '` ADD CONSTRAINT  FOREIGN KEY (`' +
                                            columnName+ '`) REFERENCES `' + refTable + '`(`'+refKey+'`);')

        else:
            # print(dW,'blahblah')
            # pdb.set_trace()
            logger.info("Creating Table:-{} ".format(table))

            self.connection.execute('CREATE TABLE ' + dW + '.' + table + ' (`' + columnName + '` ' + columnType + ');')
            #if Pkey:
            #        self.connection.execute('ALTER TABLE ' + dW + '.' + table +
             #                               ' ADD CONSTRAINT PRIMARY KEY (`' + columnName + '`);')
            if Fkey:
                for key in Fkey:
                    refTable , refKey = key.split('.')
                    refcolumnType=self.findRefColumnType(refTable,refKey)

                    if refTable not in existing_tables:
                        # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                         #self.connection.execute('CREATE TABLE `' + dW + '`.`' + refTable +
                          #                      '` (`'+ refKey+'` '+refcolumnType+' ,PRIMARY KEY (`'+ refKey+'`));')
                          # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                         if refTable not in existing_tables:
                        # mycursor.execute('CREATE TABLE '+dW+'.'+refTable+'(ID INT,PRIMARY KEY (ID));')
                            self.connection.execute('CREATE TABLE `' + dW + '`.`' + refTable +
                                                '` (`'+ refKey+'` '+refcolumnType+' ,PRIMARY KEY (`'+ refKey+'`));') 
                    self.connection.execute('ALTER TABLE `' + dW + '`.`' + table + '` ADD CONSTRAINT  FOREIGN KEY (`' +
                                            columnName+ '`) REFERENCES `' + refTable + '`(`'+refKey+'`);')
        # closeConnection(con)
    def create_database_obj(self):
        with open(self.migrate_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        clientschema = schema_dict.get('Source_schema')

        if self.dw_name:
            dWName = self.dw_name
        else:
            schemaName = schema_dict.get('Table_schema')
            dWName = str(schemaName)

        self.createDW(dWName)
        self.schema_dict= schema_dict
        for tName in schema_dict['Tables']:
            for cName in tName['Columns']:
                newTable = tName['TableName']
                self.createTable(dWName, newTable, cName['ColumnName'], cName['ColumnType'], cName.get('ForeignKey'))
            if tName.get('PrimaryKeys'):
                self.addPrimaryKey(dWName,newTable,tName.get('PrimaryKeys'))

if __name__ == '__main__':
    database = MySQLDatabase('test')
    # datawarehouse.create_database_with_obj()
    database.create_database_obj()
