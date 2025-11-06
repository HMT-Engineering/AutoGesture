## Todo

Next up take the data from leap motion (hand) and the data from the watch, 
and store it in a file

Then create a mapped input preview and also a mapped object to be used as input for LSTM



## Instructions Video Labeling
- Go to https://vidat2.davidz.cn/#/
- Upload Video
- Download annotations
- Copy annotation.video block from json to template
- run csvToJsonAnnotation.py with path to poses.csv
- Upload annotation json to website and adjust annotations



preprocessAnnotations.py
- Use windows to determine most common gesture
- Prepadd the gesture to get "premovememtns" as well


alignCSVSensorData.py 
- Takes the sensor files, and creates on dataset with all the sensor data