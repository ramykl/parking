import cv2  
import numpy as np
import glob
import sys
import subprocess
import threading
import Queue
import select
import time

# camera name to be found
camera = "C920"
# camera = 'HD-3000'


def doloop():
    path = "./videos/"
    num = glob.glob(str(path) + "video*.avi")
    i = len(num)
    
    print camera
    
    # gets camera video number by searching in /dev/v4l/by-id with the camera name 
    p1 = subprocess.Popen(['ls', '-l', '/dev/v4l/by-id'], stdout=subprocess.PIPE) #, '|', 'grep', 'HD-3000']
    p2 = subprocess.Popen(['grep', camera], stdin = p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out = p2.communicate()[0]
    if out == '':
        print 'webcam not attached'
        sys.exit(1)
    
    # camera number
    cam = int(out[-2])
    # settings for the logitech C920 webcam
    if camera == 'c920':
        subprocess.Popen(['v4l2-ctl', '-d', '/dev/video'+str(cam), '--set-fmt-video=width=640,height=480,pixelformat=1'])
        subprocess.Popen(['v4l2-ctl', '-d', '/dev/video'+str(cam), '--set-parm=30'])
    
    
        # 1 for manual, 3 for auto
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Brightness', "50"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Contrast', "128"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Saturation', "128"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Gain', "50"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Power Line Frequency', "0"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'White Balance Temperature, Auto', "1"])
#         subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'White Balance Temperature, Auto', "0"])
#         subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'White Balance Temperature', "3200"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Sharpness', "25"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Backlight Compensation', "0"])
#         subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure, Auto', "3"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure, Auto', "1"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure (Absolute)', "25"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure, Auto Priority', "1"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Focus, Auto', "0"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Focus (Absolute)', "0"])
    
    # settings for the Microsoft HD-3000 webcam 
    elif camera == 'HD-3000':
        # 1 for manual, 3 for auto
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure, Auto', "1"])
        # Exposure level 5, 10, 20, 39, 78, 156, 312, ... [roughly double value] (darkest to lightest)
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Exposure (Absolute)', "5"]) 
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Contrast', "1"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Brightness', "150"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Saturation', "50"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Sharpness', "25"])
        subprocess.Popen(['uvcdynctrl', '-dvideo'+str(cam), "-s",  'Power Line Frequency', "0"])
    
    
    """
    create video capture stream
    """
    stream = cv2.VideoCapture(cam)    
    if not stream.isOpened():
        print 'error opening stream'
        sys.exit(1)
        
    """
    create video writing stream
    """
#     video = cv2.VideoWriter(path+'video'+str(i)+'.avi',cv2.cv.CV_FOURCC('H','2','6','4'),30,(640,480))
    video = cv2.VideoWriter(path+'video'+str(i)+'.avi',cv2.cv.CV_FOURCC('D','I','V','X'),30,(640,480))
    if not video.isOpened():
        print 'error with video opening'
        sys.exit(1)
    
    time.sleep(1)
    # create two queues for passing data between threads
    flag = Queue.Queue(0)
    pic = Queue.Queue(0)
    
    # create and start thread to capture frames 
    t1 = threading.Thread(target=get_frames, args=(flag, pic, stream, video))
    t1.setDaemon(True)
    t1.start()
    print "press 'q' to exit, press 's' to toggle show images"
    k = 0
    while True:
        #check for image from capture thread
        try:
            im = pic.get_nowait()
        except Queue.Empty:
            im = None
        
        # display image if available
        if im is not None:
            cv2.imshow('stream', im)
            cv2.waitKey(1)
            im = None
        
        # check for input from terminal
        i,o,e = select.select([sys.stdin],[],[],0.01)
        if (i):
            k = sys.stdin.readline().strip()
        
        # check input for specific commands
        if k == 'q':
            # quit program
            flag.put_nowait(k)
            t1.join()
            cv2.destroyAllWindows()
            sys.exit(0)
        if k == 's':
            # toggle display frames
            flag.put_nowait(k)
            time.sleep(1)
            cv2.destroyAllWindows()
            k = 0

# thread for getting frames from webcam and saving them
def get_frames(flag, pic, stream, video):
    show = False
    count = 0
    while True:
        # get and write frame
        val, bgr = stream.read()
        video.write(bgr)
        
        # check for exit command or toggle show 
        try:
            temp = flag.get_nowait()
        except Queue.Empty:
            temp = 0
        
        # toggle show
        if temp == 's':
            show = not show
            print "show stream:", show
            count = 0
            temp = 0
            if not show:
                # clear queue if show is turned off
                pic.queue.clear()
        if show:
            count += 1
            # show only every 5th frame to limit processing
            if count %5 == 0:
                pic.put_nowait(bgr)
        # quit program
        if temp == 'q':
            # end thread
            print "exiting"
            break

# run main function
doloop()
