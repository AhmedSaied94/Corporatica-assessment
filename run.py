import sys

from app import create_app

app = create_app()

if __name__ == "__main__":
    # read the port and host from the command line as kwargs
    kwargs = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False,
    }
    # argv[0] is the script name
    print("Number of arguments:", sys.argv)
    if len(sys.argv) > 1:
        kwargs["host"] = sys.argv[1]
    if len(sys.argv) > 2:
        kwargs["port"] = int(sys.argv[2])
    if len(sys.argv) > 3:
        kwargs["debug"] = sys.argv[3] == "debug"

    app.run(**kwargs)
