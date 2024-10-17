"""
    change password
"""

# Author: XuJing shiyuchongf@126.com


from .abstract_cgi import AbstractCGI

class Change_Pass_CGI(AbstractCGI):
    """ cgi class to handle Register
    """
    
    # constant SQL 
    _Select_SQL ="""
        SELECT password FROM user
        WHERE user_id=%d;
    """
    _Update_Reply_SQL ="""
        UPDATE user 
        SET password = %s
        WHERE user_id = %d;
    """
    
    
    _Result_HTML = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>%s</h1>
        <script>
            setInterval(function(){window.location.href="%s"},3000);
        </script>
        </html>
    """
    
    def handle(self):
        """ Refresh Profile
        """
        # init
        result = {}
        inquiry_result = {}
        form_data = self._decode_form()
        
        #valid
        id, nickname = self._vaild_user()
        if not nickname:
            result['Contents'] = (Change_Pass_CGI._Result_HTML %("登录失效！三秒后回到主页面","/index.html")).encode('utf-8')
            return result
        
        # sql
        own_update_sql = Change_Pass_CGI._Update_Reply_SQL.replace("%d",str(id))
        try:
            self._get_database_entrance()
            self._database_cursor.execute(Change_Pass_CGI._Select_SQL %int(id))
            inquiry_result = self._database_cursor.fetchone()
            if not inquiry_result:
                result['Contents'] = (Change_Pass_CGI._Result_HTML %("用户不存在！三秒后回到主页面","/index.html")).encode('utf-8')
                return result
            if(inquiry_result["password"]==form_data['password_old']):
                self._database_cursor.execute(own_update_sql, [form_data['password_new']])
                result['Contents'] = (Change_Pass_CGI._Result_HTML %("改密成功，请重新登录！三秒后回到主页面。","/index.html")).encode('utf-8')
                self._database.commit()
            else:
                result['Contents'] = (Change_Pass_CGI._Result_HTML %("密码错误，请重新登录！三秒后回到主页面。","/index.html")).encode('utf-8')
                return result
                
        except Exception as e:
            # debug
            print("Select Password in changing password procedure failed")
            print(e)
            # rollback
            self._database.rollback()
        finally:
            self._close_database_entrance()
        
        return result

# which cgi class to use as entrance.
cgi = Change_Pass_CGI