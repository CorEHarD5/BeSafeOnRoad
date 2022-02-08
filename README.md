# **BeSafeOnRoad**

- University of La Laguna, Computer Science
- **Subject:** Intelligent Systems

<br>

## **Index** <!-- omit in toc -->

- [**BeSafeOnRoad**](#besafeonroad)
  - [**Authors**](#authors)
  - [**Description**](#description)
  - [**Requirements**](#requirements)
  - [**Installation**](#installation)
  - [**Program Usage**](#program-usage)
    - [**Processing Image**](#processing-image)
    - [**Processing Video**](#processing-video)
    - [**Processing Camera**](#processing-camera)

<br>

## **Authors**

- Sergio de la Barrera García (alu0100953275@ull.edu.es)
- Francisco Jesús Mendes Gómez (alu0101163970@ull.edu.es)
- Sergio Tabares Hernández (alu0101124896@ull.edu.es)

<br>

## **Description**

This program implements an Artificial Intelligence system capable of detecting pedestrians crossing the road when its traffic light is on red by using the YOLOv5 model, a convolutional neural network for object detection on images.

<br>

## **Requirements**

``` bash
- python3
- opencv-python
- imutils
- numpy
- pillow
- pysimplegui
- shapely
```

<br>

## **Installation**

First of all, you have to clone our repository:

`$ git clone https://github.com/CorEHarD5/BeSafeOnRoad.git` 

Then you must install all the dependencies, it can be simply done by using:

`$ pip install -r requirements.txt` 

<br>

## **Program Usage**

To execute this program you can run the following snippet:

```
  $ cd BeSafeOnRoad/
  $ python3 ./main.py
```

Then it will show you the main window where you can select between several options: image file, video file or camera input

<br>

### **Processing Image**

1. Select the folder where you have the image you want to process, it will show you a list of all image files in that folder.  

![select_image_folder](./readme_images/select_image_folder.jpg)

2. In the showing list, choose the target image and then push the 'Start Checking'  button.

![select_image_file_from_list](./readme_images/select_image_file_from_list.jpg)
![selected_image](./readme_images/selected_image.jpg)
![start_checking](./readme_images/start_checking.jpg)

3. Then you have to select the regions of interest by pushing the 'Select ROIs' button:  

Instructions to select a ROI:  
![instruction](./readme_images/instruction.jpg)

   - In the first pop up window you have to select the crosswalk ROI on the image. Once you have selected the area, press 'S' key to save it.

![select_crosswalk](./readme_images/select_crosswalk.jpg)

   - Then it will pop up a second window where you have to do the same as before, but this time selecting the predestrian traffic light.

![select_traffic_light](./readme_images/select_traffic_light.jpg)

4. It will show you the processed image and a result text.
   
![image_result](./readme_images/image_result.jpg)

At this stage, you can load another image or check the same one again. While executing the program you can end it by pressing the 'Exit' button or by closing the main window. 

<br>

### **Processing Video**

1. Select the folder where you have the video you want to process, it will show you a list of all video files in that folder.  

![main_menu_of_video](./readme_images/main_menu_of_video.jpg)

2. In the showing list, choose the target video and then push the 'Load/Reload Video'  button.  

![selected_video_folder](./readme_images/selected_video_folder.jpg)
![selected_video_file](./readme_images/selected_video_file.jpg)

3. Then you have to select the regions of interest by pushing the 'Select Video ROIs' button:  

![select_video_roi](./readme_images/select_video_roi.jpg)

Instructions to select a ROI:  
![instruction](./readme_images/instruction.jpg)

   - In the first pop up window you have to select the crosswalk ROI on the frame. Once you have selected the area, press 'S' key to save it.

![select_crosswalk_video](./readme_images/select_crosswalk_video.jpg)

   - Then it will pop up a second window where you have to do the same as before, but this time selecting the predestrian traffic light.

![select_traffic_light_roi_video](./readme_images/select_traffic_light_roi_video.jpg)

4. After doing the selection, press the 'Play/Pause Video' button in order to start the video processing.  

![play_video](./readme_images/play_video.jpg)
![result_video_1](./readme_images/result_video_1.jpg)
![result_video_2](./readme_images/result_video_2.jpg)

5. Finally you can choose the frame rate you want by using the slider, pause the video execution or stop it completely.

At this stage, you have several options you can choose:
 - Load another video
 - Reload the current video
 - Select others ROIs

While executing the program you can end it by pressing the 'Exit' button or by closing the main window. 

<br>

### **Processing Camera**

1. In the showing list, choose the target camera and then push the 'Load/Reload Camera'  button.  

![main_camera_menu](./readme_images/main_camera_menu.jpg)
![load_camera](./readme_images/load_camera.jpg)

2. Then you have to select the regions of interest by pushing the 'Select Camera ROIs' button:  

![select_roi_camera](./readme_images/select_roi_camera.jpg)

Instructions to select a ROI:  
![instruction](./readme_images/instruction.jpg)
   - In the first pop up window you have to select the crosswalk ROI on the frame. Once you have selected the area, press 'S' key to save it.

![select_crosswalk_camera](./readme_images/select_crosswalk_camera.jpg)

   - Then it will pop up a second window where you have to do the same as before, but this time selecting the predestrian traffic light.

![select_traffic_light_camera](./readme_images/select_traffic_light_camera.jpg)

3. After doing the selection, press the 'Play/Pause Camera' button in order to start the camera processing.

![play_camera](./readme_images/play_camera.jpg)
![result_camera](./readme_images/result_camera.jpg)

4. Finally you can choose the frame rate you want by using the slider, pause the camera execution or stop it completely.

At this stage, you have several options you can choose:
 - Load another video
 - Reload the current video
 - Select others ROIs

While executing the program you can end it by pressing the 'Exit' button or by closing the main window. 

