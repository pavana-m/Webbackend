from flask import Flask, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secret key for production
jwt = JWTManager(app)

# Simulated user database (replace this with a real database in a production app)
users = {
    'user1': 'password1',
    'user2': 'password2',
}

@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        # Create an access token (JWT)
        access_token = create_access_token(identity=username)
        return redirect(url_for('user_home', username=username, access_token=access_token))
    else:
        return 'Invalid username or password', 401

@app.route('/user_home/<username>', methods=['GET'])
@jwt_required()
def user_home(username):
    current_user = get_jwt_identity()
    if username == current_user:
        return f'Welcome to your Home Page, {username}!'
    else:
        return 'You do not have access to this user home page.', 403

if __name__ == '__main__':
    app.run(debug=True)
