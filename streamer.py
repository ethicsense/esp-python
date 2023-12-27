import time
import cv2
import imutils
import platform
import numpy as np
from threading import Thread
from queue import Queue
import os
import requests

class Streamer:
    def __init__(self):
        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)

        print('[wandlab] ', 'OpenCL : ', cv2.ocl.haveOpenCL())

        self.img = None
        self.capture = None
        self.thread = None
        self.width = 0
        self.height = 0
        self.stat = False
        self.current_time = time.time()
        self.preview_time = time.time()
        self.sec = 0
        self.Q = Queue(maxsize=128)
        self.started = False


    def image_prediction(self, model, url):
        self.model = model
        self.url = url

        img_nparr = np.asarray(bytearray(requests.get(self.url).content), dtype=np.uint8)
        self.img = cv2.imdecode(img_nparr, cv2.IMREAD_COLOR)

        results = self.model(self.img)
        pred_img = results[0].plot()

        filename = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))
        path = os.getcwd() + "/static/img/" + f"{filename}.jpg"
        filename = f"{filename}.jpg"

        cv2.imwrite(path, pred_img)

        return filename


    def pred(self, model, url):
        self.model = model
        self.url = url
        self.stop_img()

        img_nparr = np.asarray(bytearray(requests.get(self.url).content), dtype=np.uint8)
        self.capture = cv2.imdecode(img_nparr, cv2.IMREAD_COLOR)

        self.height, self.width, _ = self.capture.shape

        self.filename = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(self.current_time)))
        self.path = os.getcwd() + "/img/out/" + f"{self.filename}.jpg"
        
        if self.thread is None:
            self.thread = Thread(target=self.update_img, args=())
            self.thread.daemon = False
            self.thread.start()
        
        self.started = True

    def run(self, model, url):
        self.model = model
        self.url = url
        self.stop()
    
        if platform.system() == 'Windows':
            self.capture = cv2.VideoCapture(self.url, cv2.CAP_DSHOW)
        
        else:
            self.capture = cv2.VideoCapture(self.url)
            
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.filename = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(self.current_time)))
        self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.path = os.getcwd() + "/video/out/" + f"{self.filename}.mp4"
        
        if self.thread is None:
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = False
            self.thread.start()
        
        self.started = True

    def stop(self):
        self.started = False
        
        if self.capture is not None:
            self.capture.release()
            self.clear()

    def stop_img(self):
        self.started = False

        if self.capture is not None:
            self.capture = None
            self.clear()

    
    def write_video(self):
        out = cv2.VideoWriter(self.path, self.fourcc, self.fps, (self.width, self.height))

        while True:
            if self.started:
                grabbed, frame = self.capture.read()
                results = self.model(frame)
                annotated_frame = results[0].plot()
                out.write(annotated_frame)

                if not grabbed:
                    self.out.release()

        return self.path

    
    def update_img(self):

        # while self.started:
        results = self.model(self.capture)
        ann_frame = results[0].plot()
        self.Q.put(ann_frame)


    
    def update(self):

        while True:
            if self.started :
                grabbed, frame = self.capture.read()
                results = self.model(frame)
                annotated_frame = results[0].plot()

                if grabbed : 
                    self.Q.put(annotated_frame)

                else:
                    self.stop()

    def clear(self):

        with self.Q.mutex:
            self.Q.queue.clear()


    def read(self):

        return self.Q.get()


    def blank(self):

        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8)


    def bytescode(self):
        if not self.capture.isOpened():
            frame = self.blank()

        else:
            frame = imutils.resize(self.read(), width=int(self.width))

            if self.stat:
                cv2.rectangle(frame, (0,0), (120,30), (0,0,0), -1)
                fps = "FPS : " + str(self.fps())
                cv2.putText(frame, fps, (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,225), 1, cv2.LINE_AA)

        return cv2.imencode('.jpg', frame)[1].tobytes()

    
    def bytescode_img(self):
        frame = imutils.resize(self.read(), width=int(self.width))

        return cv2.imencode('.jpg', frame)[1].tobytes()

    
    def __exit__(self):
        print(" * streamer class exit")
        self.capture.release()