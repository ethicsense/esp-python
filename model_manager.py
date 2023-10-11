import torch
import os
from ultralytics import YOLO
import cv2
import datetime

class model_generator:

    def __init__(self, model_name):
        self.model_type = "YOLOv8"
        self.model_name = model_name
        self.dir = os.getcwd()

    def get_model(self):
        model = YOLO(self.dir + "/weights/" + self.model_name)

        return model



class model_predictor(model_generator):

    def __init__(self, model_type, model_name, url=None, video=None):
        super().__init__(model_type, model_name)
        self.url = url
        self.video = video

    def video_infer(self):
        
        cap = cv2.VideoCapture(self.video)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            os.path.join(os.path.dirname(__file__),'video/out/output.mp4'),
            fourcc,
            30.0,
            (width,height)
        )
        output_file = os.path.join(os.path.dirname(__file__),'video/out/output.mp4')

        while cap.isOpened():
        # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLOv8 inference on the frame
                results = self.model(frame)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()

                # # write video
                out.write(annotated_frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                # Break the loop if the end of the video is reached
                break
        
        cap.release()
        out.release()

        return output_file


    def stream_infer(self):

        currenttime = datetime.datetime.now()
        video_capture = cv2.VideoCapture(self.url)
        
        video_capture.set(3, 100)
        video_capture.set(4, 100)
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))

        streaming_window_width = int(video_capture.get(3))
        streaming_window_height = int(video_capture.get(4))

        filename = str(currenttime.strftime('%Y %m %d %H %M %S'))
        path = os.getcwd() + "/stream/" + f"{filename}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (streaming_window_width, streaming_window_height))

        iterating, frame = video_capture.read()

        while iterating:
            results = self.model(frame)
            annotated_frame = results[0].plot()

            cv2.imshow("streaming inference", annotated_frame)
            out.write(annotated_frame)

            iterating, frame = video_capture.read()
            
            k = cv2.waitKey(1) & 0xff
            if k == ord('q'):
                break

        video_capture.release()
        out.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        return path