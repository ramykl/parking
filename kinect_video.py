from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2  
import numpy as np
import glob
import sys


def doloop():
    global depth, rgb
    path = "./kpictures/"
    num = glob.glob(str(path) + "*.avi")
    i = len(num)
    video = cv2.VideoWriter(path+'video'+str(i)+'.avi',cv2.cv.CV_FOURCC('D','I','V','X'),20,(1280,480))
    if not video.isOpened():
        print 'error with video opening'
        sys.exit(1)
    print 'press "q" to exit' 
    while True:
        # Get a fresh frame
        (depth, _), (rgb, _) = get_depth(), get_video()
        
        # Build a two panel color image
        d3 = np.dstack((depth, depth, depth)).astype(np.uint8, copy=False)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        da = np.hstack((d3, bgr)).astype(np.uint8, copy=False)
        
#         src = cv2.cv.fromarray(da)
        cv2.imshow('both', da)
        video.write(da)
        k = cv2.waitKey(5)
        if (k > -1) and (k < 256):
            if chr(k)=='q':
#                 video.release()
                cv2.destroyAllWindows()
                sys.exit(0)
        
doloop()