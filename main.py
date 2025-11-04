from jira import JIRA 
import schedule
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import logging
import time
import json
from customtkinter import *
import threading
from tkinter import messagebox
from win10toast import ToastNotifier

logging.basicConfig(
    filename = "jira_log",
    #Info level logs
    level = logging.INFO, 
    #format of logs time, level, message logged
    format = "%(asctime)s - %(levelname)s - %(message)s", 
)

#Variables to connect to jira api
email = ""
token = ""
url = ""

#Email Settings
email_server = "smtp.gmail.com"
email_port = 
email_sender = ""
email_pass = ""

try:

    #Opening and reading json file
    with open("emails.json", "r") as e:
        user_data = json.load(e)
except Exception as e:
    logging.critical(f"Error: {e.add_note}")
    #Stops program
    raise

#Project Key/Members
proj_key = ""
members = []

class jiraDash:
    def __init__(self, root):
        self.root = root
        self.root.title("Jira Dashboard")
        self.root.geometry("720x480")
        set_appearance_mode("Light")
        self.toaster = ToastNotifier()

        #Connecting to jira/gathering members
        self.jira_connect = None
        self.members = []

        self.total_tickets = 0
        self.unassigned_tickets = 0
        self.assigned_tickets = 0
        self.closed_tickets = 0

        self.ui_create()
        self.logging()
        self.connect_jira()
        self.ticket_monitoring()
        self.close_resolved_tickets_auto()
        self.remind_old_tickets()
        self.check_tickets()
        self.start_schedule()

    def start_schedule(self):
        #every 60s
        schedule.every(60).seconds.do(self.ticket_monitoring)
        schedule.every(1).hour.do(self.close_resolved_tickets_auto)
        schedule.every(1).hour.do(self.remind_old_tickets)
        schedule.every().sunday.at("00:00").do(self.send_weekly_analytics)
        schedule.every(1).minutes.do(self.check_tickets)

        #Run in thread so gui is responsive
        threading.Thread(target=self.schedule_loop, daemon=True).start()

    def schedule_loop(self):
        #Look and run for any pending schedules
        while True:
            schedule.run_pending()
            time.sleep(1)

    def ui_create(self):
        #Create widget that contains
        self.top = CTkFrame(root, fg_color="white", width=500)
        self.top.pack(side="top", fill="x")
        
        self.left = CTkFrame(root, fg_color="white", width = 400)
        self.left.pack(side= "left", fill = "y")

        self.main = CTkFrame(root, border_color="#95F985", border_width=5)
        self.main.pack(side="right", fill = "both", expand = True,)
        self.main_text = CTkTextbox(self.main)
        self.main_text.pack(fill = "both", expand=True, pady = 10, padx = 10)
        self.main_text.insert("0.0","Loaded \n")
        self.main_text.configure(state="disabled")

        #Buttons
        css_style = {
            "fg_color": "#95F985",
            "text_color": "black",
            "hover_color": "#e6e6e6",
            "corner_radius": 25,  
            "width": 160,
            "height": 50
        }
        

        # Left section of top bar (Dashboard text)
        self.dash_label = CTkLabel(self.top, text="Dashboard", font=("Arial", 16, "bold"), text_color="black")
        self.dash_label.pack(side="left", padx=20, pady=10)

        # Right section of top bar (Project key)
        self.project_label = CTkLabel(self.top, text=f"Project - {proj_key}", font=("Arial", 16, "bold"), text_color="black")
        self.project_label.pack(side="right", padx=20, pady=10)
        
        #Create buttons using custom style
        self.close_btn = CTkButton(self.left, text="Ticket Overview",  command=lambda: self.run_in_thread(self.gather_tickets), **css_style)
        self.close_btn.pack(pady=10, padx=10)

        self.close_btn = CTkButton(self.left, text="Set resolved tickets to closed",  command=lambda: self.run_in_thread(self.close_resolved_tickets_auto), **css_style)
        self.close_btn.pack(pady=10, padx=10)

        self.close_btn = CTkButton(self.left, text="Assign Unassigned Tickets",  command=lambda: self.run_in_thread(self.ticket_monitoring), **css_style)
        self.close_btn.pack(pady=10, padx=10)

        self.close_btn = CTkButton(self.left, text="Remind old tickets",  command=lambda: self.run_in_thread(self.remind_old_tickets), **css_style)
        self.close_btn.pack(pady=10, padx=10)
    
    def logging(self):
        class handler(logging.Handler):
            def __init__(self, text_widget):
                #initialize handler and call parent class
                super().__init__()
                #Setup textbox
                self.text_widget = text_widget
            def emit(self,record):
                #Configure logging messages
                msg = self.format(record)
                #Temporarily unlocks text box and add to it
                self.text_widget.after(0, self.append_msg, msg)
            def append_msg(self, msg):
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", msg + "\n")
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")

        #Formatting logger and creating a handler to send messaghes to gui
        txt_handler = handler(self.main_text)
        format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        txt_handler.setFormatter(format)
        logging.getLogger().addHandler(txt_handler)
        logging.getLogger().setLevel(logging.INFO)

    def connect_jira(self):
        #Connecting to jira
        self.jira_connect = JIRA(server = url, basic_auth = (email, token))
        logging.info("Connected to Jira")

        try:
             #Gather users in project
            users = self.jira_connect.search_users(query=' ',maxResults = 50) 

            for u in users:
                name = getattr(u, "displayName").lower().strip()
                #Filter usernames that consist of these strings
                if not any(word in name for word in ["automation", "jira", "atlassian", "alert", "trello", "slack", "proforma"]):
                    #Find the email using the account ID
                    email_address = next((user["email"] for user in user_data["members"] if user["id"] == u.accountId), None)
                    #Add member to array
                    self.members.append({f"name": u.displayName, "id": u.accountId, "email": email})
    
            logging.info(f"{len(self.members)} project members.")
        except Exception as e:
            logging.error(f"Failed to connect or get members: {e}")
            messagebox.showerror("Couldn't connect to jira")

    def get_least_busy(self):
        workload = {} #Array of work
        for member in self.members:
            try:
                #Search tickets for agent that hasn't been done using a jql query
                ticket = self.jira_connect.search_issues(f'assignee = "{member["id"]}" AND status != closed AND status != resolved')
                #Assign issues amount to angent
                workload[member["id"]] = len(ticket) 

            except Exception as e:
                logging.error(f"Error getting workload for {member["name"]} {e}")

        # least busy agent is the one with the least issues
        available_member = min(workload, key=workload.get) 
        #Returns the dictionairy of the member that is the least busy/available
        return next(member for member in self.members if member["id"] == available_member)
    
    def ticket_monitoring(self):
        logging.info("Started monitoring for new tickets")
        self.gather_tickets()

        #Check if no tickets available if there is assign least busy worker
        if len(self.unassigned_tickets) == 0:
            logging.info("No unassinged tickets found.")
            return
        else:
            for ticket in self.unassigned_tickets:
                try:
                    member = self.get_least_busy()
                    #Update the ticket to assign the least busy member to it
                    ticket.update(fields={"assignee": {"id": member["id"]}})
                    logging.info(f'Assigned {ticket.key} to {member["name"]}')
                except Exception as e:
                    logging.error(f"Failed to assign ticket {ticket.key} to {member["name"]}")
    

    def gather_tickets(self):
        try:
            #Returns all tickets (Unassigned, assigned, closed)
            self.total_tickets = self.jira_connect.search_issues(f'project={proj_key}')
            self.unassigned_tickets = self.jira_connect.search_issues(f'project={proj_key} AND assignee is EMPTY AND status != closed AND status !=resolved')
            self.assigned_tickets = self.jira_connect.search_issues(f'project={proj_key} AND assignee is not EMPTY')
            self.closed_tickets = self.jira_connect.search_issues(f'project={proj_key} AND status = close')
            logging.info(f"Total Tickets - {len(self.total_tickets)}")
            logging.info(f"Unassigned Tickets - {len(self.unassigned_tickets)}")
            logging.info(f"Assigned Tickets - {len(self.assigned_tickets)}")
            logging.info(f"Closed Tickets - {len(self.closed_tickets)}")
            return members
        except Exception as e:
            logging.error(f"Error gathering tickets {e}")

    def send_email(self,reciever, subject, body):
        #Email formatting using MIMEText for readability in the email 
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_sender
        msg["To"] = reciever

        try:
            #Connects to gmail login to email and sends message close connection
            with smtplib.SMTP(email_server, email_port) as server:
                server.starttls()
                server.login(email_sender, email_pass)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending email {e}")
    
    def remind_old_tickets(self):
        try:
            #Searches for tickets that are not closed/resolved
            jquery = f'project={proj_key} AND status not in (Resolved, Closed)'
            tickets = self.jira_connect.search_issues(jquery)

            for ticket in tickets:
                #Gets the time of when the ticket was last updated
                last_updated_ticket = datetime.strptime(ticket.fields.updated[:19], "%Y-%m-%dT%H:%M:%S")

                #If the time of when the ticket was last updated is over 24 Hours remind assignee
                if datetime.now() - last_updated_ticket > timedelta(hours=24):
                    #Gets ticket assignee email address and sends reminder email
                    user = self.jira_connect.user(f"{ticket.fields.assignee.accountId}")
                    reciever_email = next((member["email"] for member in self.members if user.accountId == member["id"]), None)
                    subject = f"Reminder for ticket {ticket.key}. Last updated {last_updated_ticket}."
                    body = (
                        f"{ticket.fields.summary} has been not recently updated for 24 hours or more please attend."
                        f"{self.jira_connect.server_url}/browse/{ticket.key} Please update!"
                    )
                    self.send_email(reciever_email, subject, body)
                    self.jira_connect.add_comment(ticket, "Ticket has been inactive for over 24 hours. Please attend")
                    logging.info(f"Sent email/added reminder to ticket{ticket.key}")

        except Exception as e:
            logging.error(f"Error sending old ticket reminders: {e}")
    
    def close_resolved_tickets_auto(self):
        try:
            #Jquery to check if the ticket is resolved or not
            jquery = f'project={proj_key} AND status ="Resolved"'
            resolved_ticket = self.jira_connect.search_issues(jquery)

            if len(resolved_ticket) > 0:
                for ticket in resolved_ticket:

                    #Checks if ticket has a resolved status
                    #Gets the time of the resolved date and using the datetime strptime method it converts into a specific format
                    resolved_date = datetime.strptime(ticket.fields.statuscategorychangedate[:10], "%Y-%m-%d")
                
                    #if the date of the resolved date has exceeded 2 day it will close
                    if datetime.now() - resolved_date > timedelta(days=2):
                        
                        #Gets all transitions in the ticket EX Start Progress - In progress etc
                        transitions = self.jira_connect.transitions(ticket)
                        close_ticket = next((t for t in transitions if t['name'].lower() == 'close'))
                        
                        #Checks if there is a resolved transition and closes ticket/sends email
                        if close_ticket:
                            user = self.jira_connect.user(f"{ticket.fields.assignee.accountId}")
                            reciever_email = next((member["email"] for member in self.members if user.accountId == member["id"]), None)
                            subject = f"Ticket {ticket.key} has been automatically closed."

                            body = (
                                f"{ticket.fields.summary} has been closed after being left on resolved for more than 2 days"
                                f"{self.jira_connect.server_url}/browse/{ticket.key}"
                            )

                            self.send_email(reciever_email, subject, body)
                            #Moves ticket from one status to done status and closes ticket
                            self.jira_connect.transition_issue(ticket, close_ticket['id'])
                            logging.info(f"Sent Email (Ticket {ticket.key} left resolved for more than 2 days)")
            else:
                logging.info("No resolved tickets left for more than 2 days")
        except Exception as e:
            logging.error(f"Error closing resolved tickets: {e}")
        
    def send_weekly_analytics(self):
    
        sunday_date = datetime.now()
        monday_date = sunday_date - timedelta(days=6)
        monday_date = monday_date.strftime("%Y-%m-%d")
        sunday_date = sunday_date.strftime("%Y-%m-%d")

        logging.info("Generating Weekly Report")
        #list of unassigned tickets, resolved tickets, created tickets
        tickets_resolved = self.jira_connect.search_issues(f'project={proj_key} AND statusCategory = done AND created  >= "{monday_date}" AND created <= {sunday_date} ')
        tickets_created = self.jira_connect.search_issues(f'project={proj_key} AND created >= "{monday_date}" AND created <= "{sunday_date}"')
        tickets_opened = self.jira_connect.search_issues(f'project={proj_key} AND status != Done')

        #Create subject and body
        subject = f"{proj_key} Weekly ticket summary {monday_date} -> {sunday_date}"
        lines = [
            f"Tickets created: {len(tickets_created)}\n",
            f"Tickets Resolved: {len(tickets_resolved)}\n",
            f"Tickets Open: {len(tickets_opened)}\n"
        ]
        
        lines.append("Ticket Summary")

        for ticket in tickets_created:
            lines.append(f"- {ticket.key}: {ticket.fields.summary} (Created: {ticket.fields.created})")

        #Joins each string in list and adds a new line
        body = "\n".join(lines)
        logging.info("Sent weekly email report")

        self.send_email("wusujomi1@gmail.com", subject, body)

    def check_tickets(self):
        try:
            #Show Tickets a minute ago since scheduler runs every minute
            min_ago = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
            #Find newly created tickets
            jq = f'project={proj_key} AND created >= "{min_ago}"'
            tickets = self.jira_connect.search_issues(jq)

            for ticket in tickets:
                self.ticket_noti(ticket)
                logging.info(f"New Ticket Found")
        
        except Exception as e:
            logging.error(f"Error checking for new tickets: {e}")

    def ticket_noti(self, ticket):
        try:
            #Sending Windows Notifcation for 6 seconds
            title = f"(NEW) Ticket: {ticket.key}"
            summary = f"Ticket: {ticket.key} Summary - {ticket.fields.summary}" or "No Summary"
            self.toaster.show_toast(title, summary, duration=6, threaded=True)
            logging.info(f"Notification sent {ticket.key}")
        except Exception as e:
            logging.error(f"Failed to show notification: {e}")        
    
    def run_in_thread(self, func):
        threading.Thread(target=func).start()
    

    def close_tickets(self):
        print("Closed")
        
if __name__ == "__main__":
    root = CTk()
    gui = jiraDash(root)
    root.mainloop()
