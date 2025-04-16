import streamlit as st
import pymysql
from pymongo import MongoClient
from datetime import datetime
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from groq import Groq
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# API Keys and Environment Setup
GROQ_API_KEY = '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'
GOOGLE_API_KEY = 'AIzaSyBkoorRTaH08H3RFIft4ug6bT1ABexXswI'
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")
schema = """
                -- Patients Table
                CREATE TABLE IF NOT EXISTS Patients (
                    PatientID INT PRIMARY KEY AUTO_INCREMENT,
                    FirstName VARCHAR(50),
                    LastName VARCHAR(50),
                    Age INT,
                    Gender CHAR(1),
                    ContactNumber VARCHAR(15),
                    Address VARCHAR(100)
                );

                -- Doctors Table
                CREATE TABLE IF NOT EXISTS Doctors (
                    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
                    FirstName VARCHAR(50),
                    LastName VARCHAR(50),
                    Specialty VARCHAR(50),
                    ContactNumber VARCHAR(15),
                    DepartmentID INT
                );

                -- Departments Table
                CREATE TABLE IF NOT EXISTS Departments (
                    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
                    DepartmentName VARCHAR(50),
                    Floor INT
                );

                -- Appointments Table
                CREATE TABLE IF NOT EXISTS Appointments (
                    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
                    PatientID INT,
                    DoctorID INT,
                    Date DATE,
                    Time TIME,
                    Reason VARCHAR(100),
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
                );

                -- Users Table
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('patient', 'doctor', 'admin') NOT NULL,
                    PatientID INT NULL,
                    DoctorID INT NULL,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
                );
                """
# Note: MedicalRecords are stored in MongoDB.

# MySQL Database Connection
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Adi2005ale@',
            database='Hospital7'
        )
        return connection
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# MongoDB Connection (for MedicalRecords)
def get_mongo_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Hospital6"]
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = "Login"

# Login function (for existing users)
def login(username, password):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM Users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    return True
                return False
        finally:
            connection.close()
    return False

# Registration function (for new patients)
def register_patient():
    st.title("Patient Registration")
    with st.form("registration_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        gender = st.selectbox("Gender", ["M", "F", "O"])
        contact = st.text_input("Contact Number")
        address = st.text_area("Address")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                conn = get_db_connection()
                if conn is not None:
                    try:
                        with conn.cursor() as cursor:
                            # Insert patient data
                            insert_patient_query = """
                                INSERT INTO Patients (FirstName, LastName, Age, Gender, ContactNumber, Address)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_patient_query, (first_name, last_name, age, gender, contact, address))
                            patient_id = cursor.lastrowid
                            # Insert corresponding user account
                            insert_user_query = """
                                INSERT INTO Users (username, password, role, PatientID)
                                VALUES (%s, %s, 'patient', %s)
                            """
                            cursor.execute(insert_user_query, (username, password, patient_id))
                            conn.commit()
                            st.success("Registration successful! You can now log in.")
                    except Exception as e:
                        st.error(f"Error during registration: {e}")
                    finally:
                        conn.close()
    # Button at the bottom to switch back to Login mode
    if st.button("Already have an account? Login"):
        st.session_state['auth_mode'] = "Login"
        try:
            st.query_params(dummy=str(datetime.now().timestamp()))
        except Exception:
            pass

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    try:
        st.query_params(dummy=str(datetime.now().timestamp()))
    except Exception:
        pass

def view_patient_details(patient_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (patient_id,))
                patient = cursor.fetchone()
                if patient:
                    st.header("My Details")
                    st.write(f"**Name:** {patient[1]} {patient[2]}")
                    st.write(f"**Age:** {patient[3]}")
                    st.write(f"**Gender:** {patient[4]}")
                    st.write(f"**Contact:** {patient[5]}")
                    st.write(f"**Address:** {patient[6]}")
                else:
                    st.error("Patient details not found.")
        finally:
            connection.close()

def view_patient_appointments(patient_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT a.AppointmentID, d.FirstName, d.LastName, a.Date, a.Time, a.Reason 
                    FROM Appointments a
                    JOIN Doctors d ON a.DoctorID = d.DoctorID
                    WHERE a.PatientID = %s
                    ORDER BY a.Date, a.Time
                """, (patient_id,))
                appointments = cursor.fetchall()
                st.header("My Appointments")
                if appointments:
                    for appt in appointments:
                        with st.expander(f"Appointment with Dr. {appt[1]} {appt[2]} on {appt[3]}"):
                            st.write(f"**Time:** {appt[4]}")
                            st.write(f"**Reason:** {appt[5]}")
                else:
                    st.info("No appointments scheduled.")
        finally:
            connection.close()

