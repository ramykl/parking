from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2  
import numpy as np
import glob
 
def doloop():
    global depth, rgb
    path = "../kpictures/"
    num = glob.glob(str(path) + "*.jpg")
    i = len(num)
    count = 0 
    while True:
        # Get a fresh frame
        (depth, _), (rgb, _) = get_depth(), get_video()
        
        # Build a two panel color image
        d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
        da = np.hstack((d3, rgb)).astype('uint8')
        
        src = cv2.cv.fromarray(da)
        cv2.cv.ShowImage('both', src)
        cv2.waitKey(5)
        if (count % 100) == 0:
            cv2.cv.SaveImage(path + "both" + str(i) + ".jpg", src)
            i += 1
        count += 1
doloop()