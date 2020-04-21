#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math
import update_capacity_bands
from update_capacity_bands import update_capacity_bands
get_ipython().run_line_magic('matplotlib', 'inline')


# LOSS function using the difference in the sqrt of the prices
def loss_factor(price_curve, region, results, pd_curve_limits, use_sqrt_price, print_curve):
    colors={'NSW':'tab:orange', 'QLD':'tab:green','SA':'tab:red','VIC':'tab:purple','TAS':'tab:cyan'}
    actual = price_curve[region]
    model = results[region + '1']
    model = model.apply(lambda x: max(float(x),1))
    model = model.sort_values(ascending=False)
    
    if use_sqrt_price:
        model = model.apply(lambda x: math.sqrt(x))
        actual = actual.apply(lambda x: math.sqrt(max(float(x),1)))
        
    model = model.reset_index(drop=True)
    df = pd.DataFrame({'Actual':actual,'Model':model})
    
    lower_lim = pd_curve_limits[0]
    upper_lim = pd_curve_limits[1]
    df = df.iloc[lower_lim:upper_lim]        
    
    if print_curve:
        plt.figure(figsize=(12,7))
        plt.title(region)
        plt.plot(df['Actual'], 'tab:blue', df['Model'], colors[region])
        plt.show()
    
    df['Error'] = abs(df['Actual'] - df['Model'])
    loss = df['Error'].sum()
    
    return loss
    
    
    
    
# LOSS function using the difference in the sqrt of the prices
def loss_factor_DUID_CF(gen_cap_factors, plexos_cf, duid_details, regions, print_curve):
    loss = 0
    cfs_actual = []
    cfs_plexos = []
    duids = []
        
    # get all the DUIDs of the region
    plexos_duids = plexos_cf['child_name'].to_list()
    for index, row in duid_details.iterrows():
        if row['Region'] in regions and row['DUID'] in plexos_duids:
            if row['FuelType'] != 'Hydro':
                duids.append(row['DUID'])
    
    for duid in duids:
        cf_actual = float(gen_cap_factors[duid]) * 100
        cf_plexos = float(plexos_cf.loc[plexos_cf.index[plexos_cf['child_name']==duid], "Capacity Factor (%)"])
        cfs_actual.append(cf_actual)
        cfs_plexos.append(cf_plexos)
        loss += (cf_actual - cf_plexos) ** 2

    if print_curve:
        df = pd.DataFrame({'DUIDs':duids, 'Actual':cfs_actual,'PLEXOS':cfs_plexos})    
        df = df.sort_values(by=['Actual'], ascending=False)
        df.to_csv("D:\Tools and templates\Static Bidding Optimisation\Output\Capacity_Factors_" + "_".join(regions) + ".csv", index=False)   
        plt.figure(figsize=(12, 6))
        plt.title('Capacity Factor by DUID')
        plt.plot(df['DUIDs'], df['Actual'], 'tab:blue')
        plt.plot(df['DUIDs'], df['PLEXOS'], 'tab:orange')
        plt.legend(('Actual', 'PLEXOS'))
        plt.xticks(rotation=90)
        plt.show()

    return loss / len(duids) * 300 * len(regions)

    
def callback(x):
    pass


