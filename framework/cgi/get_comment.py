"""
This file tells how to deal with comments
"""

# Author: XuJing shiyuchongf@126.com

import time

from .abstract_cgi import AbstractCGI

class GetCommentCGI(AbstractCGI):
    """ cgi class to get comment
    """
    
    _Get_Message_SQL ="""
        SELECT 
        user.nickname, message.content, message.comment_time,
        message.message_id, message.reply_num
        FROM 
        user, message
        WHERE 
        message.to_message_id = %d
        AND user.user_id = message.from_user_id
        ORDER BY message.comment_time DESC
        LIMIT %d,10;
    """
    
    def handle(self):
        """ Get comment
        """
        # init
        result = {}
        inquiry_result = []
        
        # decode request
        target,num = self._request_info['Contents'].decode('utf-8').split('.',1)
        target = int(target)
        num = int(num)
        
        # sql 
        try:
            self._get_database_entrance()
            self._database_cursor.execute(GetCommentCGI._Get_Message_SQL %(target,num-10))
            inquiry_result = self._database_cursor.fetchmany(10)
            self._close_database_entrance()
        except Exception as e:
            print("Comment inquiry failed.")
            print(e)
        
        # assemble xml
        xml_result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><CATALOG>"
        if isinstance(inquiry_result,dict):
            inquiry_result = [inquiry_result]
        for item in inquiry_result:
            xml_result += "<message>"
            for key in item.keys():
                real_key = str(key)
                xmlize_data = self._xml_special_symbol_normalize(str(item[key]))
                xml_result += "<%s>%s</%s>" % \
                        (real_key, xmlize_data, real_key)
            xml_result += "</message>"
        xml_result += "</CATALOG>"
        
        # result assignment
        result['Content-Type'] = 'application/xml'
        result['Contents'] = xml_result.encode('utf-8')
        return result

# which cgi class to use as entrance.
cgi = GetCommentCGI