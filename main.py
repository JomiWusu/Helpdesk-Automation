from jira import JIRA 

#Variables to connect to jira api
email = "wusujomi1@gmail.com"
token = "ATATT3xFfGF0YCpR4jyAHN4lA0Ly6fx_9xihlB_OlU31yBx3-r2rzbLMET-dBBMLln_mPLwf9I4NRpAUoRuAY6QeCq812ArwysLc2nMvvVj8HQSwxsg--c5fm1AYuZ3DTQmvT82GOa8wp7idMawzfPWoauCQAohl62iaBNFV-jLsFWfpBAiDn48=065AACE1"
url = "https://wusujomi1.atlassian.net"

#Connecting
jira_connect = JIRA(server = url, basic_auth = (email, token))
print ("Connected")

#Project Key/Members
proj_key = "SUP"
members = []

#Gather users in project
users = jira_connect.search_users(query=' ',maxResults = 50) 

for u in users:
    name = getattr(u, "displayName").lower().strip()
    #Check if user name consists of these strings
    if not any(word in name for word in ["automation", "jira", "atlassian", "alert", "trello", "slack", "proforma"]):
        #Add member to array
        members.append({f"name": u.displayName, "id": u.accountId})
    
print(f'Members = {len(members)}')

def get_least_busy(jira, members):
    workload = {} #Array of work
    for member in members:
        #Search tickets for agent that hasn't been done using a jql query
        issues = jira.search_issues(f'assignee = "{member["id"]}" AND status != Done')
        #Assign issues amount to angent
        workload[member["id"]] = len(issues) 

    # least busy agent is the one with the least issues
    available_member = min(workload, key=workload.get) 
    #Returns the dictionairy of the member that is the least busy/available
    return next(member for member in members if member["id"] == available_member)

def search_unassigned_issue(key, jira):
    #Returns all tickets
    return jira.search_issues(f'project={key} AND assignee is EMPTY AND status != Done')

tickets = search_unassigned_issue(proj_key, jira_connect)
print(f'Ticket Amount = {len(tickets)}')

if tickets == 0:
     print("No Tickets")
else:
     for issue in search_unassigned_issue(proj_key, jira_connect):
        member = get_least_busy(jira_connect,members)
        issue.update(fields={"assignee": {"id": member["id"]}})
        print(f'Assigned {issue.key} to {member["name"]}')
