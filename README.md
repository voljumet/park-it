# park-it
Project for the course IKT452  

Park is a system that logs vehicles' license plates in a parking lot. It identifies the cars entering by object detection and tracks them through the frame to check if they are entering or exiting. The system uses object detection to detect the license plate and optical character recognition to extract the text. The information is stored in a data file to keep track of the cars inside the parking lot, and the duration of their stay is calculated when they leave.  

When cloning the repo, use: ```git clone --recurse-submodules git@github.com:voljumet/park-it.git``` to clone the "Yolov5" submodule that is used. 

The project requires a few different packages to run. There is further explanation in both the nobook files below.

The project can be run with the file [Linear](project_demo_linear.ipynb) which will run the project modules in a linear fashion and show the results after each step.  

The project can also be run with the file [Concurrent](project_demo_concurrent.ipynb) which will run the project concurrently to show that the system can handle cars as they come into frame.