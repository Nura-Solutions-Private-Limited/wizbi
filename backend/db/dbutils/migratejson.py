import json
import os
from configparser import ConfigParser

import constants
from db.dbutils.config import config

# config_file = os.path.join(os.path.join(os.getcwd(), constants.JSON_FILE_PATH),
#                            "userinput.ini")
# db=config(filename=config_file,section='Default')


class MigrateJson:
    def __init__(self,
                 source_json_file,
                 data,
                 tenant_id=None):
        self.source_json_file = source_json_file
        self.tenant_id = tenant_id
        self.data = data
        self.output_json_file = os.path.join(os.path.join(
            os.getcwd(), constants.JSON_FILE_PATH), constants.MIGRATE_JSON_FILE)

    def generate_migration_json(self):
        # parser = ConfigParser()
        # parser.read_string("[top]\n" + self.data)
        # params = parser.items("top")
        # db = {}
        # for param in params:
        #     db[param[0]] = param[1]
        #     # print(param[0], param[1])
        db = self.data
        

        print(db)
        with open(self.source_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        
        schemaName = schema_dict.get('Table_schema')  # noqa
       
    # Extract relevant information from the second file
        included_tables = [table for table_info in db for table in table_info.keys()]
        included_columns = {table: table_info[table] for table_info in db for table in table_info.keys()}

        # Filter tables and columns from the first file based on the second file
        filtered_data = []
        # Extract information from the second file
        table_info_from_file2 = schema_list[0]["Tables"]

        # Merge information from the two files
        merged_data = []
        table_data=[]
        table_dict={}
        for table_info1 in db:
            table_name = list(table_info1.keys())[0]
            columns_from_file1 = table_info1[table_name]

            # Find corresponding information in the second file
            matching_table_info = next(
                (table_info for table_info in table_info_from_file2 if table_info["TableName"] == table_name), None)

            if matching_table_info:
                # Extract relevant information from the second file
                index_column = matching_table_info.get("index_column")
                index_column_dtype = matching_table_info.get("index_column_dtype")

                # Extract primary keys from the second file
                primary_keys = [col["ColumnName"] for col in matching_table_info["Columns"] if col["isPrimaryKey"]]
                
                # Merge information
                merged_table_info = {
                    "TableName": table_name,
                    "Columns": columns_from_file1,
                    "index_column": index_column,
                    "index_column_dtype": index_column_dtype,
                    "PrimaryKeys": primary_keys
                }
                if not primary_keys:
                    merged_table_info.pop("PrimaryKeys")
                # Add the merged information to the result
                table_data.append(merged_table_info)
        
        table_dict["Table_schema"]=schemaName
        table_dict["Tables"]=table_data
        merged_data.append(table_dict)

        out_file = open(self.output_json_file, "w") 

        json.dump(merged_data, out_file, indent=6)

        out_file.close()

        return self.output_json_file, schema_list
