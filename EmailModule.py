import smtplib

def SendEmail(ReceiverId,EmailSubject,EmailBody):
    FromEmail = "medicareteam24x7@gmail.com"
    FromEmailPassword = "MediCare@123"
    ServerConnection = smtplib.SMTP("smtp.gmail.com",587)
    ServerConnection.ehlo()
    ServerConnection.starttls()
    ServerConnection.ehlo()
    ServerConnection.login(FromEmail,FromEmailPassword)
    EmailMessage = 'Subject: {}\n\n{}'.format(EmailSubject,EmailBody)
    ServerConnection.sendmail(FromEmail,ReceiverId,EmailMessage)
    ServerConnection.quit()
