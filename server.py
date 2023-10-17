from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import stream_with_context
from streamer import Streamer
from model_manager import model_generator
import os

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


@app.route('/test', methods=['POST', 'GET'])
def test():
    model_name = request.form.get("files")

    return model_name


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