def view_patient_medical_records(patient_id):
    db = get_mongo_connection()
    if db is not None:
        try:
            records = list(db.MedicalRecords.find({"PatientID": patient_id}))
            st.header("My Medical Records")
            if records:
                for record in records:
                    doctor_id = record.get("DoctorID")
                    connection = get_db_connection()
                    doctor_name = "Unknown Doctor"
                    if connection is not None:
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("SELECT FirstName, LastName FROM Doctors WHERE DoctorID = %s", (doctor_id,))
                                doctor = cursor.fetchone()
                                if doctor:
                                    doctor_name = f"Dr. {doctor[0]} {doctor[1]}"
                        finally:
                            connection.close()
                    record_date = record.get("Date")
                    if isinstance(record_date, datetime):
                        record_date_str = record_date.strftime("%Y-%m-%d")
                    else:
                        record_date_str = str(record_date)
                    with st.expander(f"Medical Record from {doctor_name} on {record_date_str}"):
                        st.write(f"**Diagnosis:** {record.get('Diagnosis')}")
                        st.write(f"**Treatment:** {record.get('Treatment')}")
            else:
                st.info("No medical records found.")
        except Exception as e:
            st.error(f"Error retrieving medical records: {e}")
    else:
        st.error("Could not connect to MongoDB.")

