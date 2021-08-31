#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import json
import numpy as np
import sys
import os
from datetime import datetime

# class to nicely exit when no conversion excel was added
class StopExecution(Exception):
    def _render_traceback_(self):
        pass


cont = True
# read converstion table
print(''*4)

if len(sys.argv)<2:
    print('Please specify an Excel with mapping and configuration')
    print('e.g.: python conversion.py conversion.xlsx')
    cont = False

if cont == True and not os.path.isfile('./'+sys.argv[1]):
    print(f'{sys.argv[0]} does not exist, please specify an Excel with mapping and configuration')
    print('e.g.: python conversion.py conversion.xlsx')
    cont = False

if not cont:
    print(''*4)
    raise StopExecution

conversion_excel = sys.argv[1] #'conversion.xlsx'

sheet_name='Conversion_Table'
conversion_table = pd.read_excel(conversion_excel, sheet_name=sheet_name, index_col=None)
sheet_name='Key_Table'
key_table = pd.read_excel(conversion_excel, sheet_name=sheet_name, index_col='Key_Old', converters = {'New_Key': str, 'Old_Key': str})
sheet_name='Settings'
settings_table = pd.read_excel(conversion_excel, sheet_name=sheet_name, index_col='Item')

# read settings
source_dir = settings_table.loc['source_dir']['Variable']
converted_dir = settings_table.loc['converted_dir']['Variable']
source_file = settings_table.loc['source_filename']['Variable']
source_separator = settings_table.loc['source_separator']['Variable']
converted_file = settings_table.loc['converted_filename']['Variable']
converted_separator = settings_table.loc['converted_separator']['Variable']

# read data
df = pd.read_csv(source_dir + '/' + source_file, index_col=None)

# ordered list of columns
column_order = []

# go through the conversion table to make the changes
for row in conversion_table.iterrows():
    # reading the necessary variables
    nv = row[1]['New_Variable']
    toc = row[1]['TypeOfConversion']
    mv = row[1]['Map_Variable']
    con = row[1]['Conversion']
    
    # add empty column when not mapped
    
    if mv != mv or mv not in df.columns:
        df[nv] = ''
        column_order.append(nv)
    else:
        # convert the conversion to a dictionary
        if con == con and str(con)[0] =='{':
            res = json.loads(con)

        # convert to lower case just in case of typo
        conversion_type = str(toc).lower()
        # normal variable swapping with value conversion
        if conversion_type == 'normal':
            df = df.rename(columns={mv: nv})
            # convert values if con is not empty
            if con == con:
                # convert dtype of target because dictionary expects a string
                df[nv] = df[nv].astype('string')
                # make sure if a value is missed, that it is visible
                df[nv] = df[nv].map(res).fillna('mapping missing')
            column_order.append(nv)

        if conversion_type == 'check2option' and con == con:
            # create empty list of all the checkbox variables
            subcolumns = []
            for key, value in res.items():
                checkbox = mv + '#' + key
                subcolumns.append(checkbox)
                # assign right value to the checkbox column
                df[checkbox] = df[checkbox].map({1: value})
            # join the checkbox columns into target column
            df[nv] = df[subcolumns].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)
            column_order.append(nv)
            # remmve all the check box columns
            df.drop(subcolumns, axis=1, inplace=True)

        # convesion of options to checkbox format
        if conversion_type == 'option2check' and con == con:
            # convert dtype of target because dictionary expects a string
            df[mv] = df[mv].astype('string')
            # counter is a counter that keeps track of the value to be expected
            counter = 1
            # create the checkbox variable and add the value '1' if applicable
            for key, value in res.items():
                # new checkbox variable
                checkbox = nv + '#' + value
                # add the values of the old variable
                df[checkbox] = df[mv]
                column_order.append(checkbox)
                # add the value '1' if correct, leave empty otherwise
                df[checkbox] = df[checkbox].map({str(counter): '1'}).fillna('')
                counter += 1
            # delete the old column
            del df[mv]

        # adding units
        if conversion_type == 'unit':
            # copy the values
            df[nv] = df[mv]
            column_order.append(nv)
            # add the units when not empty
            if df[nv].dtype == 'O':
                df.loc[df[nv] != '',nv] = con
            else:
                df.loc[df[nv].notnull(),nv] = con
                df[nv].replace(np.nan, '', regex=True, inplace=True)
                
        # replacing keys
        if conversion_type == 'id':
            # copy the values
            df[nv] = df[mv]
            column_order.append(nv)
            # convert key_table into dictionary
            res = key_table.to_dict('dict')
            res = {str(key):str(value) for key, value in res['Key_New'].items()}
            df[nv] = df[nv].astype('string')
            # make sure if a value is missed, that it is visible
            df[nv] = df[nv].map(res).fillna('mapping missing')

df=df[column_order]            


# write converted data
file_name = converted_dir+f'/{datetime.now():%Y%m%d-%H%M%S}_'+converted_file
df.to_csv(file_name+'.csv', sep=converted_separator, index=False)
df.to_excel(file_name+'.xlsx', index=False)

print(''*4)
print(f'Finished, the timestamped output (CSV and Excel) can be found in {converted_dir}')