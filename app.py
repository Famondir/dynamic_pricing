from flask import Flask, send_from_directory
# from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__, static_folder='templates', static_url_path='/')


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
