"""
send email to reset password
"""

# Author: XuJing shiyuchongf@126.com

import smtplib
from email.header import Header
from email.mime.text import MIMEText
import random

from ..email_info import email_info
from .abstract_cgi import AbstractCGI


class ResetPassCGI(AbstractCGI):
    """ cgi class to reset password
    """
    
    # constant SQL 
    _Select_SQL = """
        SELECT email FROM user
        WHERE nickname=%s;
    """
    _Update_SQL = """
        UPDATE user 
        SET password = %s
        WHERE nickname = %s;
    """
    
    # constant mail content
    _mail_content = """
        您好，您的账户密码已重置为%s。
    """
    
    # constant HTML content
    _Result_HTML = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>%s 3秒后回到主页面</h1>
        <script>
            setInterval(function(){window.location.href="/index.html"},3000);
        </script>
        </html>
    """
    
    
    def send_email(self, receiver, password):
        """ Send mail
        Arguments are
        * receivers:        target email address
        * password:         new password
        """
        # assemble message
        message = MIMEText(ResetPassCGI._mail_content %password, 'plain', 'utf-8') 
        message['From'] = "{}".format(email_info['sender'])
        message['To'] = receiver
        message['Subject'] = "留言板密码重置"
        # send
        smtpObj = smtplib.SMTP_SSL(email_info['mail_host'], 465)
        smtpObj.login(email_info['mail_user'], email_info['mail_pass'])
        smtpObj.sendmail(email_info['sender'], receiver, message.as_string())
    
    def handle(self):
        """ Reset Password
        """
        # init
        result = {}
        inquiry_result = {}
        form_data = self._decode_form()
        rand_pass = random.randint(100000,1000000)
        match = False
        mail_success = True
        user_find = True
        
        # sql
        try:
            self._get_database_entrance()
            self._database_cursor.execute(ResetPassCGI._Select_SQL, [form_data['user']])
            inquiry_result = self._database_cursor.fetchone()
            if inquiry_result:
                if inquiry_result['email']==form_data['mail']:
                    match = True
                    self._database_cursor.execute(ResetPassCGI._Update_SQL, \
                            [str(rand_pass), form_data['user']])
                    try:
                        self.send_email(form_data['mail'],str(rand_pass))
                    except:
                        mail_success = False
                    else:
                        self._database.commit()
            else:
                user_find = False
        except Exception as e:
            # debug
            print("Refresh Profile failed")
            print(e)
            # rollback
            self._database.rollback()
        finally:
            self._close_database_entrance()
        
        # assemble html
        if match:
            if mail_success:
                result['Contents'] = (ResetPassCGI._Result_HTML %"重置成功！请检查注册邮箱以获得新密码。").encode('utf-8')
            else:
                result['Contents'] = (ResetPassCGI._Result_HTML %"邮件发送失败！").encode('utf-8')
        else:
            if user_find:
                result['Contents'] = (ResetPassCGI._Result_HTML %"注册邮箱信息错误！").encode('utf-8')
            else:
                result['Contents'] = (ResetPassCGI._Result_HTML %"无此用户！").encode('utf-8')
        return result

# which cgi class to use as entrance.
cgi = ResetPassCGI