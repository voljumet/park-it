import glob
import csv
import os
import cv2


def load_data():
    """ This function will load the data from the csv file and return the data as a dictionary. """
    data_file = glob.glob('runs/track/exp/tracks/*.csv')
    assert data_file is not None, "The csv file was not loaded!"
    with open(data_file[0], 'r') as f:
        data = list(csv.reader(f))
        f.close()
        return [[float(x) for x in row] for row in data]


def delete_data(all_ids):
    """ This function will delete the data of the cars that are processed."""
    data_file = glob.glob('runs/track/exp/tracks/*.csv')
    assert data_file is not None, "The csv file was not loaded!"
    keep_rows = list()
    with open(data_file[0], 'r') as f:
        data = list(csv.reader(f))
        for row in data:
            if int(float(row[1])) not in all_ids:
                keep_rows.append(row)

    # write the rows that has not been processed, back to the csv file
    with open(data_file[0], 'w') as f:
        writer = csv.writer(f)
        writer.writerows(keep_rows)
    f.close()


def sort_into_dict(data, required_log_entries_per_car):
    """ This function will sort the data into a dictionary with the car id as key, the frame number as the second key, the bounding box and the timestamp as an array. """
    dict = {}
    for each_entry in data:
        frame_number = int(each_entry[0])
        car_id = int(each_entry[1])
        bounding_box_and_time = [each_entry[2:6], each_entry[6]]

        # check if id already exists in dict then append the data to the list with the frame number as key
        if car_id in dict:
            dict[car_id][frame_number] = bounding_box_and_time
        else:
            dict[car_id] = {frame_number: bounding_box_and_time}


    # remove the ids that have less than 5 entries because:
    # they might be cars that are on their way in our out of the frame or just noise
    ids_to_remove = []
    for each_id in dict: 
        if len(dict[each_id]) < required_log_entries_per_car:
            ids_to_remove.append(each_id)

    for each_id in ids_to_remove:
        del dict[each_id]

    return dict


def get_best_license_plate(car_dict, frame_width):
    """ This function will return the three best frames of the car and the direction the car is going. """
    car_entering = False
    sorting_list = []
    
    for frame_number in car_dict:

        size = car_dict[frame_number][0][-1] * car_dict[frame_number][0][-2]
        right_side = car_dict[frame_number][0][0] + car_dict[frame_number][0][2]
        left_side = car_dict[frame_number][0][0]
        
        if (left_side > 5) and (right_side < (frame_width-5)):
            sorting_list.append((frame_number, size))

    # sort the list by bounding box size
    sorting_list.sort(key=lambda x: x[1], reverse=True)

    # check if the biggest frame is the first or last frame, which means the car is entering or leaving the frame
    length_of_sort = len(sorting_list)-1
    if sorting_list[0][0] > sorting_list[length_of_sort][0] and sorting_list[0][0] > sorting_list[int(length_of_sort/2)][0]:
        car_entering = True

    frames_to_return = [x[0] for x in sorting_list[:3]]
    timestamp = car_dict[frames_to_return[0]][1]

    # return boolean if car is entering or leaving the parking lot, the frame numbers of the 3 biggest bounding boxes found, and the timestamp of the last frame
    return car_entering, frames_to_return, timestamp


def load_image(frame_number, bounding_box_array):
    """ This function will load the image of the frame and crop it to the bounding box of the car. """
    # load image
    img = cv2.imread('runs/track/exp/frame id_'+str(frame_number)+'.jpg')
    # crop the image to the size of the bounding box
    img = img[int(bounding_box_array[1]):int(bounding_box_array[1]+bounding_box_array[3]), int(bounding_box_array[0]):int(bounding_box_array[0]+bounding_box_array[2])]
    return img


def get_car_images(car_dict, frame_width):
    """ This function will use the three best frames of the car to load the images and return them in an array together with the direction the car is going. """
    car_array = []
    for car_id in car_dict:
        # get the best license plate for each car
        car_entering, frames, timestamp = get_best_license_plate(car_dict[car_id], frame_width)
        cropped_car_images = []
        for each_frame in frames:
            img = load_image(each_frame, car_dict[car_id][each_frame][0])
            cropped_car_images.append(img)
        
        car_array.append([car_entering, cropped_car_images, timestamp])

    return car_array


def delete_images(car_dictionary):
    """ This function will delete the images of the cars that are processed."""
    
    # TODO: if frame contains multiple cars, do not delete the image
    # frames with multiple cars
    # frames with no cars

    for car_id in car_dictionary:
        for frame in car_dictionary[car_id]:
            os.remove('runs/track/exp/frame id_'+str(frame)+'.jpg')



def fetch_cars(required_log_entries_per_car, frame_width, delete_cars=False):
    """ This function will: load csv file, check how many different cars there are in the file, fetch the three largest bounding boxes for each car, check what direction the car is going, and delete the images and data from the csv that are not needed anymore. """
    # load data from csv file
    # print working directory
    data = load_data()
    if data == None:
        return None
    # sort data into dictionary
    car_dictionary = sort_into_dict(data, required_log_entries_per_car)

    if delete_cars:
        # delete the loaded data from the csv file
        delete_data(list(car_dictionary.keys()))

    # get the 3 best license plate photos for each car and the direction of the car
    car_array = get_car_images(car_dictionary, frame_width)
    
    if delete_cars:
        # delete the images containing the cars extracted
        delete_images(car_dictionary)

    return car_array