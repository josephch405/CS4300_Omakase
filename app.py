from app import app, socketio
import os
print(os.environ['HOME'])


app_port = 5000
if "PORT" in os.environ:
    app_port = os.environ["PORT"]


if __name__ == "__main__":
    print(f"Flask app running at http://0.0.0.0:{app_port}")
    socketio.run(app, host="0.0.0.0", port=app_port)
