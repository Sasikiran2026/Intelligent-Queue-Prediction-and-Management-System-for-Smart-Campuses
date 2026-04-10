# Intelligent Queue Prediction and Management System for Smart Campuses
Project Link : https://intelligent-queue-prediction-and.onrender.com
An intelligent queue management system designed specifically for smart campuses that predicts wait times and optimizes resource allocation using AI/ML techniques.

## Overview

This system helps manage queues efficiently across campus departments by:
- **Token-based Queue Management**: Generate and track tokens for students
- **Priority Queue System**: Support for priority and normal queue items
- **AI-Powered Analytics**: Intelligent predictions and insights on queue patterns
- **Real-time Live Display**: Monitor queue status in real-time
- **Admin Dashboard**: Complete control and visibility of queue operations
- **Student Dashboard**: Personal queue status and analytics for students
- **Automated Monitoring**: Alert systems and automatic queue management

## Features

### Admin Features
- **Admin Dashboard**: Manage tokens, view current queue, and perform queue operations
- **Generate Tokens**: Create new tokens for students with priority options
- **Call Next**: Process the next token in queue
- **Advanced Analytics**: View statistics including:
  - Total users and tokens
  - Peak hours analysis
  - Queue trends and patterns
  - Historical data archival
- **Live Display**: Real-time queue display for public viewing

### Student Features
- **Student Dashboard**: Track personal queue status and position
- **Registration & Login**: Secure authentication system
- **Queue Status**: Real-time updates on queue position and wait time
- **Profile Management**: Manage personal information

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Tailwind CSS
- **Charts & Visualization**: Chart.js
- **AI/ML**: Custom AI model for predictions

## Project Structure

```
Intelligent_Queue_System/
├── app.py                 # Main Flask application
├── ai_model.py           # AI prediction model
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── database/             # Database files
├── instance/             # Flask instance folder
├── static/
│   ├── css/
│   │   └── style.css    # Global styles
│   └── js/              # JavaScript files
└── templates/           # HTML templates
    ├── index.html
    ├── login.html
    ├── register.html
    ├── admin.html
    ├── admin_dashboard.html
    ├── admin_analytics.html
    ├── student_dashboard.html
    ├── student_profile.html
    ├── live_display.html
    └── live_queue.html
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sasikiran2026/Intelligent-Queue-Prediction-and-Management-System-for-Smart-Campuses.git
   cd Intelligent_Queue_System
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Usage

### Admin Access
- Navigate to the admin dashboard
- Generate new tokens for students
- Monitor queue status in real-time
- View detailed analytics and historical data
- Manage priority queues

### Student Access
- Register for an account
- Login with credentials
- View personal queue status
- Check position and estimated wait time
- Access personal analytics dashboard
- Update profile information

## Database Schema

### Users Table
- `id`: Unique identifier
- `name`: User full name
- `email`: Email address
- `password`: Hashed password
- `phone`: Contact number
- `role`: User role (admin/student)

### Queue Table
- `id`: Token ID
- `token`: Token number
- `name`: Student name
- `department`: Department name
- `status`: Queue status (Waiting/Served)
- `time`: Timestamp
- `date`: Date of token generation

### Queue Archive Table
- Historical data for reporting and analytics

## Key Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/admin` | GET | Admin dashboard |
| `/admin_analytics` | GET | Analytics page |
| `/student` | GET, POST | Student dashboard |
| `/call_next` | GET | Process next token |
| `/live` | GET | Live queue display |
| `/logout` | GET | User logout |

## Security Features

- Password encryption for secure storage
- Session-based authentication
- Role-based access control (Admin/Student)
- Input validation and sanitization

## Future Enhancements

- SMS/Email notifications for queue status
- Mobile application
- Advanced ML predictions for queue wait times
- Integration with campus systems
- Department-specific queue management
- Facial recognition for queue bypass

## Support

For issues, questions, or suggestions, please contact the development team or open an issue on GitHub.

## License

This project is under development. All rights reserved.

## Author

**Sasi Kiran**

## Acknowledgments

Built as an intelligent solution for campus queue management and resource optimization.
