import pandas as pd
import numpy as np
import scipy.stats
import csv

# takes in a list of parameters, one for each DUID 
# overwrites the price band csv file to update PBs according to the parameters
def update_capacity_bands(params, duid_capacity, gen_grouping_to_optimize, duid_list, curr_gen_group_params, csv_filename, iteration):

    base = pd.read_csv("D:\Tools and templates\Static Bidding Optimisation\Data_Files\OfferQuantityBase.csv").copy()
    curr = pd.read_csv("D:\PLEXOS Models\Infigen Beta Model\Bids\Jacks Bidding Files\MarkupPoint.csv").copy()
    make_stepped(curr)
    
    output = calculate_capacity_bands(base, curr, params, duid_capacity, gen_grouping_to_optimize, duid_list, csv_filename, iteration)
    make_cummulative(output)
    output.to_csv("D:\PLEXOS Models\Infigen Beta Model\Bids\Jacks Bidding Files\MarkupPoint.csv", index=False)
        
    return update_curr_gen_group_params(params, gen_grouping_to_optimize, curr_gen_group_params) 
    
    
def calculate_capacity_bands(base, curr, parameters, duid_capacity, gen_grouping_to_optimize, duid_list, csv_filename, iteration):
    i = 0
    for gen_grouping in gen_grouping_to_optimize:
        # get the parameters for all the generators in this grouping
        pb2_param = parameters[i]
        voll_param = parameters[i+1]
        spread_param = parameters[i+2]
        i += 3      
        
#         print('{:15}'.format(gen_grouping) + ': [' + '{: f}'.format(pb2_param) + ', ' + '{: f}'.format(voll_param) + ', ' + '{: f}'.format(spread_param) + ']')
        
        with open(csv_filename, 'a', newline='') as csvfile:
            fieldnames = ['Iteration', 'Station', 'PB2_Param', 'VOLL_Param', 'Spread_Param']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'Iteration':iteration, 'Station':gen_grouping, 'PB2_Param':pb2_param, 
                             'VOLL_Param':voll_param, 'Spread_Param':spread_param})
        
        # update capacity bands using the same parameters for each generator in the grouping
        
        for generator in duid_list[gen_grouping]:
            # adjust the PB2 and PB10 capacities
            
            if float(base.loc[base.index[base['Name']==generator], '2']) != 0.0: 
                pb2 = float(base.loc[base.index[base['Name']==generator], '2']) ** (1+pb2_param/2)
            else:
                pb2 = 0.0
                
            if float(base.loc[base.index[base['Name']==generator], '10']) != 0.0:
                pb10 = float(base.loc[base.index[base['Name']==generator], '10']) ** (1+voll_param)
            else:
                pb10 = 0.0
        
            pb2 = max(pb2, 0)
            pb10 = max(pb10, 0)
            
            curr.at[curr.index[curr['Name']==generator], '2'] = pb2 
            curr.at[curr.index[curr['Name']==generator], '10'] = pb10
            total = pb2 + pb10
            
            for j in range(3,10):
                scale = scipy.stats.norm(spread_param, 0.3).pdf((j-6)/4) * 2
                x = base.loc[base.index[base['Name']==generator], str(j)] * scale
                x = max(float(x), 0)
                curr.at[curr.index[curr['Name']==generator], str(j)] = x
                total += x
                
            # scale everything down so that total capacity remains the same
            pb1 = float(base.loc[base.index[base['Name']==generator], '1'])
            scale = (duid_capacity[generator] - pb1) / total
            for j in range(2,11):
                x = curr.loc[curr.index[curr['Name']==generator], str(j)] * scale
                curr.at[curr.index[curr['Name']==generator], str(j)] = float(x)
                
    return curr


def update_curr_gen_group_params(parameters, gen_grouping_to_optimize, curr_gen_group_params):
    i=0
    for gen_grouping in gen_grouping_to_optimize:
        pb2_param = parameters[i]
        voll_param = parameters[i+1]
        spread_param = parameters[i+2]
        i += 3      
        curr_gen_group_params[gen_grouping] = [pb2_param, voll_param, spread_param]
    return curr_gen_group_params


# take a dataframe of pricebands and make the capacity in each PB addative
def make_cummulative(curr):
    for i in range(2, 11):
        curr[str(i)] = curr[str(i)] + curr[str(i-1)]
    return curr


# take a dataframe of cummulative pricebands and make the capacity in each PB not-addative
def make_stepped(curr):
    for i in range(10, 1, -1):
        curr[str(i)] = curr[str(i)] - curr[str(i-1)]
    return curr



