import cv2  
import numpy as np
import sys

# noise.py from capral-ocr
# http://opencvpython.blogspot.com.au/2012/06/contours-2-brotherhood.html

debug = True
crop = False
cropHeight = 0  # 0.55 # 0.55 for kinect images
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data
save = False  # flag for saving video
rotate = True  # flag for rotated video

minThresh = 0 # 84
maxThresh = 0 # 90

circleParam2 = 33
circleParam1 = 100
canny_thresh = 45
ratio = 3
kernel_size = 3
h = 0
w = 0
c = 0
sec = 270 # 150

last_circle = [0, 0, 0, 0]
last_wheel = [0, 0, 0, 0]
carCount = 0
wheelCount = 0
resetFlag = 1
allowedX = 20
allowedFrames = 5
allowedMiss = 2
counter = 4

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
    hc, wc, cc = np.shape(image)
    cropIm = image[hc * cropHeight:hc, 0:wc]
#     if debug:
#         cv2.imshow('original', image)
# #         cv2.waitKey(1)
        
    grayIm = cv2.cvtColor(cropIm, cv2.COLOR_BGR2GRAY)
#     if debug:    
#         cv2.imshow('Gray',grayIm)
#         cv2.waitKey(10)
    
    """
    Houghcircles detection 
    
    val, image = cv2.threshold(src, thresh, maxval, type)
    circles = cv2.HoughCircles(image, method, dp, minDist) -->> [[x,y,radius],[...],...]    
    """
    img = cv2.medianBlur(grayIm, 5)
    r, img = cv2.threshold(img, maxThresh, 0, cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)
    
    if debug:    
        cv2.imshow('thresh', img)
        cv2.waitKey(1)
    
    cimg = cropIm

    if frameCount - last_circle[3] > allowedFrames:
        resetFlag = 1
        similar = 0
#         counter = 2
#         print 'reset'
    
    if counter >= allowedMiss:
        similar = 0
            
    circles = cv2.HoughCircles(img, cv2.cv.CV_HOUGH_GRADIENT, 1, 400, param1=circleParam1, param2=circleParam2, minRadius=50, maxRadius=200)
    if circles is not None:
        if len(circles[0]) < 2:
            flag = 0
            for i in circles[0, :]:
                if (i[1] < (sec + 80)) and (i[1] > (sec - 80)):
                    flag += 1
                    cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 1)  # draw the outer circle
                    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)  # draw the center of the circle
                    
                    if resetFlag == 0:
                        print "xpos:", i[0], last_circle[0], last_wheel[0]
                        print "ypos:", i[1], last_circle[1], last_wheel[1]
                        if ((last_circle[0]-allowedX) <= i[0] <= last_circle[0]):
                            if counter <allowedMiss:
                                if ((last_wheel[0]-allowedX) <= last_circle[0] <= last_wheel[0]):
                                    similar = 1
                            last_wheel = last_circle[:]
                            counter = -1
#                         else:
#                             counter +=1
#                     else:
#                         counter +=1
                    last_circle[0] = i[0]
                    last_circle[1] = i[1]
                    last_circle[2] = i[2]
                    last_circle[3] = frameCount
                    resetFlag = 0
#                 else:
#                     counter +=1
                    
            if flag:
                if debug:    
                    cv2.imshow('detected circles', cimg)
                    cv2.waitKey(1)
                    if save:
                        circ[hc * cropHeight:hc, 0:wc] = cimg
#         else:
#             counter += 1
#     else:
#         counter += 1
    
    if save:
        da = np.hstack((image, circ)).astype(np.uint8, copy=False)
        video2.write(da)
    counter += 1
    print 'sim:', similar,' counter:', counter, ' reset:', resetFlag 
    cv2.waitKey(100)
    return similar

    
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
        frameCount +=1
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
