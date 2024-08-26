import sqlite3

##Connect to sqlite3
connection=sqlite3.connect("student.db")

##create a cursor to record insert,update delete etc
cursor=connection.cursor()

##create table
table_info="""CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    email TEXT UNIQUE,
    enrollment_date DATE DEFAULT CURRENT_DATE
);"""
cursor.execute(table_info)

##Insert records
cursor.execute('''INSERT INTO students (first_name, last_name, date_of_birth, email, enrollment_date) VALUES
('John', 'Doe', '2000-01-15', 'john.doe@example.com', '2024-08-26'),
('Jane', 'Smith', '1999-05-22', 'jane.smith@example.com', '2024-08-26'),
('Alice', 'Johnson', '2001-07-30', 'alice.johnson@example.com', '2024-08-26'),
('Bob', 'Brown', '2000-11-05', 'bob.brown@example.com', '2024-08-26'),
('Charlie', 'Davis', '2002-02-14', 'charlie.davis@example.com', '2024-08-26'),
('Diana', 'Wilson', '1998-09-09', 'diana.wilson@example.com', '2024-08-26'),
('Eve', 'Taylor', '2001-12-25', 'eve.taylor@example.com', '2024-08-26'),
('Frank', 'Anderson', '1999-03-19', 'frank.anderson@example.com', '2024-08-26'),
('Grace', 'Thomas', '2000-08-08', 'grace.thomas@example.com', '2024-08-26'),
('Hank', 'Martinez', '2002-04-23', 'hank.martinez@example.com', '2024-08-26');
''')

##Display all records
print("Inserted records are:")

data=cursor.execute("select * from students")

for row in data:
    print(row)

connection.commit()
connection.close()