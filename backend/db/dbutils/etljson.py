import json
import collections


class EtlJson:
    def __init__(self, mapped_json_file, etl_json_file) -> None:
        self.mapped_json_file = mapped_json_file
        self.etl_json_file = etl_json_file

    def gen_etl_json(self):
        with open(self.mapped_json_file, 'r') as input_file:
            schema_list = json.load(input_file)
        schema_dict = schema_list[0]
        schema_dict['SourceSchema'] = str(schema_dict.get('Table_schema'))
        schema_dict['TargetSchema'] = str(schema_dict.get('Table_schema') + '_DW')
        clientschema = schema_dict.get('Table_schema')

        schema_dict.pop('Table_schema')

        attributes = ['attr']
        metrics = ['mtrc'] # noqa
        factTable = collections.OrderedDict()
        factTable['TargetTable'] = clientschema + str('_fact')
        factTable['type'] = str('fact')
        factTable['Columns'] = []
        for tName in schema_dict['Tables']:

            for cName in tName['Columns']:
                if cName.get('isPrimaryKey') is True:
                    LookupKey = tName['TableName'] + '.' + cName.get('ColumnName') # noqa

                if cName.get('Type') in attributes:
                    # print(cName.get('Type'))
                    cName['SourceColumn'] = cName.get('ColumnName')
                    cName['TargetColumn'] = cName.get('ColumnName')
                    cName['SourceColumnType'] = cName.get('ColumnType')
                    cName['TargetColumnType'] = cName.get('ColumnType')
                    cName.pop('ColumnType')

                    cName.pop('ColumnName')
                    cName.pop('isPrimaryKey')
                    cName.pop('ForeignKey')
                    cName.pop('Type')
                else:
                    if cName.get('Type') and cName.get('Type').startswith('attr'):
                        cName['SourceColumn'] = cName.get('ColumnName')
                        cName['TargetColumn'] = cName.get('ColumnName')
                        cName['SourceColumnType'] = cName.get('ColumnType')
                        cName['TargetColumnType'] = cName.get('ColumnType')
                        cName.pop('ColumnType')
                        cName.pop('ColumnName')
                        cName.pop('isPrimaryKey')
                        cName.pop('ForeignKey')

                        fk_list = []
                        foreign_keys = []
                        foreign_keys = tuple(map(str, cName.get('Type').removeprefix(
                            'attr(').removesuffix(')').split(', ')))
                        # print(len(foreign_keys))
                        for key in foreign_keys:
                            dim = clientschema + '_' + key.split('.')[0]
                            dk = collections.OrderedDict()
                            dk['SourceFkey'] = str(dim + '_dim.RBID')
                            dk['DestFkey'] = str(dim + '_dim_RBFID')
                            dk['TargetJoinColumn'] = key.split('.')[-1]
                            # print(key,dim,dim_key)
                            # key_tuple=key,dim_key
                            fk_list.append(dk)
                        cName['ForeignKey'] = fk_list
                        cName.pop('Type')
                    else:

                        if cName.get('Type') and cName.get('Type').startswith('mtrc'):
                            fact_column = collections.OrderedDict()
                            fact_column['LookupColumn'] = cName.get('ColumnName')
                            fact_column['TargetColumn'] = cName.get('ColumnName')
                            fact_column['LookupTable'] = tName.get('TableName')
                            # fact_column['LookupKey']= LookupKey
                            fact_column['TargetColumnType'] = cName.get('ColumnType')
                            etl_keys = tuple(map(str, cName.get('Type').removeprefix(
                                'mtrc(').split(',timedim', 1)[0].split(',')))
                            # print(len(foreign_keys))
                            lk_list = []
                            for key in etl_keys:
                                lk = collections.OrderedDict()
                                if ('(') in key:
                                    source_keys = tuple(map(str, key.split('(', 1)[0].removesuffix(')').split('.')))
                                    dest_keys = tuple(map(str, key.split('(', 1)[1].removesuffix(')').split('.')))
                                    # print(lk['destLookupKey'])
                                    dim = clientschema + '_' + dest_keys[0]
                                    dim = str(dim + '_dim')
                                    fact_id = str(dim + '_RBID')
                                    lk['LookupDim'] = dim
                                    lk['SourceLookupKey'] = source_keys[1]
                                    lk['DestLookupKey'] = dest_keys[1]
                                    lk['DimKey'] = str('RBID')
                                    lk['FactKey'] = fact_id

                                # if key.startswith('timedim'):
                                #  lk['TimeID']=key.removeprefix('timedim(').removesuffix(')')
                                # lk_list.append(lk)

                                # fact_column['TimeID']=key.removeprefix('timedim(').removesuffix(')')

                                else:
                                    dim = clientschema + '_' + key.split('.')[0]
                                    keyval = key.split('.')[-1]
                                    dim = str(dim + '_dim')
                                    fact_id = str(dim + '_RBID')
                                    lk['LookupDim'] = dim
                                    lk['SourceLookupKey'] = lk['DestLookupKey'] = keyval
                                    lk['DimKey'] = str('RBID')
                                    lk['FactKey'] = fact_id
                            # print(key,dim,dim_key)
                                lk_list.append(lk)
                                fact_column['ETLKeys'] = lk_list
                            # fact_column['ForeignKey']=str(tName['TableName']+'_dim.ID')
                            # fact_column['FactID']=fk_list
                            time_keys = tuple(map(str, cName.get('Type').split(
                                'timedim(', 1)[1].removesuffix('))').split(',')))
                            # tk_list=[]
                            tk = collections.OrderedDict()
                            tk['TimeIDTable'] = ""
                            tk['TimeIDColumn'] = ""
                            tk['TimeIDTargetColumn'] = 'TimeID'
                            tk['TimeIDLookupkey'] = ""

                            for key in time_keys:

                                if key.startswith('lookuptable'):
                                    tk['TimeIDTable'] = key.removeprefix('lookuptable=')
                                elif key.startswith('time'):
                                    tk['TimeIDColumn'] = key.removeprefix('time=')
                                elif key.startswith('lookupkey'):
                                    tk['TimeIDLookupkey'] = key.removeprefix('lookupkey=')

                            # tk_list.append(tk)

                            fact_column['TimeIDs'] = tk

                            factTable['Columns'].append(fact_column)

                        cName.clear()

            tName['Columns'] = list(filter(None, tName['Columns']))

            if not tName['Columns']:
                tName.clear()
            else:
                new_column = collections.OrderedDict()
                new_column['TargetColumn'] = 'RBID'
                new_column['TargetColumnType'] = 'INTEGER'
                new_column['isPrimaryKey'] = 'yes'
                tName['Columns'].append(new_column)

                # tName['TableName']=str(tName["TableName"]+'_dim')
                tName['SourceTable'] = tName.get('TableName')
                tName['TargetTable'] = clientschema + '_' + tName.get('TableName') + '_dim'
                tName['type'] = str('dim')
                tName.pop('TableName')

        schema_dict['Tables'] = list(filter(None, schema_dict['Tables']))
        schema_dict['Tables'].append(factTable)
        # print(schema_dict)
        schema_list[0] = schema_dict
        out_file = open(self.etl_json_file, "w")

        json.dump(schema_list, out_file, indent=6)

        out_file.close()

        return True, schema_list
