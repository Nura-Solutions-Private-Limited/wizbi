# from config import config
import os
import json
import collections

import constants


class DimFactJson:
    def __init__(self, mapped_json_file, tenant_id=None) -> None:
        self.mapped_json_file = mapped_json_file
        self.tenant_id = tenant_id
        self.output_json_file = os.path.join(os.path.join(
            os.getcwd(), constants.JSON_FILE_PATH), constants.DIMFACT_JSON_FILE)

    def generate_dimfact_json(self):
        with open(self.mapped_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        schema_dict['Source_schema'] = str(schema_dict.get('Table_schema'))
        schema_dict['Table_schema'] = str(schema_dict.get('Table_schema') + '_DW')

        attributes = ['attr']
        # metrics = [str.startswith('mtrc')]
        factTable = collections.OrderedDict()
        factTable['TableName'] = schema_dict.get('Source_schema') + str('_fact')
        factTable['Columns'] = []
        for tName in schema_dict['Tables']:
            tName['Source_Table'] = tName.get('TableName')
            for cName in tName['Columns']:

                if cName.get('Type') in attributes:
                    # print(cName.get('Type'))
                    cName.pop('isPrimaryKey')
                    cName.pop('ForeignKey')
                    cName.pop('Type')
                else:
                    if cName.get('Type') and cName.get('Type').startswith('attr'):
                        fk_list = []
                        foreign_keys = []
                        foreign_keys = tuple(map(str, cName.get('Type').removeprefix(
                            'attr(').removesuffix(')').split(', ')))
                        # print(len(foreign_keys))
                        for key in foreign_keys:
                            dim = key.split('.')[0]
                            dim_key = schema_dict.get('Source_schema') + '_' + str(dim + '_dim.RBFID')
                            # print(key,dim,dim_key)
                            # key_tuple=key,dim_key
                            if dim_key not in fk_list:
                                fk_list.append(dim_key)
                        cName['ForeignKey'] = fk_list
                        cName.pop('isPrimaryKey')
                        cName.pop('Type')
                    else:
                        if cName.get('Type') and cName.get('Type').startswith('mtrc'):
                            fact_column = collections.OrderedDict()
                            fact_column['ColumnName'] = cName.get('ColumnName')

                            fact_column['ColumnType'] = cName.get('ColumnType')
                            fk_list = []
                            foreign_keys = []
                            """ foreign_keys = tuple(map(str, cName.get('Type').removeprefix(
                                        'mtrc(').split(',timedim', 1)[0].split(',')))
                            for key in foreign_keys:
                                if not key.startswith('timedim'):
                                    dim = key.split('.')[0]
                                    dim_key = str(dim + '_dim.RBID')
                                # print(key,dim,dim_key) """
                            # key_tuple=key,dim_key
                            foreign_keys = tuple(map(str, cName.get('Type').removeprefix(
                                'mtrc(').split(',timedim', 1)[0].split(',')))
                            # print(len(foreign_keys))
                            fk_list = []
                            for key in foreign_keys:
                                fk = collections.OrderedDict() # noqa
                                if ('(') in key:
                                    # source_keys = tuple(map(str, key.split('(',1)[0].removesuffix(')').split('.')))
                                    dest_keys = tuple(map(str, key.split('(', 1)[1].removesuffix(')').split('.')))
                                    # print(lk['destLookupKey'])
                                    dim = dest_keys[0]
                                    dim_key = schema_dict.get('Source_schema') + '_' + str(dim + '_dim.RBID')

                                    # if key.startswith('timedim'):
                                    #  lk['TimeID']=key.removeprefix('timedim(').removesuffix(')')
                                    # lk_list.append(lk)

                                    # fact_column['TimeID']=key.removeprefix('timedim(').removesuffix(')')

                                else:
                                    dim = key.split('.')[0]

                                    dim_key = schema_dict.get('Source_schema') + '_' + str(dim + '_dim.RBID')

                                    # print(key,dim,dim_key)
                                    # lk_list.append(lk)
                                    # fact_column['ETLKeys'] = lk_list
                                    # fact_column['ForeignKey']=str(tName['TableName']+'_dim.ID')
                                    # fact_column['FactID']=fk_list
                                if dim_key not in fk_list:
                                    fk_list.append(dim_key)
                                fact_column['ForeignKey'] = fk_list
                    # fact_column['ForeignKey']=str(tName['TableName']+'_dim.ID')
                            factTable['Columns'].append(fact_column)
                            cName.clear()

                        else:
                            cName.clear()

            tName['Columns'] = list(filter(None, tName['Columns']))

            if not tName['Columns']:
                tName.clear()
            else:
                new_column = collections.OrderedDict()
                new_column['ColumnName'] = 'RBID'
                new_column['ColumnType'] = 'INTEGER'
                new_column['isPrimaryKey'] = 'yes'
                tName['Columns'].append(new_column)

                tName['TableName'] = schema_dict.get('Source_schema') + '_' + str(tName["TableName"] + '_dim')

        schema_dict['Tables'] = list(filter(None, schema_dict['Tables']))
        schema_dict['Tables'].append(factTable)
        # print(schema_dict)
        schema_list[0] = schema_dict
        out_file = open(self.output_json_file, "w")

        json.dump(schema_list, out_file, indent=6)

        out_file.close()

        return self.output_json_file, schema_list
