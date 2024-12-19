from flask import Flask, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from game import Game

app = Flask(__name__, static_folder='templates', static_url_path='/')
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)

    # Initialize room state if it doesn't exist
    if room not in chat_rooms:
        chat_rooms[room] = {
            'users': [],
            'user_sessions': {},
            'game': Game(),  # Example of a room-specific variable
        }

    # Check if the room is already full
    if len(chat_rooms[room]['users']) >= 2:
        emit('room_full', {'message': 'The room is already full.'}, to=request.sid)
        return

    # Add user to room state
    chat_rooms[room]['users'].append(username)
    chat_rooms[room]['user_sessions'][username] = request.sid

    # Notify the user and provide the initial Game state
    # game = chat_rooms[room]['game']
    emit('join_successful', to=request.sid)
    emit('user_joined', {'username': username, 'message': f'{username} has joined the room.'}, room=room, include_self=False)
    # emit('game_state', {'year': game.year, 'price_company1': game.company1.price, 'price_company2': game.company2.price}, room=room)


if __name__ == '__main__':
    app.run(debug=True)
