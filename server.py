from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import stream_with_context
from streamer import Streamer
from model_manager import model_generator

app = Flask(__name__)
streamer = Streamer()

@app.route('/pickModel', methods=['POST', 'GET'])
def model_choice():
    return render_template('get_model.html')

@app.route('/stream', methods=['POST', 'GET'])
def stream():

    model_name = request.form["Model Name"]
    modelGen = model_generator(model_name)
    model = modelGen.get_model()
    url = request.form["Cam URL"]
    src = request.args.get('src', default = 0, type = int)

    try:
        return Response(
            stream_with_context(stream_gen(model, url, src)),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print('[EVC]', 'stream error :', str(e))


def stream_gen(model, url, src):

    try:
        streamer.run(model, url, src)

        while True:
            frame = streamer.bytescode()
            yield (
                b'--frame\r\n'
                b'Content-Type : image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
    except GeneratorExit :
        print("[EVC]", "disconnected stream")
        streamer.stop()

