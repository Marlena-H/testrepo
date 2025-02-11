# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 08:51:52 2025

@author: kftg4
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 13:51:50 2025

@author: maddalen
"""
import netCDF4 as ncdf
import matplotlib.pyplot as plt 
import pandas as pd 
import datetime
import math
import numpy as np

# Assign traffic light colors based on Z-Score thresholds
def traffic_light(z):
    if abs(z) == 0:
        return 'black'
    if abs(z) <= 1:
        return 'green'
    elif 1 < abs(z) <= 2:
        return 'orange'
    else:
        return 'red'

#we love a function
def time_conv(time_val):
    time = datetime.datetime(1990, 1, 1) + datetime.timedelta(days=time_val)
    return time

def select_month(val, df):
    if val[0] == 0:
        return df, "All Months"
    else:
        return df[df['time'].dt.month.isin(val)], val

def get_data(nc, basin):
    
    basin_names = nc.variables["basin_names"][:]
    basin_names = list(basin_names)
    basin_no = basin_names.index(basin)
    print(basin_no)
    mon_mean_thickness = nc.variables["sea_ice_thickness"][basin_no][:]
    time = nc.variables["time"][:]
    
    #Better method? apply along axix didn't work
    time_ts = []
    for i in time:
        i_conv = time_conv(i)
        time_ts += [i_conv]
    
    # time series data in dataframe
    data = {
        'time': time_ts,
        'sea ice thickness': mon_mean_thickness
    }
    
    df = pd.DataFrame(data)
    
    return df

def stat_and_plot(month, df_input, basin):
    
    df, mon_list = select_month(month, df_input)
    
    #better way to do this?
    if mon_list == "All Months":
        str_mon = "All Months"
    else:
        str_mon = []
        for i in mon_list:
            month = datetime.date(1900, i, 1).strftime('%B')
            str_mon += [month]
            if len(str_mon) > 2:
                sentence = ', '.join(str_mon[0:-1]) + f', and {str_mon[-1]}'
            elif len(str_mon) == 2:
                sentence = str(str_mon[0]) + ' and ' + str(str_mon[1])
            else:
                sentence = str(str_mon[0])
                
    arr = df['sea ice thickness']
    zero_els = len(arr) - np.count_nonzero(arr)
    
    mean = df['sea ice thickness'].mean()
    std = df['sea ice thickness'].std()
    df['z_score'] = (df['sea ice thickness'] - mean) / std
    
    df['traffic_light'] = df['z_score'].apply(traffic_light)
        
    # Map colors for visualization
    color_map = {'black': 'black','green': 'green', 'orange': 'orange', 'red': 'red'}
    df['color'] = df['traffic_light'].map(color_map)    
    
    
    if mean == 0 or math.isnan(mean) or zero_els >= 5:
        print("No Data for " + str(basin))   
        
        #plot figure with no data
        plt.figure(figsize=(12, 6))
        plt.title('Traffic Light System for Sea Ice Thickness for ' + str(sentence) + ' in the ' + str(basin))
        plt.text(0.5, 0.5, "No Data for " + str(basin), horizontalalignment='center', verticalalignment='center')
        plt.xlabel('Year')
        plt.ylabel('Sea Ice Thickness (m)')
        plt.show()
        
    else:
        
        # Plot results with traffic light colors
        plt.figure(figsize=(12, 6))
        plt.scatter(df['time'], df['sea ice thickness'], c=df['color'], s=50, zorder=5)
        plt.axhline(mean, color='blue', linestyle='--', label='Mean')
        plt.axhline(mean + std, color='green', linestyle=':', label='1 STD')
        plt.axhline(mean - std, color='green', linestyle=':')
        plt.axhline(mean + 2*std, color='orange', linestyle=':', label='2 STD')
        plt.axhline(mean - 2*std, color='orange', linestyle=':')
        plt.axhline(mean + 3*std, color='red', linestyle=':', label='3 STD')
        plt.axhline(mean - 3*std, color='red', linestyle=':')
        
        plt.title('Traffic Light System for Sea Ice Thickness for ' + str(sentence) + ' in the ' + str(basin))
        plt.xlabel('Year')
        plt.ylabel('Sea Ice Thickness (m)')
        plt.legend()
        plt.show()
    
    return df

def select_basin(basin, month_sets):
    df = get_data(nc, basin)
    
    for item in month_sets:
        stat_and_plot(item, df, basin)
    
    return df

#get_data - loadng from file
path = 'EOCIS-SEAICE-TIMESERIES-THICKVOLMASS-CS2-ARCTIC-201011_202411-fv1.0.nc'
nc = ncdf.Dataset(path)

basin_names = nc.variables["basin_names"][:]
basin_names = list(basin_names)
#Basin names
'''
['Arctic', 'Amerasian Basin', 'Eurasian Basin', 'Canadian Archipelago', 
'Hudson & Foxe Bays', 'Baffin Bay', 'Greenland Sea', 'Iceland Sea', 
'Norwegian Sea', 'Barents Sea', 'White Sea', 'Kara Sea', 
'Siberian Shelf Seas', 'Bering Sea', 'Sea of Okhotsk', 'Baltic Sea & Gulfs', 
'Gulf of St Lawrence & Nova Scotia Peninsular', 'Labrador Sea']
'''
#Input one of the basin names
months = [[3],[10]]
basin = "Kara Sea"

#to plot specific basin
select_basin(basin, months)

#to plot all basin for selected months
'''
for item in basin_names:
    select_basin(item, months)
'''
# Print the dataframe to see classifications
#print(df_all[['time', 'sea ice thickness', 'z_score', 'traffic_light']])