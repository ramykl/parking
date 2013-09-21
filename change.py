import cv2  
import numpy as np
import sys

# noise.py from capral-ocr
# http://opencvpython.blogspot.com.au/2012/06/contours-2-brotherhood.html

debug = True
crop = False
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data
save = False # flag for saving video
rotate = True # flag for rotated video

lowThreshold = 50
max_lowThreshold = 100
ratio = 3
kernel_size = 3
h = 0
w = 0
c = 0
sec = 270

cropHeight = 0 #0.55 # 0.55 for kinect images

path = "./videos/"
if save:
    file = 5
    video2 = cv2.VideoWriter(path+'convert'+str(file)+'.avi',cv2.cv.CV_FOURCC('D','I','V','X'),20,(1280,480))
    circ = np.zeros((480,640,3),np.uint8)

#     k = cv2.waitKey(5)
#     if (k > -1) and (k < 256):
#         if chr(k)=='q':
#             cv2.destroyAllWindows()
#             sys.exit(0)


def video(stream):
    val, frame = stream.read()
    h, w, c = np.shape(frame)
    while True:
        if not val:
            break
        if crop:
            frame = frame[0:h,w/2:w]
        if rotate:
            frame = cv2.flip(frame, -1)
        process(frame)
        val, frame = stream.read()
    
def process(image):
    hc, wc, cc = np.shape(image)
    cropIm = image[hc*cropHeight:hc,0:wc]
#     if debug:
#         cv2.imshow('original', image)
# #         cv2.waitKey(1)
        
    grayIm = cv2.cvtColor(cropIm, cv2.COLOR_BGR2GRAY)
#     if debug:    
#         cv2.imshow('Gray',grayIm)
#         cv2.waitKey(10)
    
    
    """
    Houghcircles detection
    """
    img = cv2.medianBlur(grayIm,3)
#     img = cv2.medianBlur(thresh,5)
#     r, img = cv2.threshold(img, 83, 0, cv2.THRESH_TOZERO)
#     r, img = cv2.threshold(img, 200, 0, cv2.THRESH_TOZERO_INV)
    r, img = cv2.threshold(img, 85, 0, cv2.THRESH_TOZERO_INV)
    if debug:    
        cv2.imshow('thresh',img)
        cv2.waitKey(1)
    cimg = cropIm
    circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,400,param1=100,param2=45,minRadius=50,maxRadius=200)
    if circles is not None:
        if len(circles[0]) < 2:
            count = 0
            for i in circles[0,:]:
                if (i[1] < (sec+80)) and (i[1] > (sec-80)):
                    count += 1
                    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),1)  # draw the outer circle
                    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)     # draw the center of the circle
            if count:
                if debug:    
                    cv2.imshow('detected circles',cimg)
#                 print message
                    cv2.waitKey(10)
                    if save:
                        circ[hc*cropHeight:hc,0:wc] = cimg
    if save:
        da = np.hstack((image, circ)).astype(np.uint8, copy=False)
        video2.write(da)
    

def main(inputfile):
    if inputfile[-4:] == '.avi':
        print 'Video'
        stream = cv2.VideoCapture(inputfile)
        video(stream)
    elif inputfile[-4:] == '.jpg':
        print 'Image'
        image = cv2.imread(inputfile)
        process(image)
        

if __name__ == '__main__':
    if(len(sys.argv) is not 2):
        print "Usage: python process.py inputfile[.avi or .jpg] outputfile[.avi or .jpg]"
        sys.exit(1)
    else:
        main(sys.argv[1])
