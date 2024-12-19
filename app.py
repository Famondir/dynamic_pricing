from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from game import Game

app = Flask(__name__, static_folder='build', static_url_path='/')
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to track active chat rooms
chat_rooms = {}

@app.route('/')
def index():
    # return {"status": "Server is running"}
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)

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

@socketio.on('get_game_state')
def handle_get_game_state(data):
    room = data['room']
    sid = request.sid  # Get the unique session ID of the requester
    if room in chat_rooms:
        game = chat_rooms[room]['game']
        emit('game_state', {
            'year': game.year,
            'capital_company1': game.company1.capital,
            'capital_company2': game.company2.capital,
            'price_company1': game.company1.price,
            'price_company2': game.company2.price,
            'loyals_company1': game.company1.loyals,
            'loyals_company2': game.company2.loyals
        }, to=sid)

def send_game_state(data):
    room = data['room']
    if room in chat_rooms:
        game = chat_rooms[room]['game']
        emit('game_state', {
            'year': game.year,
            'capital_company1': game.company1.capital,
            'capital_company2': game.company2.capital,
            'price_company1': game.company1.price,
            'price_company2': game.company2.price,
            'loyals_company1': game.company1.loyals,
            'loyals_company2': game.company2.loyals
        }, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    message = data['message']
    emit('receive_message', {'username': username, 'message': message}, room=room, include_self=False)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    # Remove user from room state
    if room in chat_rooms and username in chat_rooms[room]['users']:
        chat_rooms[room]['users'].remove(username)

        # Notify others in the room
        emit('user_left', {'username': username, 'message': f'{username} has left the room.'}, room=room)

@socketio.on('get_rooms')
def handle_get_rooms():
    rooms_list = [
        {
            'name': room,
            'users': chat_rooms[room]['users']
        } for room in chat_rooms
    ]
    emit('rooms_list', {'rooms': rooms_list}, to=request.sid)

@socketio.on('get_users_in_room')
def send_user_list(data):
    room = data['room']
    if room in chat_rooms:
        emit('users_list', {'users': chat_rooms[room]['users']}, room=room)

@socketio.on('start_game')
def handle_start_game(data):
    room = data['room']
    game = chat_rooms[room]['game']

    if room in chat_rooms:
        users = chat_rooms[room]['users']

        if len(users) == 2:
            # Notify all clients to hide the "Start Game" button
            emit('hide_start_button', {}, room=room)
            game.state_label = 'in progress'
            game.set_next_state()
            show_next_modal(game, users, room)

def show_next_modal(game, users, room, decison=None):
    # Assign modals to users
    next_player_list_index = game.get_next_player_index()
    user1, user2 = users[next_player_list_index], users[1 - next_player_list_index]
    user1_sid = chat_rooms[room]['user_sessions'][user1]
    user2_sid = chat_rooms[room]['user_sessions'][user2]

    modal_data = game.get_modal_data()

    emit('show_modal', {
        'username': user1,
        'message': modal_data['message'],
        'choices': modal_data['choices']
    }, to=user1_sid)  # Emit to User 1
    emit('show_modal', {
        'username': user2,
        'message': "Waiting for opponent's move...",
        'choices': []
    }, to=user2_sid)  # Emit to User 2

@socketio.on('game_decision')
def handle_game_decision(data):
    room = data['room']
    users = chat_rooms[room]['users']
    username = data['username']
    player = users.index(username) + 1
    decision = data['decision']  # True for Yes, False for No
    game = chat_rooms[room]['game']

    print(f"{username} in {room} chose: {decision}")
    
    # Process the decision and perform game logic as needed
    game.resolve_decision(decision, player)
    send_game_state(data)
    game.set_next_state(decision)
    show_next_modal(game, users, room, decison=None)

if __name__ == '__main__':
    socketio.run(app)