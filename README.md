# Automation Dashboard

**Python / Jira API / SMTP / CustomTkinter / Win10toast / Schedule / Logging**

---

## Summary  
Automation Dashboard for Jira — a desktop application that connects to Atlassian Jira to help IT support teams manage tickets more efficiently.  
It automates helpdesk operations like ticket monitoring, inactivity reminders, workload balancing, and weekly analytics.  
This application simulates real-world IT automation used in service desk environments.  

---

## Features  
- **Automatic Ticket Assignment** – Finds unassigned issues and assigns them to the least busiest member.  
- **Inactive Ticket Reminders** – Detects tickets untouched for 24 hours and emails reminders automatically.  
- **Automatically Close Resolved Tickets** – Closes tickets left in the *Resolved* state for more than 2 days.  
- **Real-Time Notifications** – Displays Windows toast alerts when new tickets are created.  
- **Thread-Safe Scheduling** – Uses background threads to keep the GUI responsive.  
- **Custom GUI Dashboard** – Built with CustomTkinter, showing logs, buttons, and live actions.  
- **Weekly Analytics Report** – Sends an email summary every Sunday.  

---

## Instructions  
1. **Clone Repo.**  
2. **Install dependencies:**  
   ```bash
   pip install jira schedule smtplib customtkinter win10toast
