from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import stream_with_context
from flask import send_file
from flask import redirect
from streamer import Streamer
from model_manager import model_generator

import os
import cv2
import time

app = Flask(__name__)
streamer = Streamer()


@app.route('/', methods=['POST', 'GET'])
def model_choice():
    files = os.listdir(os.getcwd() + '/weights')

    return render_template('get_model.html', files=files)


@app.route('/stream', methods=['POST', 'GET'])
def stream():
    model_name = str(request.form.get("files"))
    modelGen = model_generator(model_name)
    model = modelGen.get_model()
    url = request.form["url"]

    try:
        return Response(
            stream_with_context(stream_gen(model, url)),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print('[EVC]', 'stream error :', str(e))


def stream_gen(model, url):

    try:
        streamer.run(model, url)

        while True:
            frame = streamer.bytescode()
            yield (
                b'--frame\r\n'
                b'Content-Type : image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

    except GeneratorExit :
        print("[EVC]", "disconnected stream")
        streamer.stop()


@app.route('/downloadVideo', methods=['POST', 'GET'])
def downloadVideo():
    model_name = str(request.form.get("files"))
    modelGen = model_generator(model_name)
    model = modelGen.get_model()
    url = request.form["url"]

    capture = cv2.VideoCapture(url)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    crttime = time.time()

    filename = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(crttime)))
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    path = os.getcwd() + "/video/out/" + f"{filename}.mp4"

    out = cv2.VideoWriter(path, fourcc, fps, (width, height))

    while capture.isOpened:
        grabbed, frame = capture.read()

        if grabbed:
            results = model(frame)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        else:
            break

    capture.release()
    out.release()

    return send_file(
        path,
        as_attachment=True
    )



def downloadLog():

    pass