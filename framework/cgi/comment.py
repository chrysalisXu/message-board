"""
This file tells how to deal with comments
"""

# Author: XuJing shiyuchongf@126.com

import time


from .abstract_cgi import AbstractCGI

class CommentCGI(AbstractCGI):
    """ cgi class to handle comment
    """
    
    # constant SQL 
    _Insert_Message_SQL ="""
        INSERT INTO message(
            from_user_id, to_message_id, content, reply_num, comment_time)
        VALUES(%d, %d, %s, 0, %s);
    """
    _Update_Reply_SQL ="""
        UPDATE message 
        SET reply_num = reply_num + 1
        WHERE message_id = %d;
    """
    
    # HTML
    _Result_HTML = """
        <!DOCTYPE HTML>
        <html>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <h1>%s！3秒后回到主页面</h1>
        <script>
            setInterval(function(){window.location.href="/index.html%s"},3000);
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
        
        target_message = int(form_data['target'])
        content = form_data['content']
        now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        
        #valid
        id, nickname = self._vaild_user()
        if not nickname:
            result['Contents'] = (CommentCGI._Result_HTML %("登录过期，评论失败","")).encode('utf-8')
            return result
        
        # sql 
        own_Insert_Message_SQL = \
                CommentCGI._Insert_Message_SQL.replace('%d',str(id),1)
        own_Insert_Message_SQL = \
                own_Insert_Message_SQL.replace('%d',str(target_message),1)
        try:
            self._get_database_entrance()
            self._database_cursor.execute(own_Insert_Message_SQL, \
                    [content, now_time])
            if target_message!=0:
                self._database_cursor.execute(CommentCGI._Update_Reply_SQL %target_message)
        except Exception as e:
            # debug
            print("comment failed")
            print(e)
            # rollback
            self._database.rollback()
        else:
            self._database.commit()
            result['Contents'] = (CommentCGI._Result_HTML %("评论成功", "?user="+nickname)).encode('utf-8')
        finally:
            self._close_database_entrance()

        return result

# which cgi class to use as entrance.
cgi = CommentCGI