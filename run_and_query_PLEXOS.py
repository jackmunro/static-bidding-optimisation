#!/usr/bin/env python
# coding: utf-8

# -*- coding: utf-8 -*-
"""
Connect to a PLEXOS Solution File, load data into pandas DataFrame,
and write an Excel file.
Created on Fri Sep 08 15:03:46 2017
@author: Steven
"""

# standard Python/SciPy libraries
import os
import pandas as pd
from datetime import datetime

# Python .NET interface
from dotnet.seamless import add_assemblies, load_assembly

# load PLEXOS assemblies... replace the path below with the installation
#   installation folder for your PLEXOS installation.
add_assemblies('C:/Program Files (x86)/Energy Exemplar/PLEXOS 8.0/')
# load_assembly('ADODB')
load_assembly('PLEXOS7_NET.Core')
load_assembly('EEUTILITY')

# Import from .NET assemblies (both PLEXOS and system)
from PLEXOS7_NET.Core import *
from EEUTILITY.Enums import *
from System import *

import sys, os, re
from shutil import copyfile
import subprocess as sp


def get_property_id(collection_list, property_list, sol):
    # Takes a list of collections and properties and returns the resulting property id string
    property_ids = []
    for prop in property_list:
        prop_id = str(sol.PropertyName2EnumId(*collection_list, prop))
        property_ids.append(prop_id)
    return ','.join(property_ids)


def write_query_to_df(query_result):
    # Check to see if the query had results
#     print("Writing query to dataframe...")
    if query_result.EOF:
        return None
    idx = 0
    data = []
    while not query_result.EOF:
        data.append([str(x.Value) for x in query_result.Fields])
        idx += 1
        query_result.MoveNext() #VERY IMPORTANT
#         if idx % 1000 == 0: print('querying row: ' + str(idx))
    df = pd.DataFrame.from_records(data, columns=[x.Name for x in query_result.Fields])
    return df


def write_df_to_excel(df, data_file_name):
    # Write the workbook to an excel file
    wb = pd.ExcelWriter(data_file_name)
    df.to_excel(wb) # 'Query' is the name of the worksheet
    wb.save()


# def query_solution_file(collection_list, property_list, sol_file):
#      # Create a PLEXOS solution file object and load the solution
#     sol =  Solution()
#     if not os.path.exists(sol_file):
#         print('No such file')
#         return None
#     sol.Connection(sol_file)
    
#     phase = SimulationPhaseEnum.STSchedule
#     parent = ''
#     child = ''
#     collection = CollectionEnum.SystemRegions    # -> CollectionEnum
#     period = PeriodEnum.Interval                    # -> PeriodEnum
#     series = SeriesTypeEnum.Names                   # -> SeriesTypeEnum
#     props = get_property_id(collection_list, property_list, sol)
#     start_date = '1/10/2018'
#     end_date = '31/12/2018'
    
#     # Simple query: works similarly to PLEXOS Solution Viewer. Returns a ADODB recordset
#     print("Querying solution file...")
#     results = sol.Query(phase, collection, parent, child, period, series, props, start_date, end_date)

#     return write_query_to_df(results)


"""
Below methods written by Jack Munro
They define parameters and call the above methods to run models and query solutions
"""

def run_model():
    # launch the model on the local desktop
    # The \n argument is very important because it allows the PLEXOS engine to terminate after completing the simulation
    plexospath = 'C:/Program Files (x86)/Energy Exemplar/PLEXOS 8.0/'
    filename = 'D:/PLEXOS Models/Infigen Beta Model/DLT Infigen Beta Model_200203 (Jack).xml'
    foldername = 'D:/PLEXOS Models/Infigen Beta Model'
    modelname = 'ST_1830_POE50_cB_2degBudget_r1314 Copy'
    sp.call([os.path.join(plexospath, 'PLEXOS64.exe'), filename, r'\n', r'\o', foldername, r'\m', modelname])

def query_model_prices(start_date, end_date):        
    # Variables to Query
    collection_list = ["System", "Region", "Regions"]
    property_list = ["Price"]
    modelname ='ST_1830_POE50_cB_2degBudget_r1314 Copy'
    foldername = 'D:/PLEXOS Models/Infigen Beta Model/'
    sol_file = foldername + 'Model ' + modelname + ' Solution\Model ' + modelname + ' Solution.zip'
      
     # Create a PLEXOS solution file object and load the solution
    sol =  Solution()
    if not os.path.exists(sol_file):
        print('No such file')
        return None
    sol.Connection(sol_file)
    
    phase = SimulationPhaseEnum.STSchedule
    parent = ''
    child = ''
    collection = CollectionEnum.SystemRegions    # -> CollectionEnum
    period = PeriodEnum.Interval                    # -> PeriodEnum
    series = SeriesTypeEnum.Names                   # -> SeriesTypeEnum
    props = get_property_id(collection_list, property_list, sol)
    
    # Simple query: works similarly to PLEXOS Solution Viewer. Returns a ADODB recordset
    query = sol.Query(phase, collection, parent, child, period, series, props, start_date, end_date)
    result = write_query_to_df(query)

    return result



def query_capacity_factor(start_date, end_date):        
    # Variables to Query
    collection_list = ["System", "Generator", "Generators"]
    property_list = ["Capacity Factor"]
    modelname = 'ST_1830_POE50_cB_2degBudget_r1314 Copy'
    foldername = 'D:/PLEXOS Models/Infigen Beta Model/'
    sol_file = foldername + 'Model ' + modelname + ' Solution\Model ' + modelname + ' Solution.zip'

     # Create a PLEXOS solution file object and load the solution
    sol =  Solution()
    if not os.path.exists(sol_file):
        print('No such file')
    sol.Connection(sol_file)

    phase = SimulationPhaseEnum.STSchedule
    parent = ''
    child = ''
    collection = CollectionEnum.SystemGenerators    # -> CollectionEnum
    period = PeriodEnum.FiscalYear                    # -> PeriodEnum
    series = SeriesTypeEnum.Properties                   # -> SeriesTypeEnum
    props = get_property_id(collection_list, property_list, sol)

    # Simple query: works similarly to PLEXOS Solution Viewer. Returns a ADODB recordset
    query = sol.Query(phase, collection, parent, child, period, series, props, start_date, end_date)
    result = write_query_to_df(query)

    return result



def clear_temp_folder():
    temp_dir = 'C:/Users/Jack.Munro/AppData/Local/Temp/~PLEXOS/'
    # Iterate through all folders in the temp folder
    for folder_name in os.listdir(temp_dir):
        # Delete all files in the folder
        for file_name in os.listdir(temp_dir + folder_name):
            try:
                os.remove(temp_dir + folder_name + '/' + file_name)
            except:
                pass
        # Now delete the folder
        try:
            os.rmdir(temp_dir + folder_name)
        except:
            pass

