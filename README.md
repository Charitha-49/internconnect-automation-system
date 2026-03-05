# internconnect-automation-system
A backend automation system that tracks internship deadlines and sends automated email alerts to subscribed users using Streamlit, MySQL, and n8n workflow automation.
Automated Internship Notification System
# Overview
The Automated Internship Notification System is a backend-focused application that helps students stay updated about internship deadlines. The system allows users to subscribe to internships and automatically receive reminder emails before the deadline.

This project demonstrates backend development, database integration, and workflow automation using n8n.
Instead of manually checking deadlines, the system automatically scans the database daily and sends reminder emails to subscribed users.

# Key Features

 ## User Features
    •	User signup and login authentication
    •	Browse available internships
    •	Search internships by title
    •	Subscribe to internship notifications
    •	Unsubscribe anytime
    •	View subscribed internships in profile 
    •	Change account password
      
  ## Admin Features
    •	Post new internships
    •	View all internships
    •	Delete internships
    •	Manage internship listings

  ## Automation Features
    •	Automated workflow using n8n
    •	Daily deadline scanning
    •	Email notifications sent automatically
    •	MySQL database integration
    •	Cron based scheduling

# System Architecture
 •	Frontend:Streamlit Web Application
 •	Backend:Python,MySQL Database
 •	Automation Layer:n8n Workflow Automation
 •	Notification Service:Gmail API via n8n
 •	Workflow:
  •	Admin posts internship
  •	Users subscribe to internships
  •	n8n workflow runs daily
  •	System checks upcoming deadlines
  •	Emails are automatically sent to subscribed users

    
# Technology Stack
  Frontend
 Streamlit
  Backend
    Python
  Database
    MySQL
  Automation
    n8n Workflow Automation 
  Email Service
    Gmail Node in n8n
  Containerization
    Docker
  
# n8n Automation Workflow

  The automation workflow runs using a Cron trigger.
  Workflow steps:
    •	Cron Trigger
    •	Runs daily at scheduled time
    •	MySQL Query
    •	Fetch internships with deadlines approaching
    •	Join Query
    •	Match internships with subscribed users
    •	Gmail Node
    •	Send reminder emails
    •	Update Query
    •	Mark internship as notified
    This ensures users receive only one reminder email.

# Installation Guide
Clone Repository
 git clone https://github.com/Charitha-49/internconnect-automation-system.git
Install Dependencies
  pip install streamlit mysql-connector-python
Run Application
  streamlit run app.py
Run n8n using Docker
  docker-compose up -d
Open n8n:
  http://localhost:5678
Author
  Developed by Sri Charitha
  Focused on backend development, workflow automation, and scalable systems.
License
  This project is for educational and demonstration purposes.

