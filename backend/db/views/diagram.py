import os
import time
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData, sql
import json
import constants
import collections


class Diagram:
    def __init__(self,
                 engine,
                 schema,
                 db_type,
                 type) -> None:
        self.engine = engine
        self.schema = schema
        if db_type == 'sqlserver' or db_type == 'mysql':
            self.metadata = MetaData(bind=engine, schema=schema)
        else:
            self.metadata = MetaData(bind=engine)
        if type:
            self.type = type
        self.er_diagram_file = None

    def generate_diagram(self):
        self.er_diagram_file = os.path.join(os.path.join(os.getcwd(),
                                                         constants.IMAGE_FILE_PATH),
                                            constants.ER_DIAGRAM_SUFFIX)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.er_diagram_file = self.er_diagram_file + timestr + '.png'

        graph = create_schema_graph(metadata=self.metadata)
        graph.write_png(self.er_diagram_file)

        return self.er_diagram_file

    def generate_diagram_json(self):
        '''
        function to generate json
        '''
        if self.type == 'source':
            json_file = os.path.join(os.path.join(os.getcwd(),
                                                  constants.IMAGE_FILE_PATH),
                                     constants.SOURCE_DIAGRAM_JSON)
        elif self.type == 'dest':
            json_file = os.path.join(os.path.join(os.getcwd(),
                                                  constants.IMAGE_FILE_PATH),
                                     constants.DEST_DIAGRAM_JSON)

        self.metadata.reflect()
        schema_list = []
        headr = collections.OrderedDict()

        # headr['dbytype']=engine
        headr['Table_schema'] = self.schema

        # print("Metabdata %s", metadata_obj.tables)

        # print("######## before keys ##########")
        table_list = []
        for table in self.metadata.tables:
            # print("######## key start##########")
            table_dict = collections.OrderedDict()
            table_dict['TableName'] = table.removeprefix(str(self.schema + '.'))
            # table_dict['TableName']=table
            tablewithcols = self.metadata.tables[table]
            col_list = []
            for col in tablewithcols.columns:
                col_dict = collections.OrderedDict()
                col_dict['ColumnName'] = col.name
                col_dict['ColumnType'] = str(col.type)
                col_dict['isPrimaryKey'] = col.primary_key
                fk_list = []
                for key in col.foreign_keys:
                    # fk_dict=collections.OrderedDict()
                    # fk_dict['ForeignKeyFrom']=key.target_fullname
                    fk_list.append(key.target_fullname)
                    # col_dict['Constraints']= col.constraints
                col_dict['ForeignKey'] = fk_list
                # print("columntype is ",col.type)

                col_list.append(col_dict)
                if isinstance(col.type, sql.sqltypes.NullType):
                    col_dict.clear()
                    col_list.pop()

            table_dict['Columns'] = col_list
            table_list.append(table_dict)
        headr['Tables'] = table_list
        schema_list.append(headr)
        # print(schema_list)
        out_file = open(json_file, "w")

        json.dump(schema_list, out_file, indent=6)

        out_file.close()

        return json_file
