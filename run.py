import model_manager as mm
import argparse
from server import app


def new_weights(f):

    return f



def streaming_server():
    pass



def main(model_type, model_name, url):

    app.run(host='0.0.0.0', port=5454)

    # output_path = model.stream_infer()

    # print()
    # print()
    # print()
    # print()
    # print(f"saved path : {output_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_type',
        type=str,
        default="YOLOv8"
    )
    parser.add_argument(
        '--model_name',
        type=str,
        default='yolov8n.pt'
    )
    parser.add_argument(
    '--url',
    type=str,
    default='rtsp://user1:ketiabcs@evc.re.kr:39091/h264Preview_01_main'
    )
    args=parser.parse_args()

    main(args.model_type, args.model_name, args.url)