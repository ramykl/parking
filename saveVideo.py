import cv2  
import numpy as np
import glob
import sys
import subprocess

# x = 1280
# y = 720


def doloop():
    path = "./videos/"
    num = glob.glob(str(path) + "*.avi")
    i = len(num)
    
    
    p1 = subprocess.Popen(['ls', '-l', '/dev/v4l/by-id'], stdout=subprocess.PIPE) #, '|', 'grep', 'HD-3000']
    p2 = subprocess.Popen(['grep', 'HD-3000'], stdin = p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out = p2.communicate()[0]
    if out == '':
        print 'webcam not attached'
        sys.exit(1)
    cam = int(out[-2])
    
    """
    to get video number for specific camera look in /dev/v4l/by-id "ls -l" 
    """
    stream = cv2.VideoCapture(cam)    
    if not stream.isOpened():
        print 'error opening stream'
        sys.exit(1)
        
    video = cv2.VideoWriter(path+'video'+str(i)+'.avi',cv2.cv.CV_FOURCC('D','I','V','X'),20,(640,480))
    if not video.isOpened():
        print 'error with video opening'
        sys.exit(1)
    
    subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure, Auto', "3"])
    subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Contrast', "1"])
    subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Brightness', "150"])
    subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Saturation', "75"])
    subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Sharpness', "25"])
    
#     stream.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, y)
#     stream.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, x)

    print 'press "q" to exit' 
    while True:
        # Get a fresh frame
        val, bgr = stream.read()
        
        # Build a two panel color image
#         bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        
#         src = cv2.cv.fromarray(da)
        cv2.imshow('stream', bgr)
        video.write(bgr)
        k = cv2.waitKey(1)
        if (k > -1) and (k < 256):
            if chr(k)=='q':
#                 video.release()
                cv2.destroyAllWindows()
                sys.exit(0)
        
doloop()