def book_new_appointment(patient_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DoctorID, FirstName, LastName, Specialty FROM Doctors")
                doctors = cursor.fetchall()
                doctor_options = {f"Dr. {d[1]} {d[2]} ({d[3]})": d[0] for d in doctors}
                st.header("Book New Appointment")
                with st.form("appointment_form"):
                    doctor = st.selectbox("Select Doctor", options=list(doctor_options.keys()))
                    date = st.date_input("Date", min_value=datetime.now().date())
                    time = st.time_input("Time")
                    reason = st.text_area("Reason for Appointment")
                    if st.form_submit_button("Book Appointment"):
                        doctor_id = doctor_options[doctor]
                        cursor.execute("""
                            INSERT INTO Appointments (PatientID, DoctorID, Date, Time, Reason)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (patient_id, doctor_id, date, time.strftime('%H:%M:%S'), reason))
                        connection.commit()
                        st.success("Appointment booked successfully!")
        finally:
            connection.close()

def view_doctor_details(doctor_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Doctors WHERE DoctorID = %s", (doctor_id,))
                doctor = cursor.fetchone()
                if doctor:
                    st.header("My Details")
                    st.write(f"**Name:** {doctor[1]} {doctor[2]}")
                    st.write(f"**Specialty:** {doctor[3]}")
                    st.write(f"**Contact:** {doctor[4]}")
                else:
                    st.error("Doctor details not found.")
        finally:
            connection.close()

def view_doctor_appointments(doctor_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT a.AppointmentID, p.FirstName, p.LastName, a.Date, a.Time, a.Reason 
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    WHERE a.DoctorID = %s
                    ORDER BY a.Date, a.Time
                """, (doctor_id,))
                appointments = cursor.fetchall()
                st.header("My Appointments")
                if appointments:
                    for appt in appointments:
                        with st.expander(f"Appointment with {appt[1]} {appt[2]} on {appt[3]}"):
                            st.write(f"**Time:** {appt[4]}")
                            st.write(f"**Reason:** {appt[5]}")
                else:
                    st.info("No appointments scheduled.")
        finally:
            connection.close()

def add_medical_record(doctor_id):
    connection = get_db_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT PatientID, FirstName, LastName FROM Patients")
                patients = cursor.fetchall()
                patient_options = {f"{p[1]} {p[2]}": p[0] for p in patients}
                st.header("Add Medical Record")
                with st.form("medical_record_form"):
                    patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
                    diagnosis = st.text_area("Diagnosis")
                    treatment = st.text_area("Treatment")
                    date = st.date_input("Date", datetime.now().date())
                    if st.form_submit_button("Submit"):
                        patient_id = patient_options[patient]
                        db = get_mongo_connection()
                        if db is not None:
                            if not isinstance(date, datetime):
                                date = datetime.combine(date, datetime.min.time())
                            record = {
                                "PatientID": patient_id,
                                "DoctorID": doctor_id,
                                "Diagnosis": diagnosis,
                                "Treatment": treatment,
                                "Date": date
                            }
                            db.MedicalRecords.insert_one(record)
                            st.success("Medical record added successfully!")
                        else:
                            st.error("Could not connect to MongoDB.")
        finally:
            connection.close()

def admin_chatbot():
    st.header("Admin Chatbot")
    query = st.text_input("Enter your query:")
    if st.button("Submit"):
        prompt = ChatPromptTemplate.from_template(f"""
                    Here is the schema for a database:
                    {schema}
                    Based on this scheme, write the SQL query to achieve the following:
                    {query}
                    Please provide a response to the following question based on your general knowledge.
                    Give only the SQL query as output and nothing else. Query should be simple and effective.
                """)
        try:
            messages = prompt.format_messages(input=prompt)
            response = llm.invoke(messages)
            generated_query = response.content
            generated_query = generated_query.replace('```', '').strip()
            st.write("Generated SQL Query:")
            st.code(generated_query)
            connection = get_db_connection()
            if connection is not None:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(generated_query)
                        if generated_query.strip().lower().startswith("select"):
                            results = cursor.fetchall()
                            if results:
                                st.write("Query Results:")
                                st.table(results)
                            else:
                                st.info("No results returned from the query.")
                        else:
                            connection.commit()
                            st.success("Query executed successfully!")
                except Exception as e:
                    st.error(f"Error executing query: {str(e)}")
                finally:
                    connection.close()
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

def main():
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Select Option", ["Login", "Register"],
                             index=0 if st.session_state['auth_mode'] == "Login" else 1)
        st.session_state['auth_mode'] = auth_mode
        if auth_mode == "Login":
            st.title("Hospital Management System - Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                if submit_button:
                    if login(username, password):
                        st.success("Login successful!")
                        try:
                            st.query_params(dummy=str(datetime.now().timestamp()))
                        except Exception:
                            pass
                    else:
                        st.error("Invalid username or password")
        elif auth_mode == "Register":
            register_patient()
    else:
        st.sidebar.button("Logout", on_click=logout)
        user = st.session_state['user']
        user_dict = {
            'user_id': user[0],
            'username': user[1],
            'password': user[2],
            'role': user[3],
            'PatientID': user[4],
            'DoctorID': user[5]
        }
        st.title(f"Welcome, {user_dict['username']} ({user_dict['role'].capitalize()})")
        if user_dict['role'] == 'doctor':
            doctor_id = user_dict['DoctorID']
            tabs = st.tabs(["My Details", "Appointments", "Add Medical Record"])
            with tabs[0]:
                view_doctor_details(doctor_id)
            with tabs[1]:
                view_doctor_appointments(doctor_id)
            with tabs[2]:
                add_medical_record(doctor_id)
        elif user_dict['role'] == 'patient':
            patient_id = user_dict['PatientID']
            tabs = st.tabs(["My Details", "Appointments", "Medical Records", "Book Appointment"])
            with tabs[0]:
                view_patient_details(patient_id)
            with tabs[1]:
                view_patient_appointments(patient_id)
            with tabs[2]:
                view_patient_medical_records(patient_id)
            with tabs[3]:
                book_new_appointment(patient_id)
        elif user_dict['role'] == 'admin':
            tabs = st.tabs(["Admin Chatbot"])
            with tabs[0]:
                admin_chatbot()

if __name__ == "__main__":
    main()
