#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import json
import numpy as np
import sys
import os
from datetime import datetime

# functions
def correct_date(a,b):
    '''
    Dates are usually an issue, this function converts certain given formats into ISO8601, %Y-%m-%d format
    '''
    print(f'{a:}, {b:}')
    try:
        a = datetime.strptime(str(a), b)
        return datetime.strftime(a, '%Y-%m-%d')
    except:
        return 'ERR: ' + str(a)

def duration_days(x, con):
    '''
    Duration in days, requires data date fields are in ISO 8601
    '''
    try:
        end = datetime.strptime(x[mv], '%Y-%m-%d')
        start = datetime.strptime(x[con], '%Y-%m-%d')
        return (end-start).days
    except:
        return 'ERR'
    
    
    

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

if cont:
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
    source_variables = df.columns
    
    # keep track of all the variables that are mapped
    mapped_variables = []

    # go through the conversion table to make the changes
    for row in conversion_table.iterrows():
        # reading the necessary variables
        nv = row[1]['New_Variable']
        toc = row[1]['TypeOfConversion']
        mv = row[1]['Map_Variable']
        con = row[1]['Conversion']
        mapped_variables.append(mv)

        # only do stuff when there is a mapping
        if mv == mv:
            # convert the conversion to a dictionary
            if con == con and str(con)[0] =='{':
                res = json.loads(con)

            # convert to lower case just in case of typo
            conversion_type = str(toc).lower()
            
            # swapping the variables
            if conversion_type == 'swap':
                # add nv to mapped_variables otherwise it causes a false negative
                mapped_variables.append(nv)
                # swapping the column names
                df.rename(columns={nv: 'mv', mv: 'nv'}, inplace=True)
                df.rename(columns={'mv': mv, 'nv': nv}, inplace=True)
            
            # converting dates
            if conversion_type == 'date':
                df[nv] = df.apply(lambda x: correct_date(x[mv], con), axis=1)
                                
            # duration in days
            if conversion_type == 'duration':
                df[nv] = df.apply(lambda x: duration_days(x, con), axis=1)
            
            # normal variable swapping with value conversion
            if conversion_type == 'normal':
                df = df.rename(columns={mv: nv})
                # convert values if con is not empty
                if con == con:
                    # convert dtype of target because dictionary expects a string
                    df[nv] = df[nv].astype('string')
                    # make sure if a value is missed, that it is visible
                    df[nv] = df[nv].map(res).fillna('mapping missing')

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
                    # add the value '1' if correct, leave empty otherwise
                    df[checkbox] = df[checkbox].map({str(counter): '1'}).fillna('')
                    counter += 1
                # delete the old column
                del df[mv]

            # adding units
            if conversion_type == 'unit':
                # copy the values
                df[nv] = df[mv]
                # add the units when not empty
                if df[nv].dtype == 'O':
                    df.loc[df[nv] != '',nv] = str(con)
                else:
                    df.loc[df[nv].notnull(),nv] = str(con)
                    df[nv].replace(np.nan, '', regex=True, inplace=True)

            # replacing keys
            if conversion_type == 'id':
                # crelate list with missing keys
                id_set = list(set(df[mv]))
                df_missing_keys = pd.DataFrame({'MissingKeys': [x for x in id_set if x not in list(key_table.index)]})
                # copy the values
                df[nv] = df[mv]
                # convert key_table into dictionary
                res = key_table.to_dict('dict')
                res = {str(key):str(value) for key, value in res['Key_New'].items()}
                df[nv] = df[nv].astype('string')
                # make sure if a value is missed, that it is visible
                df[nv] = df[nv].map(res).fillna('mapping missing')

    # creating list with empty variables
    df_empty = pd.DataFrame({'VarsWithoutValues': [x for x in df.columns if df[x].empty]})

    # creating list with non-maped variables
    df_non_mapped = pd.DataFrame({'NonMappedVars': [x for x in source_variables if x not in mapped_variables]})           
                

    # Setting the correct order, repeating the loop, but easier and more robust to do it here
    # ordered list of columns
    column_order = []
    for row in conversion_table.iterrows():
        # reading the necessary variables
        nv = row[1]['New_Variable']
        toc = row[1]['TypeOfConversion']
        con = row[1]['Conversion']
        conversion_type = str(toc).lower()

        # add missing variables except when conversion_type == option2check
        if nv not in df.columns and conversion_type != 'option2check':
            df[nv] = ''
            column_order.append(nv)

        # add missing variables for conversion_type == option2check, requirement is that there is a mapping
        elif con == con and str(con)[0] =='{' and conversion_type=='option2check':
            res = json.loads(con)
            for key, value in res.items():
                # new checkbox variable
                checkbox = nv + '#' + value
                column_order.append(checkbox)
        # in all other cases add the variable to the list
        else:
            column_order.append(nv)              
                
            
    # sort the dataframe in the correct order            
    df=df[column_order]            


    # write converted data
    file_name = converted_dir+f'/{datetime.now():%Y%m%d-%H%M%S}_'+converted_file
    df.to_csv(file_name+'.csv', sep=converted_separator, index=False)
    df.to_excel(file_name+'.xlsx', index=False)
    file_name = converted_dir + f"/{stamp}_" + converted_file + '_EMPTY'
    df_empty.to_csv(file_name + ".csv", sep=converted_separator, index=False)
    file_name = converted_dir + f"/{stamp}_" + converted_file + '_NON_MAPPED'
    df_non_mapped.to_csv(file_name + ".csv", sep=converted_separator, index=False)
    file_name = converted_dir + f"/{stamp}_" + converted_file + '_MISSING_KEYS'
    df_missing_keys.to_csv(file_name + ".csv", sep=converted_separator, index=False)

    print(''*4)
    print(f'Finished, the timestamped output (CSV and Excel) can be found in {converted_dir}')