import smtplib
from email.mime.text import MIMEText

from stratum import settings

import stratum.logger
log = stratum.logger.get_logger('Notify_Email')

class NOTIFY_EMAIL():

    def notify_start(self):
        if settings.NOTIFY_EMAIL_TO != '':
            self.send_email(settings.NOTIFY_EMAIL_TO,'Stratum Server Started','Stratum server has started!')
    
    def notify_found_block(self,worker_name):
        if settings.NOTIFY_EMAIL_TO != '':
            text = '%s on Stratum server found a block!' % worker_name
            self.send_email(settings.NOTIFY_EMAIL_TO,'Stratum Server Found Block',text)

    def notify_dead_coindaemon(self,worker_name):
        if settings.NOTIFY_EMAIL_TO != '':
            text = 'Coin Daemon Has Crashed Please Report' % worker_name
            self.send_email(settings.NOTIFY_EMAIL_TO,'Coin Daemon Crashed!',text)

    def send_email(self,to,subject,message):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = settings.NOTIFY_EMAIL_FROM
        msg['To'] = to
        try:
            s = smtplib.SMTP(settings.NOTIFY_EMAIL_SERVER)
            if settings.NOTIFY_EMAIL_USERNAME != '':
                if settings.NOTIFY_EMAIL_USETLS:
                    s.ehlo()
                    s.starttls()
                s.ehlo()
                s.login(settings.NOTIFY_EMAIL_USERNAME, settings.NOTIFY_EMAIL_PASSWORD)
            s.sendmail(settings.NOTIFY_EMAIL_FROM,to,msg.as_string())
            s.quit()
        except smtplib.SMTPAuthenticationError as e:
            log.error('Error sending Email: %s' % e[1])
        except Exception as e:
            log.error('Error sending Email: %s' % e[0])
