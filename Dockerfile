# استفاده از تصویر پایه Python
FROM python:3.9-slim

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن requirements.txt
COPY requirements.txt requirements.txt

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن فایل‌های پروژه
COPY . .

# ایجاد محیط مجازی
RUN python -m venv venv

# فعال کردن محیط مجازی
ENV PATH="/app/venv/bin:$PATH"

# ایجاد دایرکتوری برای لاگ‌ها
RUN mkdir -p /app/logs

# اجرای Gunicorn برای سرو کردن اپلیکیشن
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
