"""
User Log in 
"""

# Author: XuJing shiyuchongf@126.com

import random

from .abstract_cgi import AbstractCGI


class LoginCGI(AbstractCGI):
    """ cgi class to handle Register
    """
    
    # constant SQL 
    _Select_Password_SQL ="""
        SELECT password, user_id FROM user
        WHERE nickname=%s;
    """
    _Update_Valid_SQL ="""
        UPDATE user 
        SET validation = %d
        WHERE nickname = %s;
    """
    
    # HTML
    _Login_Success = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>登录成功！3秒后回到主页面</h1>
        <script>
            setInterval(function(){window.location.href="/index.html?user=%s"},3000);
        </script>
        </html>
    """
    _Login_Fail = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>登录失败！3秒后回到登录页面</h1>
        <script>
            setInterval(function(){window.location.href="/login.html"},3000);
        </script>
        </html>
    """.encode('utf-8')
    
    def handle(self):
        """ Insert comment
            assume contents are ISO-8859-1
        """
        # init
        result = {}
        inquiry_result ={}
        form_data = self._decode_form()
        rand_valid = random.randint(1,100000)
        own_Update_SQL = \
                LoginCGI._Update_Valid_SQL.replace('%d',str(rand_valid),1)
        password_correct = False
        
        # sql
        try:
            self._get_database_entrance()
            self._database_cursor.execute(LoginCGI._Select_Password_SQL, \
                    [form_data['user']])
            inquiry_result = self._database_cursor.fetchone()
            if inquiry_result:
                if form_data['password'] == inquiry_result['password']:
                    password_correct = True
                    self._database_cursor.execute(own_Update_SQL, [form_data['user']])
                    self._database.commit()
        except Exception as e:
            # debug
            print("Get Password failed")
            print(e)
            # rollback
            self._database.rollback()
        finally:
            self._close_database_entrance()
        
        
        if password_correct:
            result['Contents'] = (LoginCGI._Login_Success % form_data['user']).encode('utf-8')
            result['Set-Cookie'] = "user=%d&%d;"%(inquiry_result['user_id'], rand_valid)
        else:
            result['Contents'] = LoginCGI._Login_Fail
        return result

# which cgi class to use as entrance.
cgi = LoginCGI