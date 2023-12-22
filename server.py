from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import stream_with_context
from flask import send_file
from flask import send_from_directory
from flask import redirect
from streamer import Streamer
from model_manager import model_generator

from pandas import Series, DataFrame

import os
import cv2
import time

IMAGE_FOLDER = os.path.join('static', 'img')

app = Flask(__name__)
streamer = Streamer()
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

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
    gen = stream_gen(model, url)

    try:
        return Response(
            stream_with_context(gen),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print('[EVC]', 'stream error :', str(e))


@app.route('/predImg', methods=['POST', 'GET'])
def pred_img():
    model_name = str(request.form.get("files"))
    modelGen = model_generator(model_name)
    model = modelGen.get_model()
    url = request.form["url"]
    
    filename = streamer.image_prediction(model, url)
    full_fname = os.path.join(app.config["IMAGE_FOLDER"], filename)

    return render_template("image_predict_page.html", user_image=full_fname)




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


@app.route('/downloadLog', methods=['POST', 'GET'])
def downloadLog():
    model_name = str(request.form.get("files"))
    modelGen = model_generator(model_name)
    model = modelGen.get_model()
    url = request.form["url"]

    cap = cv2.VideoCapture(url)
    log = []

    ret, frame = cap.read()

    while True:
        results = model(frame)
        now = time.time()
        
        
        for r in results:

            if not r :
                continue

            tmp = r.boxes.data.cpu().numpy()

            for t in tmp:
                data = {}

                data["timestamp"] = now
                data["x1"] = t[0]
                data["y1"] = t[1]
                data["x2"] = t[2]
                data["y2"] = t[3]
                data["conf"] = t[4]
                data["clss"] = t[5]

                log.append(data)

        ret, frame = cap.read()
        
        if not ret:
            break
    
    path = os.getcwd() + "/logs/evclog.csv"
    dflog = DataFrame(log)
    dflog.to_csv(path)

    return send_file(
        path,
        as_attachment=True
    )