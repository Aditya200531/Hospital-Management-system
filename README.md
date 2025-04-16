# Hospital Management System

A comprehensive hospital management system built with Streamlit, featuring patient and doctor management, appointment scheduling, medical records, and an AI-powered chatbot. This system modernizes hospital operations by providing a seamless interface for patients, doctors, and administrators.

## 🚀 Features

### Patient Features
- **User Management**
  - Secure registration and login system
  - Profile management
  - Password reset functionality
- **Appointment Management**
  - Book appointments with preferred doctors
  - View upcoming and past appointments
  - Cancel or reschedule appointments
  - Receive appointment reminders
- **Medical Records**
  - View personal medical history
  - Access test results and reports
  - Download medical documents
  - Track prescription history
- **Communication**
  - Direct messaging with doctors
  - Receive notifications for appointments
  - View hospital announcements

### Doctor Features
- **Dashboard**
  - Daily appointment schedule
  - Patient queue management
  - Quick access to patient records
- **Patient Management**
  - View patient medical history
  - Add new medical records
  - Update patient status
  - Manage prescriptions
- **Appointment Management**
  - View and manage appointments
  - Set availability
  - Handle emergency cases
- **Medical Records**
  - Create and update patient records
  - Upload test results
  - Generate prescriptions
  - Document treatment plans

### Admin Features
- **System Management**
  - User management and permissions
  - Department management
  - Staff scheduling
  - System configuration
- **AI-Powered Chatbot**
  - 24/7 administrative support
  - Automated responses to common queries
  - Document processing and analysis
  - Data insights and reporting
- **Analytics**
  - Patient statistics
  - Appointment trends
  - Resource utilization
  - Performance metrics

## 🛠️ Technical Stack

### Frontend
- **Streamlit**: Modern web interface
- **Custom Components**: Enhanced UI elements
- **Responsive Design**: Mobile-friendly interface

### Backend
- **MySQL**: 
  - Patient information
  - Appointment scheduling
  - User management
  - Department details
- **MongoDB**:
  - Medical records
  - Patient history
  - Prescriptions
  - Chat logs

### AI Integration
- **Groq API**: 
  - Advanced language processing
  - Real-time responses
  - Context-aware interactions
- **Google Generative AI**:
  - Document analysis
  - Text processing
  - Data extraction
- **LangChain**:
  - Document processing
  - Information retrieval
  - Context management
- **FAISS**:
  - Vector storage
  - Similarity search
  - Fast retrieval

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- MongoDB 4.4 or higher
- 4GB RAM minimum
- 10GB free disk space

### Required Python Packages
```bash
streamlit>=1.24.0
pymysql>=1.0.2
pymongo>=4.3.3
tensorflow>=2.12.0
numpy>=1.24.0
pillow>=9.5.0
groq>=0.1.0
langchain>=0.0.200
langchain-groq>=0.0.1
langchain-google-genai>=0.0.1
faiss-cpu>=1.7.4
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=hospital_db
MONGODB_URI=mongodb://localhost:27017
```

### 5. Database Setup
#### MySQL Setup
```sql
-- Run the schema.sql file
mysql -u root -p < schema.sql
```

#### MongoDB Setup
```bash
# Start MongoDB service
sudo service mongod start
```

## 💾 Database Structure

### MySQL Tables
1. **Patients**
   - PatientID (Primary Key)
   - Personal Information
   - Contact Details
   - Medical History

2. **Doctors**
   - DoctorID (Primary Key)
   - Professional Details
   - Specialization
   - Schedule

3. **Appointments**
   - AppointmentID (Primary Key)
   - PatientID (Foreign Key)
   - DoctorID (Foreign Key)
   - Date and Time
   - Status

4. **Users**
   - UserID (Primary Key)
   - Credentials
   - Role
   - Permissions

### MongoDB Collections
1. **MedicalRecords**
   - Patient Information
   - Diagnosis
   - Treatment Plans
   - Test Results

2. **Prescriptions**
   - Medication Details
   - Dosage
   - Duration
   - Instructions

## 🔒 Security Features

- **Authentication**
  - Secure password hashing
  - Session management
  - Two-factor authentication (optional)
- **Authorization**
  - Role-based access control
  - Permission management
  - Activity logging
- **Data Protection**
  - Encrypted storage
  - Secure transmission
  - Regular backups
- **Compliance**
  - HIPAA compliance
  - Data privacy
  - Audit trails

## 📱 Usage Guide

### Starting the Application
```bash
streamlit run app.py
```

### Accessing the System
1. Open your browser and navigate to `http://localhost:8501`
2. Choose your role:
   - Patient: Register or login
   - Doctor: Professional login
   - Admin: Administrative access

### Common Operations
1. **Patient Registration**
   - Fill in personal details
   - Create account
   - Verify email (if enabled)

2. **Booking Appointments**
   - Select department
   - Choose doctor
   - Pick available slot
   - Confirm booking

3. **Managing Records**
   - View medical history
   - Upload documents
   - Track prescriptions

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**
   - Check MySQL/MongoDB service status
   - Verify credentials
   - Ensure proper network access

2. **API Integration**
   - Validate API keys
   - Check rate limits
   - Monitor usage quotas

3. **Performance Issues**
   - Clear cache
   - Check system resources
   - Optimize database queries

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Maintain backward compatibility


