-- db_data/init.sql

-- ایجاد دیتابیس
CREATE DATABASE IF NOT EXISTS datadb;

-- انتخاب دیتابیس
USE databd;

-- ایجاد جدول students
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    age INT NOT NULL
);
