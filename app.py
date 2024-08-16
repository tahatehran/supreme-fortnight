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

# تابع برای ایجاد اتصال به پایگاه داده
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)  # تلاش برای اتصال به پایگاه داده
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")  # ثبت خطا در صورت عدم موفقیت
        return None

# تابع برای بررسی اتصال به پایگاه داده
def check_database_connection():
    connection = create_connection()
    if connection:
        logger.info("Successfully connected to the database.")  # ثبت موفقیت در اتصال
        connection.close()
        return True
    else:
        logger.error("Failed to connect to the database.")  # ثبت خطا در صورت عدم موفقیت
        return False

# صفحه اصلی
@app.route('/')
def index():
    return render_template('index.html')  # بارگذاری قالب HTML

# برای دیدن اطلاعات دانشجو
@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        connection = create_connection()  # ایجاد اتصال به پایگاه داده
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500  # خطا در اتصال

        cursor = connection.cursor(dictionary=True)  # ایجاد یک کرسر برای اجرای کوئری
        query = "SELECT * FROM students"  # کوئری برای دریافت تمام دانشجویان
        cursor.execute(query)
        students = cursor.fetchall()  # دریافت نتایج
        
        cursor.close()
        connection.close()

        return jsonify(students), 200  # بازگشت نتایج به صورت JSON
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")  # ثبت خطا در پایگاه داده
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # ثبت خطای غیرمنتظره
        return jsonify({'error': 'An unexpected error occurred'}), 500

# جستجو بر اساس ایدی با استفاده از متد POST
@app.route('/student', methods=['POST'])
def get_student_by_id():
    try:
        student_id = request.form.get('id')  # دریافت شناسه دانشجو از درخواست
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400  # خطا در صورت عدم وجود شناسه

        try:
            student_id = int(student_id)  # تبدیل شناسه به عدد صحیح
        except ValueError:
            return jsonify({'error': 'Invalid student ID'}), 400  # خطا در صورت تبدیل ناموفق

        connection = create_connection()  # ایجاد اتصال به پایگاه داده
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500  # خطا در اتصال

        cursor = connection.cursor(dictionary=True)  # ایجاد کرسر
        query = "SELECT * FROM students WHERE id = %s"  # کوئری برای جستجوی دانشجو بر اساس شناسه
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()  # دریافت نتیجه
        
        cursor.close()
        connection.close()

        if student:
            return jsonify(student), 200  # بازگشت اطلاعات دانشجو
        else:
            return jsonify({'error': 'Student not found'}), 404  # خطا در صورت عدم وجود دانشجو
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")  # ثبت خطا در پایگاه داده
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # ثبت خطای غیرمنتظره
        return jsonify({'error': 'An unexpected error occurred'}), 500

# ایجاد دانشجو بر اساس سن و نام و نام خانوادگی همچنین دادن ایدی خودکار با متد POST
@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        name = request.form.get('name')  # دریافت نام دانشجو
        lastname = request.form.get('lastname')  # دریافت نام خانوادگی دانشجو
        age = request.form.get('age')  # دریافت سن دانشجو

        if not name or not lastname or not age:
            return jsonify({'error': 'Missing required fields'}), 400  # خطا در صورت عدم وجود فیلدهای ضروری

        try:
            age = int(age)  # تبدیل سن به عدد صحیح
        except ValueError:
            return jsonify({'error': 'Age must be a number'}), 400  # خطا در صورت تبدیل ناموفق

        connection = create_connection()  # ایجاد اتصال به پایگاه داده
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500  # خطا در اتصال

        cursor = connection.cursor()  # ایجاد کرسر
        
        query = "INSERT INTO students (name, lastname, age) VALUES (%s, %s, %s)"  # کوئری برای افزودن دانشجو
        cursor.execute(query, (name, lastname, age))
        connection.commit()  # تأیید تغییرات
        
        new_id = cursor.lastrowid  # دریافت شناسه جدید دانشجو
        
        cursor.close()
        connection.close()

        new_student = {
            'id': new_id,
            'name': name,
            'lastname': lastname,
            'age': age
        }
        return jsonify(new_student), 201  # بازگشت اطلاعات دانشجوی جدید

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")  # ثبت خطا در پایگاه داده
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # ثبت خطای غیرمنتظره
        return jsonify({'error': 'An unexpected error occurred'}), 500

# اجرای برنامه
if __name__ == '__main__':
    if check_database_connection():  # بررسی اتصال به پایگاه داده
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # اجرای برنامه
    else:
        sys.exit(1)  # خروج از برنامه در صورت عدم اتصال
