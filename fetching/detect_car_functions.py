import easyocr
import cv2
import numpy as np
import pytesseract
import torch

from fetching.data_handling_functions import *

# ------------------------- license plates detection --------------------------------
# DEFINING GLOBAL VARIABLE
EASY_OCR = easyocr.Reader(['en'])  # initiating easyocr
OCR_TH = 0.2

# Global Variables for text regecnitioin
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

def detectx(frame, model):
    """ function to run detection on a single frame """
    frame = [frame]
    results = model(frame)
    labels, cordinates = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
    return labels, cordinates



def recognize_plate_easyocr(img, coords, reader, region_threshold):
    """ function to recognize license plate numbers using Tesseract OCR """
    
    # separate coordinates from box
    xmin, ymin, xmax, ymax = coords
    # get the subimage that makes up the bounded region and take an additional 5 pixels on each side
    #nplate = img[int(ymin)+15:int(ymax)-5, int(xmin)+12:int(xmax)-12]
    # cropping the number plate from the whole image

    nplate = img[int(ymin):int(ymax), int(xmin):int(xmax)]
    # delete the left side with 10 px of the image
    nplate = nplate[:, 35:]

    # convert nplate to gray
    nplate = cv2.cvtColor(nplate, cv2.COLOR_BGR2GRAY)
    #display(Image.fromarray(nplate))
    
    scale_factor = 6
    scaled_img = cv2.resize(nplate[1:50, 0:SCREEN_WIDTH], (0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    assert(scaled_img is not None)
    #display(Image.fromarray(scaled_img))

    thres,thres_img = cv2.threshold(nplate, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    assert(thres_img is not None)
    #display(Image.fromarray(thres_img))

    ############################ Using Pytesseract to extract text from image ########################################
    text_1 = pytesseract.image_to_string(thres_img, config='--user-words words.txt config.txt')
    print('Text prediciton using Pytesseract:"{}"'.format(text_1)) 
    #############################################################################################################

    ####################################### using EasyORC to extract text ###############################################################
    ocr_result = reader.readtext(nplate)
    text = filter_text(region=nplate, ocr_result=ocr_result,
                        region_threshold=region_threshold)
    if len(text) == 1:
        text = text[0].upper()
        print("Text prediction using EasyOCR: ", text)
        return text
    else:
        return None



def plot_boxes(results, frame, classes):
    """
    --> This function takes results, frame and classes
    --> results: contains labels and coordinates predicted by model on the given frame
    --> classes: contains the string labels
    """
    labels, cord = results
    n = len(labels)
    x_shape, y_shape = frame.shape[1], frame.shape[0]

    # looping through the detections
    for i in range(n):
        row = cord[i]
        if row[4] >= 0.55:  # threshold value for detection. We are discarding everything below this value
            x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(
                row[2]*x_shape), int(row[3]*y_shape)  # BBOx coordniates
            coords = [x1, y1, x2, y2]
            plate_num = recognize_plate_easyocr(
                img=frame, coords=coords, reader=EASY_OCR, region_threshold=OCR_TH)
            return plate_num



def filter_text(region, ocr_result, region_threshold):
    """ to filter out wrong detections """
    rectangle_size = region.shape[0]*region.shape[1]

    plate = []
    for result in ocr_result:
        length = np.sum(np.subtract(result[0][1], result[0][0]))
        height = np.sum(np.subtract(result[0][2], result[0][1]))

        if length*height / rectangle_size > region_threshold:
            plate.append(result[1])
            
    return plate



def license_plate_to_text(image):
    """ this function uses an image as argument, and returns the text that it extracted from the image """
    model = torch.hub.load('./yolov5', 'custom', source='local',
                           path='weights/best_submission.pt', force_reload=True)  # The repo is stored locally

    classes = model.names  # class names in string format
    # --------------- for detection on image --------------------

    results = detectx(image, model=model)  # DETECTION HAPPENING HERE

    frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    plate_num = plot_boxes(results, frame, classes=classes)
   
    return plate_num



def filter_plate_text(strings):
    """ this function takes a list of strings as argument, and returns the string that contains the license plate number """
    result = []
    for i in range(0, len(strings[0])):
        if strings[0][i] == strings[1][i] or strings[0][i] == strings[2][i]:
            result.append(strings[0][i])
        elif strings[1][i] == strings[2][i]:
            result.append(strings[1][i])
    # merge the list to a string
    result = "".join(result)
    return result



def detect_and_log_cars(car_array):
    """ this function takes a car as argument (bool, [img1,img2,img3]), converts license palte to text and writes this to files """
    drive_in = car_array[0]
    images = car_array[1]
    output = []
    # loop through the three images
    for i in range(3):
        # print "working with image number: ", i
        # call the main function
        plate_num = license_plate_to_text(images[i])
        # remve the space in the plate number
        plate_num = plate_num.replace(" ", "")
        # save the output to a list
        output.append(plate_num)
    
    detected_license_plate = filter_plate_text(output)
    print("detected_license_plate: ", detected_license_plate)

    if drive_in:
        print(f"the car with licence palte {detected_license_plate} driving in")
        write_to_csv_drive_in(detected_license_plate)
    else:
        print(f"the car with licence palte {detected_license_plate} driving out")
        write_to_csv_drive_out(detected_license_plate)
