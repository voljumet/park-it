import pandas as pd
import csv
import os
from datetime import datetime


def write_to_csv_drive_in(_plate_number):  
    """ write the plate number to the csv files when a car is etnering the parking lot """ 
    # Headrs for the csv files
    drive_in_colums_headers = ['Plate Number', 'Date and time']
    drive_out_colums_headers = ['Plate Number', 'Drive in time', 'Drive out time', 'Duration']

    # This will change with accual value 
    plate_number = _plate_number

    #########  get the current date and time #######
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    #############################################

    # if the header is already written, then don't write it again. If not, then write it
    if not os.path.exists('drive_in.csv'):
        with open('drive_in.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(drive_in_colums_headers)
            writer.writerow([plate_number,dt_string])
            f.close()
    else:
        with open('drive_in.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([plate_number,dt_string])
            f.close()

    if not os.path.exists('drive_out.csv'):
        with open('drive_out.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(drive_out_colums_headers)
            writer.writerow([plate_number,dt_string])
            f.close()
    else:
        with open('drive_out.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([plate_number,dt_string])
            f.close()
    return



def delete_row_from_csv(_plate_number, file_name):
    """ this function takes the plate number and the file name as arguments, and deletes the row with the plate number from the "drive in" file """
    df = pd.read_csv(file_name+'.csv')
    df = df[df['Plate Number'] != _plate_number]
    df.to_csv('drive_in.csv', index=False)
    return



def write_to_csv_drive_out(_plate_number):
    """ this function takes the plate number as argument, and writes it to the drive_out.csv file """
    # This will change with accual value
    plate_number = _plate_number

    #########  get the current date and time####
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    #############################################

    # read the csv file
    df = pd.read_csv('drive_out.csv')

    # find the row with the plate number where the drive out time is empty
    assert df['Drive out time'].isnull().sum() == 1, "The car is not in the parking lot"
    row = df.loc[(df['Plate Number'] == plate_number) & (df['Drive out time'].isnull())]

    # get the index of the row
    index = row.index[0]

    # update the drive out time for the plate number
    df.at[index, 'Drive out time'] = dt_string

    # calculate the duration
    drive_in_time = df.at[index, 'Drive in time']
    drive_out_time = df.at[index, 'Drive out time']
    drive_in_time = datetime.strptime(drive_in_time, "%d/%m/%Y %H:%M:%S")
    drive_out_time = datetime.strptime(drive_out_time, "%d/%m/%Y %H:%M:%S")
    duration = drive_out_time - drive_in_time

    # update the duration
    df.at[index, 'Duration'] = duration

    # Drop the row with the plate number from the drive_in.csv file
    delete_row_from_csv(plate_number, 'drive_in')

    # save the updated csv file
    df.to_csv('drive_out.csv', index=False)

    # print the updated csv file
    print(df)
    return

