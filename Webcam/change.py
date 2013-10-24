import cv2  
import numpy as np
import sys

# wheellevel1 = 225 cars

#Flags for different operations in program
debug = False
crop = False
cropHeight = 0  # 0.55 for kinect images
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data
save = False  # flag for saving video
rotate = False #True  # flag for rotated video

minThresh = 0  # 84
maxThresh = 0  # 90

# Colour thresholds for colours to ignore
min_green = np.array([0, 60, 68], np.uint8)
max_green = np.array([240, 255, 255], np.uint8)
min_white = np.array([0, 0, 200], np.uint8)
max_white = np.array([255, 13, 255], np.uint8)


# parameters for houghcircles
circleParam2 = 33
circleParam1 = 100
canny_thresh = 45
ratio = 3
kernel_size = 3
h = 0
w = 0
c = 0

# parameters for car/wheel classification
sec = 270  # 150
last_circle = [0, 0, 0, 0]
last_wheel = 0
carCount = 0
wheelCount = 0
resetFlag = True
allowedX = 160
allowedFrames = 14
allowedMiss = 3
counter = 0
wheel = False
wheel2 = False
circ = np.zeros((480, 720, 3), np.uint8)


path = "./videos/"
if save:
    file = 1
    video2 = cv2.VideoWriter(path + 'convert' + str(file) + '.avi', cv2.cv.CV_FOURCC('D', 'I', 'V', 'X'), 20, (1280, 480))
    circ = np.zeros((480, 720, 3), np.uint8)


def process(image, frameCount):
    global last_wheel
    global last_circle
    global wheelCount
    global carCount
    global resetFlag
    global counter
    global wheel
    global wheel2
    global circ
    hc, wc, cc = np.shape(image)
    cropIm = image[hc * cropHeight:hc, 0:wc]
    orig = cropIm.copy()
    
    # colour filter for green and white
    hsv = cv2.cvtColor(cropIm, cv2.COLOR_BGR2HSV)
    maskg = cv2.inRange(hsv, min_green, max_green)
    maskw = cv2.inRange(hsv, min_white, max_white)
    maskg = cv2.bitwise_not(maskg)
    maskw = cv2.bitwise_not(maskw)
    grayIm = cv2.cvtColor(cropIm, cv2.COLOR_BGR2GRAY)
    # apply filter over greyscale image
    image = grayIm * maskg * maskw
    
    
    """
    Houghcircles detection 
      
    val, image = cv2.threshold(src, thresh, maxval, type)
    circles = cv2.HoughCircles(image, method, dp, minDist) -->> [[x,y,radius],[...],...]    
    """
    img = cv2.medianBlur(image, 5)
    r, img = cv2.threshold(img, maxThresh, 0, cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)
    
    # display original and thresholded images for debugging purposes
    if debug:    
        cv2.imshow('image', cropIm)
        cv2.imshow('thresh', img)
        cv2.waitKey(1)
      
    cimg = cropIm
    
    # check if second wheel has been found in allowed number of frames
    if frameCount-last_wheel >= allowedFrames+allowedMiss and wheel2 == True:
        resetFlag = True
        if wheel == True:
            carCount += 1
            if save:
                cv2.circle(circ, (10, 10), 5, (0, 0, 255), 5)  # draw the dot for car
        # reset wheel flags and resetFlag
        wheel2 = False
        wheel = False
    
    # check if a wheel has been found in allowed number of frames while a previous wheel hasn't been found
    if frameCount - last_circle[3] >= allowedMiss and wheel2 != True:
        if wheel != True:
            resetFlag = True
        else:
            last_wheel = last_circle[3]
            wheel2 = True
            wheel = False
        counter = 0
    
    # detect circles
    circles = cv2.HoughCircles(img, cv2.cv.CV_HOUGH_GRADIENT, 1, 400, param1=circleParam1, param2=circleParam2, minRadius=50, maxRadius=200)
    if circles is not None:
        # only use circles if there is only 1 detected
        if len(circles[0]) < 2:
            flag = 0
            for i in circles[0, :]:
                # limit useful circle height (y position) by sec +/- 80
                if (i[1] < (sec + 80)) and (i[1] > (sec - 80)):
                    flag += 1
                    
                    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)  # draw the center of the circle
                    # reset count
                    if resetFlag:
                        resetFlag = False
                        counter = 0
                    
                    # check if the x position of the circle is similar to previously detected
                    elif last_circle[0]-allowedX <= i[0] <= last_circle[0]+5:
                        counter += 1
                    
                    # change colour of circle for a wheel vs just circle
                    if counter >= 2:
                        cv2.circle(cimg, (i[0], i[1]), i[2], (255, 0, 0), 1)  # draw the outer circle
                    else:
                        cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 1)  # draw the outer circle
                    
                    # set last circle
                    last_circle[0] = i[0]
                    last_circle[1] = i[1]
                    last_circle[2] = i[2]
                    last_circle[3] = frameCount
            # appropriate circles have been detected
            if flag:
                if debug:    
                    # display detected circle
                    cv2.imshow('detected circles', cimg)
                    cv2.waitKey(1)
                # set circ to the image with the previous circle shown
                if save:
                    circ[hc * cropHeight:hc, 0:wc] = cimg

    # combine current image with the previous found circle image and write to file
    if save:
        da = np.hstack((orig, circ)).astype(np.uint8, copy=False)
        video2.write(da)
        
    # check how many similar circles have been detected
    if counter >= 2:
        # if not already a wheel increment number of detected wheels
        if wheel != True:
            wheelCount += 1    
        wheel = True
    
    if debug:
        print counter, wheel, wheel2, wheelCount, carCount

# runs program for a video
def video(stream):
    frameCount = 0
    # read frame from video
    val, frame = stream.read()
    h, w, c = np.shape(frame)
    while True:
        # break if there are no frames left
        if not val:
            break

        # crop image to h, w
        if crop:
            frame = frame[0:h, w / 2:w]

        # rotate image by 180 degrees
        if rotate:
            frame = cv2.flip(frame, -1)
        
        # increase frame count
        frameCount += 1
        # process frame
        process(frame, frameCount)
        # get new frame
        val, frame = stream.read()
    
    # output number of wheels detected and the number of cars detected
    print wheelCount, carCount


# checks what file type the input is
def main(inputfile):
    if inputfile[-4:] == '.avi':
        print 'Video'
        # creates video stream to get frames
        stream = cv2.VideoCapture(inputfile)
        video(stream)
        
    elif inputfile[-4:] == '.jpg':
        print 'Image'
        image = cv2.imread(inputfile)
        process(image, 1)
        
    else:
        print "unkown file type"
        sys.exit(0)
        

# starts main program and checks input argument
if __name__ == '__main__':
    if(len(sys.argv) is not 2):
        print "Usage: python process.py inputfile[.avi or .jpg]"
        sys.exit(1)
    else:
        main(sys.argv[1])
