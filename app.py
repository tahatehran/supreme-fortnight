#کتابخانه مورد نیاز حتما فایل requirements.txt را با دستور دانلود کنید 
# وارد کردن کتابخانه‌های مورد نیاز
from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
import sys
import logging
import os

# ایجاد یک نمونه از برنامه Flask
app = Flask(__name__)

# تنظیم پیکربندی لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# تنظیمات اتصال به پایگاه داده
db_config = {
    'host': os.environ.get('DB_HOST', 'HOST_DATA'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'USER_DATA'),
    'password': os.environ.get('DB_PASSWORD', 'PASSWORD_DATA'),
    'database': os.environ.get('DB_NAME', 'NAME_DATA')
}

# کلاس مدیریت پایگاه داده
class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

    # باز کردن اتصال به پایگاه داده
    def open_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                logger.info("Database connection opened.")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.connection = None

    # متد جدید برای گرفتن اتصال به پایگاه داده
    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.open_connection()
        return self.connection

    # بستن اتصال پایگاه داده
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed.")

    # اجرای کوئری SELECT
    def execute_query(self, query, params=None):
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as err:
            logger.error(f"Database query error: {err}")
            return None

    # اجرای کوئری INSERT
    def execute_insert(self, query, params):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as err:
            logger.error(f"Database insert error: {err}")
            return None

# ایجاد یک نمونه از کلاس Database
db = Database(db_config)

# کلاس سرویس دانش‌آموز
class StudentService:
    @staticmethod
    def get_all_students():
        return db.execute_query("SELECT * FROM students")

    @staticmethod
    def get_student_by_id(student_id):
        return db.execute_query("SELECT * FROM students WHERE id = %s", (student_id,))

    @staticmethod
    def add_student(name, lastname, age):
        return db.execute_insert(
            "INSERT INTO students (name, lastname, age) VALUES (%s, %s, %s)",
            (name, lastname, age)
        )

# کلاس مدیریت خطاها
class ErrorHandler:
    @staticmethod
    def handle_database_error(err):
        logger.error(f"Database error: {err}")
        return jsonify({'error': 'Database error occurred'}), 500

    @staticmethod
    def handle_unexpected_error(e):
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

    @staticmethod
    def handle_missing_fields():
        return jsonify({'error': 'Missing required fields'}), 400

    @staticmethod
    def handle_invalid_student_id():
        return jsonify({'error': 'Invalid student ID'}), 400

    @staticmethod
    def handle_student_not_found():
        return jsonify({'error': 'Student not found'}), 404

# مسیر اصلی
@app.route('/')
def index():
    return render_template('index.html')

# مسیر دریافت همه دانش‌آموزان
@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        students = StudentService.get_all_students()
        if students is not None:
            return jsonify(students), 200
        else:
            return ErrorHandler.handle_database_error("Failed to fetch students")
    except Exception as e:
        return ErrorHandler.handle_unexpected_error(e)

# مسیر دریافت دانش‌آموز با شناسه
@app.route('/student', methods=['POST'])
def get_student_by_id():
    student_id = request.form.get('id')
    if not student_id:
        return ErrorHandler.handle_missing_fields()

    try:
        student_id = int(student_id)
    except ValueError:
        return ErrorHandler.handle_invalid_student_id()

    try:
        student = StudentService.get_student_by_id(student_id)
        if student:
            return jsonify(student[0]), 200
        else:
            return ErrorHandler.handle_student_not_found()
    except Exception as e:
        return ErrorHandler.handle_unexpected_error(e)

# مسیر اضافه کردن دانش‌آموز جدید
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    age = request.form.get('age')

    if not name or not lastname or not age:
        return ErrorHandler.handle_missing_fields()

    try:
        age = int(age)
    except ValueError:
        return ErrorHandler.handle_invalid_student_id()

    try:
        new_id = StudentService.add_student(name, lastname, age)
        if new_id is not None:
            new_student = {'id': new_id, 'name': name, 'lastname': lastname, 'age': age}
            return jsonify(new_student), 201
        else:
            return ErrorHandler.handle_database_error("Failed to add student")
    except Exception as e:
        return ErrorHandler.handle_unexpected_error(e)

# اجرای برنامه
if __name__ == '__main__':
    if db.get_connection():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        sys.exit(1)
