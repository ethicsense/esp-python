import model_manager as mm
import argparse
from server import app



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--server_name',
        type=str,
        default="0.0.0.0"
    )
    parser.add_argument(
        '--server_port',
        type=int,
        default=7999
    )
    args=parser.parse_args()

    app.run(host=args.server_name, port=args.server_port)