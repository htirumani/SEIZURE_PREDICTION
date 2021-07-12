from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
from pprint import pprint
from matplotlib import pyplot as plt
import os

'''
Given a clean dataframe FROM A SINGLE USER, returns a list of tuples
containing start and end times of contiguous chunks of data.
'''
def get_contiguous_chunks(df):
    # get data sorted by date
    sdf = df.sort_values('DATE', ascending=True)
    ixs = np.array(list(range(sdf.shape[0])))
    sdf.set_index(ixs, inplace = True)

    tups = []
    s = sdf.at[0, 'DATE']
    p = sdf.at[0, 'DATE']
    l = 0
    delta = timedelta(minutes = 1)
    for index, row in sdf.iterrows():
        if index == 0: continue

        c = row['DATE']
        if c != p+delta:
            tups.append( (s, p, l) )
            s = c
            l = 0
        else:
            l += 1
        p = c
    tups.append( (s, p, l) )

    return tups

'''
0 for 9am-9pm, 1 else
'''
def append_nighttime_feature(df):
    times = df['DATE'].to_list()
    hours = [int(t.hour < 9 or t.hour > 21) for t in times]

    df['NIGHTTIME'] = hours

'''
1 for Monday - Friday, 0 for Saturday - Sunday
'''

def append_weekday_feature(df):
    times = df['DATE'].to_list()
    days = []
    for time in times:
        time = time[:-9]
        if datetime.datetime.strptime(time, '%Y-%m-%d').weekday():
            days.append(1)
        else: days.append(0)
    modded = df.assign(WEEKDAY=days)
    df = modded

'''
minute-by-minute running total that turns over at 4am
'''
def append_activity_feature(df):
    steps = df['STEP'].to_list()
    times = df['DATE'].to_list()
    sum = 0
    minutes_since_reset = 0
    activity = []
    for step, time in zip(steps, times):
        time = time[:-3]
        new_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
        if (new_time.hour == 4 and new_time.minute == 0) or (minutes_since_reset > 1440):
            sum = 0
            minutes_since_reset = 0
        else: 
            sum += step
            minutes_since_reset += 1
        activity.append(sum)
    df = df.assign(ACTIVITY=activity)

'''
how many minutes of sleep in the past 24 hrs
'''

def append_previous_sleep_feature(df):
    sleep = df['SLEEP'].tolist()
    mins_of_sleep = 0
    minutes_since_reset = 0
    previous_sleep = []
    for s in sleep:
        if(minutes_since_reset > 1440):
            minutes_since_reset = 0
            mins_of_sleep = 0
        elif (s == 1):
            mins_of_sleep += 1
        minutes_since_reset += 1
        previous_sleep.append(mins_of_sleep)
    df = df.assign(PSLEEP=previous_sleep)
    
'''
appends both MEAN_{}MIN_HR and SD_{}MIN_HR
corresponding to mean and sd of HR data for previous 'window' minutes

note: requires the omittion of rows without 'window' minutes of data
immediately preceding them
'''
def append_historical_hr_features(df, window):
    mean_label = 'MEAN_{}MIN_HR'.format(window)
    sd_label = 'SD_{}MIN_HR'.format(window)
    
    df.sort_values('DATE', ascending=True, inplace=True)
    ixs = np.array(list(range(df.shape[0])))
    df.set_index(ixs, inplace = True)

    df[mean_label] = None
    df[sd_label] = None

    for index, row in df.iterrows():
        
        # attempt to get row's preceding HR values
        hist = []
        punt = False
        for m in range(1, window+1):
            if punt: break

            if index - m < 0: 
                punt = True
                continue

            curr = df.at[index-m, 'DATE']
            if curr != row['DATE'] - timedelta(minutes=m): 
                punt = True
                continue

            hist.append(df.at[index-m, 'HEART'])
        
        # append mean and sd of hist if all data is collected
        if not punt:
            df.at[index, mean_label] = np.mean(hist)
            df.at[index, sd_label] = np.std(hist)
        
    df.dropna(inplace=True)

'''
Appends the sum of the previous 'window' minutes of steps to each row.

Rows missing from the immediate history are assumed 0 values.
'''
def append_historical_step_feature(df, window):
    label = '{}MIN_STEP_SUM'.format(window)
    
    df.sort_values('DATE', ascending=True, inplace=True)
    ixs = np.array(list(range(df.shape[0])))
    df.set_index(ixs, inplace = True)

    df[mean_label] = None
    df[sd_label] = None

    for index, row in df.iterrows():
        
        # attempt to get row's preceding HR values
        hist = []
        punt = False
        for m in range(1, window+1):
            if punt: break

            if index - m < 0: 
                punt = True
                continue

            curr = df.at[index-m, 'DATE']
            if curr != row['DATE'] - timedelta(minutes=m): 
                punt = True
                continue

            hist.append(df.at[index-m, 'HEART'])
        
        # append mean and sd of hist if all data is collected
        if not punt:
            df.at[index, mean_label] = np.mean(hist)
            df.at[index, sd_label] = np.std(hist)
        
    df.dropna(inplace=True)

'''
Takes a list of filepaths, appends extracted features from the data in those files, saves new data to files in 'final' folder.

fps: list of data files on which to append features
users: list of user indexes corresponding to files in fps
combine_filename: if not none, appends all user's processed data to a file 'combined_filename'
validation: should the processed files go into the validation folder
nighttime...historical_hr: boolean on whether to include said feature
historical_hr_window: window argument for historical hr feature
'''
def append_and_write(fps, users, combine_filename = None, validation = False, activity = False, nighttime = False, historical_hr = False, historical_hr_window = None):
    all_dfs = []
    for path, user in zip(fps, users):
        print('Processing user', user)
        df = pd.read_csv(path)

        if nighttime:
            print('Appending nighttime...')
            append_nighttime_feature(df)
        if historical_hr:
            print('Appending historical HR...')
            append_historical_hr_features(df, historical_hr_window)
        if activity:
            print('Appending activity...')
            append_activity_feature(df)

        print('Writing data...')
        if validation:
            df.to_csv('Data Analysis/Dataset/final/validation/user{}_featured.csv'.format(user))
        else:
            df.to_csv('Data Analysis/Dataset/final/user{}_featured.csv'.format(user))

        if combine_filename != None: all_dfs.append(df)
    
    if combine_filename != None:
        all_df = pd.concat(all_dfs)
        all_df.to_csv('Data Analysis/Dataset/final/combined/' + combine_filename)

    print('Done')

def main():
    data_path = 'Data Analysis/Dataset/clean/'
    fps = os.listdir(data_path)
    fps.remove('all_clean.csv')
    users = [int(u[4:-10]) for u in fps]

    val_fps = ['user4020332650_clean.csv', 'user6775888955_clean.csv']
    val_users = [int(u[4:-10]) for u in val_fps]

    for fp in val_fps: fps.remove(fp)
    for u in val_users: users.remove(u)

    fps = [data_path + fp for fp in fps]
    val_fps = [data_path + fp for fp in val_fps]

    append_and_write(fps, users, combine_filename='all_featured.csv', activity=True)
    append_and_write(val_fps, val_users, combine_filename='validation_featured.csv', validation=True, activity=True)

if __name__ == '__main__':
    main()
