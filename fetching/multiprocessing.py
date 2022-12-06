import time
import cv2
import torch

from fetching.fetch_car_functions import fetch_cars
from fetching.detect_license_plate_functions import detect_and_log_cars


def logging_cars():
    """ This function checks the intermediate_ storage CSV file for new cars and logs them."""
    model = torch.hub.load('./yolov5', 'custom', source='local', path='weights/best_submission.pt', force_reload=True)

    while True:
        # sleep for 5 seconds to wait for more data to be added to the CSV file
        time.sleep(5)

        # print clock now
        # print(time.strftime("%H:%M:%S", time.localtime()))

        array_of_cars_found = fetch_cars(required_log_entries_per_car=5, frame_width=3840, delete_cars=True)
        if array_of_cars_found is not None:
            for i, each_car in enumerate(array_of_cars_found):
                # cv2.imwrite('runs/track/exp/car'+str(i)+'.jpg', each_car[1][0])
                detect_and_log_cars(each_car, model)


