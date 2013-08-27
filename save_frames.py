from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2  
import numpy as np
import glob
import sys

total = 10

def doloop():
    global depth, rgb
    path = "./kpictures/"
    num = glob.glob(str(path) + "*.jpg")
    i = len(num)
    count = 0 
    while True:
        # Get a fresh frame
        (depth, _), (rgb, _) = get_depth(), get_video()
        
        # Build a two panel color image
        d3 = np.dstack((depth, depth, depth)).astype(np.uint8, copy=False)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        da = np.hstack((d3, bgr)).astype(np.uint8, copy=False)
        
#         src = cv2.cv.fromarray(da)
        cv2.imshow('both', da)
        k = cv2.waitKey(5)
        if (k > -1) and (k < 256):
            if chr(k) == 'q':
                cv2.destroyAllWindows()
                sys.exit(0)
        if (count % total) == 0:
            cv2.imwrite(path + "both" + str(i) + ".jpg", da)
            i += 1
        count += 1
        
        
doloop()
