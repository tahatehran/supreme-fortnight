from flask import Flask, jsonify, request, render_template, abort
import mysql.connector
from mysql.connector import Error
import sys
import logging
import os

# ایجاد یک نمونه از برنامه Flask
app = Flask(__name__)

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# تنظیمات اتصال به پایگاه داده
db_config = {
    'host': os.environ.get('DB_HOST', 'HOST_DATA'),  # آدرس میزبان پایگاه داده
    'port': int(os.environ.get('DB_PORT', 3306)),     # پورت پایگاه داده
    'user': os.environ.get('DB_USER', 'USER_DATA'),   # نام کاربری پایگاه داده
    'password': os.environ.get('DB_PASSWORD', 'PASWORD_DATA'),  # رمز عبور پایگاه داده
    'database': os.environ.get('DB_NAME', 'NAME_DATA')  # نام پایگاه داده
}

class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def open_connection(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            logger.info("Database connection opened.")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")

    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.open_connection()
        return self.connection

db = Database(db_config)

# صفحه اصلی
@app.route('/')
def index():
    return render_template('index.html')  # بارگذاری قالب HTML

# برای دیدن اطلاعات دانشجو
@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        connection = db.get_connection()  # دریافت اتصال به پایگاه داده
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students"
        cursor.execute(query)
        students = cursor.fetchall()
        
        cursor.close()
        db.close_connection()  # بستن اتصال

        return jsonify(students), 200
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# جستجو بر اساس ایدی با استفاده از متد POST
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

        connection = db.get_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE id = %s"
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()
        
        cursor.close()
        db.close_connection()  # بستن اتصال

        if student:
            return jsonify(student), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# ایجاد دانشجو بر اساس سن و نام و نام خانوادگی همچنین دادن ایدی خودکار با متد POST
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

        connection = db.get_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()
        query = "INSERT INTO students (name, lastname, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, lastname, age))
        connection.commit()
        
        new_id = cursor.lastrowid
        
        cursor.close()
        db.close_connection()  # بستن اتصال

        new_student = {
            'id': new_id,
            'name': name,
            'lastname': lastname,
            'age': age
        }
        return jsonify(new_student), 201

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# اجرای برنامه
if __name__ == '__main__':
    if db.get_connection():  # بررسی اتصال به پایگاه داده
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # اجرای برنامه
    else:
        sys.exit(1)  # خروج از برنامه در صورت عدم اتصال
