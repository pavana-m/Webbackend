import os
import jwt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask_mysqldb import MySQL
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
system = Flask(__name__)
jwt = JWTManager(system)
system.secret_key = '12345'

tuffy_recipes_FOLDER = 'static/tuffy_recipes'
user_recipes_FOLDER = 'static/user_recipes'
file_types = {'txt', 'docx', 'pdf'}
dimensions=  4 * 1024 * 1024

system.config['sync_tuffy_recipes'] = os.path.join(system.root_path, tuffy_recipes_FOLDER)
system.config['sync_user_recipes'] = os.path.join(system.root_path, user_recipes_FOLDER)

system.config['MYSQL_USER'] = 'root'
system.config['MYSQL_passcode'] = 'Krishna@2604'
system.config['MYSQL_HOST'] = '127.0.0.1'
system.config['MYSQL_DB'] = 'systemle'
JWT_SECRET_KEY = '12345'


mysql = MySQL(system)

def permitted_document(documentname):
    return '.' in documentname and documentname.rsplit('.', 1)[1].lower() in file_types

@system.route('/')
def home_page():
    recipes_doc = os.listdir(system.config['sync_tuffy_recipes'])
    return render_template('home_page.html', recipes_doc=recipes_doc)

@system.route('/enroll', methods=['POST'])
def enroll():
        if request.method == 'POST':
            studentname = request.form['studentname']
            passcode = request.form['passcode']

            # Check if the studentname is already in use
            point = mysql.connection.cursor()
            point.execute("SELECT * FROM users WHERE studentname= %s", [studentname])
            user = point.fetchone()
            point.close()
            if user:
                flash('studentname already in use', 'danger')
            else:
                point = mysql.connection.cursor()
                point.execute("INSERT INTO users (studentname, passcode) VALUES (%s, %s)", [studentname, passcode])
                mysql.connection.commit()
                point.close()
                flash('Student Account created ! turn_in with your student credentials', 'Done')
        recipes_doc = os.listdir(system.config['sync_tuffy_recipes'])
        return render_template('home_page.html', recipes_doc=recipes_doc)
        
@system.route('/tuffy_home', methods=['GET', 'POST'])
def tuffy_home():
    try:
        if request.method == 'POST':
            # Handle file sync and save it to the user_recipes folder
            file = request.files['file']
            if file and permitted_document(file.documentname) and (len(file.read()) < dimensions):
                file.save(os.path.join(system.config['sync_user_recipes'], file.documentname))

        tuffy_recipes = os.listdir(system.config['sync_user_recipes'])
        return render_template('tuffy_home.html', tuffy_recipes=tuffy_recipes)
            
    except jwt.ExpiredSignatureError:
        return "SignIn expired. Please log in again."    

@system.route('/delete/<string:documentname>', methods=['DELETE'])
def delete_recipe(documentname):
    recipe_path = os.path.join(system.config['sync_user_recipes'], documentname)
    if os.path.exists(recipe_path):
        os.remove(recipe_path)
        return jsonify({"message": "Recipe deleted successfully"}), 200
    else:
        return jsonify({"message": "Recipe not found"}), 404

@system.route('/turn_in', methods=['POST'])
def turn_in():
        if request.method == 'POST':
            studentname = request.form['studentname']
            passcode = request.form['passcode']

            point = mysql.connection.cursor()
            point.execute("SELECT * FROM users WHERE studentname = %s", [studentname])
            user = point.fetchone()
            print(user)
            point.close()

            if user and (user[0]==studentname and user[1]==passcode):
                session['user_id'] = user[0]
                flash('turn_in successful', 'Done')
                session.user = studentname
                return redirect(url_for('tuffy_home'))
                # access_token = create_access_token(identity=studentname)
                # tuffy_recipes = os.listdir(system.config['sync_user_recipes'])
                # render_template('tuffy_home.html', tuffy_recipes=tuffy_recipes)
                # return jsonify(access_token=access_token), 200 
            else:
                flash('turn_in failed', 'error')
        recipes_doc = os.listdir(system.config['sync_tuffy_recipes'])
        return render_template('home_page.html', recipes_doc=recipes_doc)    


if __name__ == '__main__':
    system.run(debug=True)
























