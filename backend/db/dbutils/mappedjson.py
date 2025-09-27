import json
import os
from configparser import ConfigParser

import constants
from db.dbutils.config import config

# config_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
#                            "userinput.ini")
# db=config(filename=config_file,section='Default')


class MappedJson:
    def __init__(self,
                 source_json_file,
                 data,
                 tenant_id=None):
        self.source_json_file = source_json_file
        self.tenant_id = tenant_id
        self.data = data
        self.output_json_file = os.path.join(os.path.join(
            os.getcwd(), constants.JSON_FILE_PATH), constants.MAPPED_JSON_FILE)

    def generate_mapped_json(self):
        # parser = ConfigParser()
        # parser.read_string("[top]\n" + self.data)
        # params = parser.items("top")
        # db = {}
        # for param in params:
        #     db[param[0]] = param[1]
        #     # print(param[0], param[1])
        db = self.data
        with open(self.source_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        schemaName = schema_dict.get('Table_schema')  # noqa
        # print(db.keys())
        for tName in schema_dict['Tables']:
            # print(tName)
            for cName in tName['Columns']:
                # c = str(tName['TableName'] + '.' + cName['ColumnName'])
                # print(db)
                if tName['TableName'] in db:
                    for db_entry in db[tName['TableName']]:
                        if db_entry['column_name'] == cName['ColumnName']:
                            ctype = db_entry.get('type', '')
                            cdatatype = db_entry.get('datatype', '')
                            clength = db_entry.get('length', '')
                            cName.update({"Type": ctype, "ColumnType": cdatatype, "Length": clength})
        # print(schema_dict)
        schema_list[0] = schema_dict
        out_file = open(self.output_json_file, "w")

        json.dump(schema_list, out_file, indent=6)

        out_file.close()

        return self.output_json_file, schema_list
