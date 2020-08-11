import smtplib

def SendEmail(ReceiverId,EmailSubject,EmailBody):
    FromEmail = "medicareteam24x7@gmail.com"
    EmailPassword = "MediCare@123"
    emailServer = smtplib.SMTP("smtp.gmail.com",587)
    emailServer.ehlo()
    emailServer.starttls()
    emailServer.ehlo()
    emailServer.login(FromEmail,EmailPassword)
    EmailMessage = 'Subject: {}\n\n{}'.format(EmailSubject,EmailBody)
    emailServer.sendmail(FromEmail,ReceiverId,EmailMessage)
    emailServer.quit()
