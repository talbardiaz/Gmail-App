# Gmail-App

This script automatically downloads and unpacks specific business emails into a specified Google Drive folder utilizing both the Google Gmail API and the Google Drive API. 
The main file initially calls the service file and its function that constructs any Google API service such as the Gmail service and Drive service that is being used in this 
script. This then creates two separate tokens that save the login info for the Gmail account and Drive account once the user has inputted their information. The following 
“search_email” and “get_message_detail” functions search the users email and return the email according to the specifications. In this case, the script will return emails that: 
have an attachment, are unread, have any subject, and are newer than 1 day. 
This can be altered by changing the input in the “query_string” variable. The following steps is the utilization of the Drive API where the email message is sent to. 
Using the ID of a folder within the Google Drive the API accesses the folder location and send the attachments to the folder. Lastly, the script marks the email as “READ” so the 
program does not iterate over the same email again.
