import cv2  
import numpy as np
import sys

# noise.py from capral-ocr
# http://opencvpython.blogspot.com.au/2012/06/contours-2-brotherhood.html

debug = True
message = 'waiting for button press'
lowerThresh = 0
upperThresh = 255
scale = 1  # 8 for 11 bit data

def video(stream):
    while True:
        val, frame = stream.read()
        if not val:
            break
        process(frame)

def process(image):
    cv2.imshow('image', image)
    if debug:
        print message
        cv2.waitKey()
    
    # everything below lowerThresh is set to 0
    val, threshIm = cv2.threshold(image, lowerThresh * scale, upperThresh * scale, cv2.THRESH_TOZERO)
    # everything above upperThresh is set to 0
    val, threshIm = cv2.threshold(threshIm, upperThresh * scale, upperThresh * scale, cv2.THRESH_TOZERO_INV)
    cv2.imshow('thresh', threshIm)
    if debug:
        print message
        cv2.waitKey()
    # do more image processing
    # blob detection - need to blur to get values similar
    # stuff

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
        print "Usage: python process.py inputfile[.avi or .jpg]"
        sys.exit(1)
    else:
        main(sys.argv[1])
