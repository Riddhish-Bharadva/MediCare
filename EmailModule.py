import smtplib
import ssl

def SendEmail(ReceiverId,EmailSubject,EmailBody):
    FromEmail = "riddhishbharadva@gmail.com"
    EmailPassword = "Rab24122011"
    emailServer = smtplib.SMTP("smtp.gmail.com",587)
    emailServer.ehlo()
    emailServer.starttls()
    emailServer.ehlo()
    emailServer.login(FromEmail,EmailPassword)
    EmailMessage = 'Subject: {}\n\n{}'.format(EmailSubject,EmailBody)
    emailServer.sendmail(FromEmail,ReceiverId,EmailMessage)
    emailServer.quit()
