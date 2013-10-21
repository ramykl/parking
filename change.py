import cv2  
import numpy as np
import sys

# wheellevel1 = 225 cars

debug = True
crop = False
cropHeight = 0  # 0.55 # 0.55 for kinect images
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data
save = False  # flag for saving video
rotate = True  # flag for rotated video

minThresh = 0  # 84
maxThresh = 0  # 90

# Colour thresholds for colours to ignore
min_green = np.array([0, 60, 68], np.uint8)
max_green = np.array([240, 255, 255], np.uint8)
min_white = np.array([0, 0, 200], np.uint8)
max_white = np.array([255, 13, 255], np.uint8)

circleParam2 = 33
circleParam1 = 100
canny_thresh = 45
ratio = 3
kernel_size = 3
h = 0
w = 0
c = 0
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


path = "./videos/"
if save:
    file = 5
    video2 = cv2.VideoWriter(path + 'convert' + str(file) + '.avi', cv2.cv.CV_FOURCC('D', 'I', 'V', 'X'), 20, (1280, 480))
    circ = np.zeros((480, 640, 3), np.uint8)


def process(image, frameCount, similar):
    global last_wheel
    global last_circle
    global wheelCount
    global carCount
    global resetFlag
    global counter
    global wheel
    global wheel2
    hc, wc, cc = np.shape(image)
    cropIm = image[hc * cropHeight:hc, 0:wc]
    
    # colour filter
    hsv = cv2.cvtColor(cropIm, cv2.COLOR_BGR2HSV)
    maskg = cv2.inRange(hsv, min_green, max_green)
    grayIm = cv2.cvtColor(cropIm, cv2.COLOR_BGR2GRAY)
    maskw = cv2.inRange(hsv, min_white, max_white)
    maskg = cv2.bitwise_not(maskg)
    maskw = cv2.bitwise_not(maskw)
    image = grayIm * maskg * maskw
    
    
#     if debug:
#         cv2.imshow('std', cropIm)
#         cv2.imshow('white', maskw)
#         cv2.imshow('green', maskg)
#         cv2.imshow('com', image)
#         cv2.waitKey()
    
    """
    Houghcircles detection 
      
    val, image = cv2.threshold(src, thresh, maxval, type)
    circles = cv2.HoughCircles(image, method, dp, minDist) -->> [[x,y,radius],[...],...]    
    """
    img = cv2.medianBlur(image, 5)
    r, img = cv2.threshold(img, maxThresh, 0, cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)
      
    if debug:    
        cv2.imshow('image', cropIm)
        cv2.imshow('thresh', img)
        cv2.waitKey(1)
      
    cimg = cropIm
    
    if frameCount-last_wheel >= allowedFrames+allowedMiss and wheel2 == True:
        resetFlag = True
        if wheel == True:
            carCount += 1
            seconds = frameCount/20
            print seconds/60,':',seconds%60,carCount
        wheel2 = False
        wheel = False
    
    # find random circle, and clear
    if frameCount - last_circle[3] >= allowedMiss and wheel2 != True:
        if wheel != True:
            resetFlag = True
        else:
            last_wheel = last_circle[3]
            wheel2 = True
            wheel = False
        counter = 0
        
    circles = cv2.HoughCircles(img, cv2.cv.CV_HOUGH_GRADIENT, 1, 400, param1=circleParam1, param2=circleParam2, minRadius=50, maxRadius=200)
    if circles is not None:
        if len(circles[0]) < 2:
            flag = 0
            for i in circles[0, :]:
                if (i[1] < (sec + 80)) and (i[1] > (sec - 80)):
                    flag += 1
                    cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 1)  # draw the outer circle
                    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)  # draw the center of the circle
                    if resetFlag:
                        resetFlag = False
                        counter = 0
                        
                    elif last_circle[0]-allowedX <= i[0] <= last_circle[0]+5:
                        counter += 1
                        
                    last_circle[0] = i[0]
                    last_circle[1] = i[1]
                    last_circle[2] = i[2]
                    last_circle[3] = frameCount
                    
            if flag:
                if debug:    
                    cv2.imshow('detected circles', cimg)
                    cv2.waitKey(1)
                    if save:
                        circ[hc * cropHeight:hc, 0:wc] = cimg

    if save:
        da = np.hstack((image, circ)).astype(np.uint8, copy=False)
        video2.write(da)
        
    if counter >= 2:
        wheel = True
    print counter, wheel, wheel2, carCount

    
def video(stream):
    frameCount = 0
    val, frame = stream.read()
    h, w, c = np.shape(frame)
    similar = 0
    while True:
        if not val:
            break
        if crop:
            frame = frame[0:h, w / 2:w]
        if rotate:
            frame = cv2.flip(frame, -1)
        frameCount += 1
        similar = process(frame, frameCount, similar)
        val, frame = stream.read()
        
    print wheelCount, carCount


def main(inputfile):
    if inputfile[-4:] == '.avi':
        print 'Video'
        stream = cv2.VideoCapture(inputfile)
        video(stream)
    elif inputfile[-4:] == '.jpg':
        print 'Image'
        image = cv2.imread(inputfile)
        process(image, 1)
        

if __name__ == '__main__':
    if(len(sys.argv) is not 2):
        print "Usage: python process.py inputfile[.avi or .jpg] outputfile[.avi or .jpg]"
        sys.exit(1)
    else:
        main(sys.argv[1])
