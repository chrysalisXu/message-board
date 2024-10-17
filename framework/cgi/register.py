"""
Register a new user
"""

# Author: XuJing shiyuchongf@126.com


from .abstract_cgi import AbstractCGI

class RegisterCGI(AbstractCGI):
    """ cgi class to handle Register
    """
    
    # constant SQL 
    _Insert_User_SQL ="""
        INSERT INTO user(
            nickname, password, email)
        VALUES(%s,%s,%s);
    """
    
    # HTML
    _Insert_Success = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>%s！3秒后回到主页面</h1>
        <script>
            setInterval(function(){window.location.href="/"},3000);
        </script>
        </html>
    """
    
    def handle(self):
        """ Insert comment
            assume contents are ISO-8859-1
        """
        # init
        result = {}
        form_data = self._decode_form()
        
        # sql
        try:
            self._get_database_entrance()
            self._database_cursor.execute(RegisterCGI._Insert_User_SQL, \
                    [form_data['user'], form_data['password'], form_data['mail']])
        except Exception as e:
            # 已被注册
            self._database.rollback()
            result['Contents'] = (RegisterCGI._Insert_Success %"该用户名或邮箱已被使用，请换一个名字").encode('utf-8')
        else:
            result['Contents'] = (RegisterCGI._Insert_Success %"注册成功").encode('utf-8')
            self._database.commit()
        self._close_database_entrance()
        
        
        return result

# which cgi class to use as entrance.
cgi = RegisterCGI