import cv2  
import numpy as np
import sys

# noise.py from capral-ocr
# http://opencvpython.blogspot.com.au/2012/06/contours-2-brotherhood.html

debug = True
crop = True
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data

lowThreshold = 50
max_lowThreshold = 100
ratio = 3
kernel_size = 3
h = 0
w = 0
c = 0

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
        process(frame)
        val, frame = stream.read()

# # Used for Canny edge detection       
# def CannyThreshold(lowThreshold, gray, img):
#     detected_edges = cv2.GaussianBlur(gray,(5,5),0)
#     detected_edges = cv2.Canny(detected_edges,lowThreshold,lowThreshold*ratio,apertureSize = kernel_size)
#     dst = cv2.bitwise_and(img,img,mask = detected_edges)  # just add some colours to edges from original image.
#     
#     if debug:
#         print message
#         cv2.imshow('canny demo',dst)
#         cv2.waitKey()
#     

    
def process(image):
    hc, wc, cc = np.shape(image)
    cropIm = image[hc*0.55:hc,0:wc]
    if debug:
        cv2.imshow('original', image)
        cv2.waitKey(1)
        
    grayIm = cv2.cvtColor(cropIm, cv2.COLOR_BGR2GRAY)
    
#     """
#     Canny edge detection
#     """
#     cv2.namedWindow('canny demo')
#     
# #     def thresh(lowThreshold):
# #         CannyThreshold(cv2.getTrackbarPos('Min threshold', 'canny demo'), grayIm, cropIm) # initialization
# # 
# #     cv2.createTrackbar('Min threshold','canny demo',lowThreshold, max_lowThreshold, thresh)
# #     
# 
#     CannyThreshold(lowThreshold, grayIm, cropIm) # initialization
#     

    """
    Houghcircles detection
    """
    img = cv2.medianBlur(grayIm,5)
    cimg = cropIm
    circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,200,param1=100,param2=40,minRadius=35,maxRadius=90)
    if circles is not None:
        if len(circles[0]) < 3:
            for i in circles[0,:]:
                cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),1)  # draw the outer circle
                cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)     # draw the center of the circle
            if debug:
                cv2.imshow('detected circles',cimg)
#                 print message
                cv2.waitKey(500)
    

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
