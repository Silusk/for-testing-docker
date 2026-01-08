CREATE DATABASE hospital_db;
USE hospital_db;
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE doctor_salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT,
    salary DECIMAL(10,2),
    month VARCHAR(20),
    status VARCHAR(20),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);
CREATE TABLE nurses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE nurse_salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nurse_id INT,
    salary DECIMAL(10,2),
    month VARCHAR(20),
    status VARCHAR(20),
    FOREIGN KEY (nurse_id) REFERENCES nurses(id)
);

CREATE TABLE workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE worker_salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT,
    salary DECIMAL(10,2),
    month VARCHAR(20),
    status VARCHAR(20),
    FOREIGN KEY (worker_id) REFERENCES workers(id)
);
ALTER TABLE doctors ADD COLUMN role VARCHAR(50);
ALTER TABLE workers ADD COLUMN role VARCHAR(50);
ALTER TABLE nurses ADD COLUMN role VARCHAR(50);
ALTER TABLE doctor_salaries ADD UNIQUE(doctor_id);
ALTER TABLE nurse_salaries ADD UNIQUE(nurse_id);
ALTER TABLE worker_salaries ADD UNIQUE(worker_id);
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    father_name VARCHAR(100),
    village VARCHAR(100),
    phone VARCHAR(20)
);
ALTER TABLE patients ADD COLUMN record_date DATE NOT NULL DEFAULT (CURRENT_DATE);
ALTER TABLE patients ADD UNIQUE KEY unique_patient (name, phone, record_date);