from jira import JIRA 

#Variables to connect to jira api
email = "wusujomi1@gmail.com"
token = "ATATT3xFfGF0YCpR4jyAHN4lA0Ly6fx_9xihlB_OlU31yBx3-r2rzbLMET-dBBMLln_mPLwf9I4NRpAUoRuAY6QeCq812ArwysLc2nMvvVj8HQSwxsg--c5fm1AYuZ3DTQmvT82GOa8wp7idMawzfPWoauCQAohl62iaBNFV-jLsFWfpBAiDn48=065AACE1"
url = "https://wusujomi1.atlassian.net"

#Connecting
jira_connect = JIRA(server = url, basic_auth = (email, token))
print ("Connected")

#Project Key
proj_key = "SUP"

"""
testIssues = [
    {"summary": "Can't log in", "description": "User cannot log in to email", "issuetype": "Submit a request or incident", "priority": "High"},
    {"summary": "Printer not working", "description": "Office printer jammed", "issuetype": "Submit a request or incident", "priority": "High"},
    {"summary": "Software install request", "description": "Install Microsoft Teams", "issuetype": "Submit a request or incident", "priority": "High"},
]


for t in testIssues:
    issue = jira_connect.create_issue(
        project=proj_key,
        summary=t["summary"],
        description=t["description"],
        issuetype={"name": t["issuetype"]},
        priority={"name": t["priority"]}
    )
    print(f"Created ticket {issue.key}")
"""

members = []

users = jira_connect.search_users(query=' ',maxResults = 50) #Gather users in project

for u in users:
    name = getattr(u, "displayName").lower().strip()
    if not any(word in name for word in ["automation", "jira", "atlassian", "alert", "trello", "slack", "Proforma"]): #Check if user name consists of these strings
        #Add members to array
        members.append(f"name: {u.displayName}") 
        members.append(f"id: {u.accountId}")
    

    get_least_busy(jira_connect, members)

def get_least_busy(jira, agents):
    workload = {} #Array of work
    for agent in agents:
        issues = jira.search_issues(f'assignee={agent["id"]} AND status != Done') #Search tickets for agent that hasn't been done
        workload[agent["id"]] = len(issues) #Assign issues amount to angent
    available_angent = min(workload) # least busy agent is the one with the least issues
    return available_angent 