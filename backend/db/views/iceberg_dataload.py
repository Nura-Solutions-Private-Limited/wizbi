import boto3
import json
import duckdb

from db.models.models import Source_Db_Mapping


class IcebergDataload:
    def __init__(self, aws_access_key, aws_secret_key, s3_bucket, s3_region):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.glue_client = None

        # create aws glue client
        if self.aws_access_key and self.aws_secret_key and self.s3_region:
            self.glue_client = boto3.client(
                "glue",
                region_name=self.s3_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
            )

    def validate_iceberg_table(self, iceberg_database, iceberg_table):
        try:
            response = self.glue_client.get_table(DatabaseName=iceberg_database, Name=iceberg_table)
        except Exception as e:
            raise Exception(f"Error getting table metadata.json: {str(e)}")
        return {"status": True, "metadata_location": response.get('Table').get('Parameters').get('metadata_location')}

    def get_table_query_selection(self, iceberg_database, iceberg_table, model_mappings):
        for model_mapping in model_mappings:
            if model_mapping.get('database_name') == iceberg_database\
                    and model_mapping.get('table_name') == iceberg_table:
                table_preview = model_mapping.get('table_preview')
                return table_preview[0]
        return None

    def table_previews(self, iceberg_database, iceberg_table, db, user_id, pipeline_id):
        # create duckdb connection with in-memory database
        con = duckdb.connect(database=":memory:", read_only=False)

        # install iceberg extension
        con.install_extension("httpfs")
        con.install_extension("iceberg")

        # load extension
        con.load_extension("httpfs")
        con.load_extension("iceberg")

        # create connection
        con.execute(f"CREATE SECRET (TYPE S3,KEY_ID '{self.aws_access_key}', SECRET '{self.aws_secret_key}', REGION '{self.s3_region}');") # noqa

        # get table metadata.json file
        try:
            response = self.glue_client.get_table(DatabaseName=iceberg_database, Name=iceberg_table)
            col = response.get('Table').get('StorageDescriptor').get('Columns')
            metadata_json = response.get('Table').get('Parameters').get('metadata_location')
        except Exception as e:
            raise Exception(f'Error getting table metadata.json: {str(e)}')

        # get existig table mapping
        source_db_mapping = db.query(Source_Db_Mapping).filter(Source_Db_Mapping.pipeline_id == pipeline_id).first()
        table_preview = None
        if source_db_mapping:
            user_input = source_db_mapping.user_input
            model_mappings = user_input.get('model_mappings')
            table_preview = self.get_table_query_selection(iceberg_database=iceberg_database,
                                                           iceberg_table=iceberg_table,
                                                           model_mappings=model_mappings)

        if response:
            # get table previews
            cur = con.cursor()
            df = cur.execute(f"SELECT * FROM iceberg_scan('{metadata_json}') LIMIT 5;").df()
            result_list = []
            for c in col:
                col_dict = {}
                # col_dict[c.get('Name')] = c.get('Type')
                col_dict['name'] = c.get('Name')
                col_dict['type'] = c.get('Type')

                if table_preview:
                    if c.get('Name') == table_preview.get('name'):
                        if table_preview.get('is_selected') == 'y':
                            col_dict['is_selected'] = True
                        else:
                            col_dict['is_selected'] = False
                    else:
                        col_dict['is_selected'] = False
                else:
                    col_dict['is_selected'] = False

                if table_preview:
                    if c.get('Name') == table_preview.get('name'):
                        if table_preview.get('aggregate_function'):
                            col_dict['aggregate_function'] = table_preview.get('aggregate_function')
                        else:
                            col_dict['aggregate_function'] = None
                    else:
                        col_dict['aggregate_function'] = None
                else:
                    col_dict['aggregate_function'] = None

                if table_preview:
                    if c.get('Name') in table_preview.get('group_by'):
                        col_dict['group_by'] = True
                    else:
                        col_dict['group_by'] = False
                else:
                    col_dict['group_by'] = False
                col_dict['data'] = df[c.get('Name')].to_list()
                result_list.append(col_dict)

            print(json.dumps(result_list, indent=4, default=str))

            cur.close()

        con.close()
        return [{"database_name": iceberg_database, "table_name": iceberg_table, "table_preview": result_list}]

    def load_data(self):
        pass
