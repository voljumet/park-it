import pandas as pd
import csv
import os
from datetime import datetime


def writer(file_to_open, mode, drive_direction_colums_headers, plate_number, clock_time):
    """ this function takes the file name, the mode, the headers and the plate number as arguments, and writes the plate number to the csv file """
    date_time_string = datetime.fromtimestamp(clock_time).strftime('%d/%m/%Y %H:%M:%S')

    with open(file_to_open, mode) as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(drive_direction_colums_headers)
        writer.writerow([plate_number, date_time_string])
        f.close()



def write_to_csv_drive_in(plate_number, time):  
    """ write the plate number to the csv files when a car is etnering the parking lot """ 
    
    # If the header is already written, then don't write it again.
    if not os.path.exists('drive_in.csv'):
        writer('drive_in.csv', 'w', ['Plate Number', 'Date and time'], plate_number, time)
    else:
        writer('drive_in.csv', 'a', None, plate_number, time)

    if not os.path.exists('drive_out.csv'):
        writer('drive_out.csv', 'w', ['Plate Number', 'Drive in time', 'Drive out time', 'Duration'], plate_number, time)
    else:
        writer('drive_out.csv', 'a', None, plate_number, time)



def delete_row_from_csv(_plate_number, file_name):
    """ this function takes the plate number and the file name as arguments, and deletes the row with the plate number from the "drive in" file """
    df = pd.read_csv(file_name+'.csv')
    df = df[df['Plate Number'] != _plate_number]
    df.to_csv('drive_in.csv', index=False)



def write_to_csv_drive_out(plate_number, clock_time):
    """ this function takes the plate number as argument, and writes it to the drive_out.csv file """

    date_time_string = datetime.fromtimestamp(clock_time).strftime('%d/%m/%Y %H:%M:%S')
    #########  get the current date and time####
    # now = datetime.now()
    # dd/mm/YY H:M:S
    # date_time_string = time.strftime("%d/%m/%Y %H:%M:%S")
    #############################################

    # read the csv file
    df = pd.read_csv('drive_out.csv')

    # find the row with the plate number where the drive out time is empty
    assert df['Drive out time'].isnull().sum() == 1, "The car is not in the parking lot"
    row = df.loc[(df['Plate Number'] == plate_number) & (df['Drive out time'].isnull())]

    # get the index of the row
    index = row.index[0]

    # update the drive out time for the plate number
    df.at[index, 'Drive out time'] = date_time_string

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
    # return

