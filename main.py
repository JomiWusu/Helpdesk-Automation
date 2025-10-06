from jira import JIRA 

#Variables to connect to jira api
email = "wusujomi1@gmail.com"
token = "ATATT3xFfGF0YCpR4jyAHN4lA0Ly6fx_9xihlB_OlU31yBx3-r2rzbLMET-dBBMLln_mPLwf9I4NRpAUoRuAY6QeCq812ArwysLc2nMvvVj8HQSwxsg--c5fm1AYuZ3DTQmvT82GOa8wp7idMawzfPWoauCQAohl62iaBNFV-jLsFWfpBAiDn48=065AACE1"
url = "https://wusujomi1.atlassian.net"

#Connecting
jira_connect = JIRA(server = url, basic_auth = (email, token))
print ("Connected")