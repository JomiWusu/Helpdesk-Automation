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

class jiraDash:
    def __init__(self, root):
        self.root = root
        self.root.title("Jira Dashboard")
        self.root.geometry("720x480")
        set_appearance_mode("Light")
        
        #Create widget that contains
        self.top = CTkFrame(root, fg_color="white")
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
        
        # CTK label for the background top left
        self.logo_label = CTkLabel(
            self.top, 
            width=100, 
            height=50, 
            bg_color="white", 
            fg_color="white", 
            text="")
        self.logo_label.pack(side="left", padx=0, pady=0)

        # Add white text
        self.logo_text = CTkLabel(self.logo_label, text="Dashboard", font=("Arial", 16, "bold"), text_color="black")
        self.logo_text.place(relx=0.5, rely=0.5, anchor="center")  # Center the text

        #Create buttons using custom style
        self.close_btn = CTkButton(self.left, text="Close Resolved Tickets", command=self.close_tickets, **css_style)
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
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", msg + "\n")
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")

        #Formatting logger and creating a handler to send messaghes to gui
        handler = handler(self.log_area)
        format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(format)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
    def run_in_thread(self, func):
        threading.Thread(target=func).start()
    def close_tickets(self):
        print("Closed")



if __name__ == "__main__":
    root = CTk()
    gui = jiraDash(root)
    root.mainloop()