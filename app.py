from flask import Flask, jsonify, request, render_template, abort
import mysql.connector
from mysql.connector import Error
import sys

app = Flask(__name__)

# تنظیمات اتصال به پایگاه داده
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'students_db'
}

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def check_database_connection():
    connection = create_connection()
    if connection:
        print("Successfully connected to the database.")
        connection.close()
        return True
    else:
        print("Failed to connect to the database. Exiting...")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        connection = create_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students"
        cursor.execute(query)
        students = cursor.fetchall()
        
        cursor.close()
        connection.close()

        return jsonify(students), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/student', methods=['POST'])
def get_student_by_id():
    try:
        student_id = request.form.get('id')
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400

        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({'error': 'Invalid student ID'}), 400

        connection = create_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE id = %s"
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if student:
            return jsonify(student), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        age = request.form.get('age')

        if not name or not lastname or not age:
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            age = int(age)
        except ValueError:
            return jsonify({'error': 'Age must be a number'}), 400

        connection = create_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()
        
        query = "INSERT INTO students (name, lastname, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, lastname, age))
        connection.commit()
        
        new_id = cursor.lastrowid
        
        cursor.close()
        connection.close()

        new_student = {
            'id': new_id,
            'name': name,
            'lastname': lastname,
            'age': age
        }
        return jsonify(new_student), 201

    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    if check_database_connection():
        app.run(debug=True)
    else:
        sys.exit(1)
