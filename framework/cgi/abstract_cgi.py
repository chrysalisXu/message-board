"""
This module is ABSTRACT CGI class.
Any CGI class should inherit this class.
"""

# Author: XuJing shiyuchongf@126.com


import pymysql
from urllib.parse import unquote_plus as urldecode

from ..mysql_info import database_info


class AbstractCGI:
    """ Base class for cgi classes.
        
        When url refer to a python file, server will call __init__()
        and pass request_info, which holds info in http request.
        Then handle() will be called, which should return a dict about
        response info to refresh server default response. "refresh" means 
        that only new/different elements will be refreshed. others remain
        the same.
        
        Also: useful tool function providing in this class.
        
        Methods :
        
        - __init__(request_info)
        - _get_database_entrance()
        - _close_database_entrance()
        - _xml_special_symbol_normalize(origin)
        - _decode_form()
        - _vaild_user
        - handle()
    
        Class variables:
        
        - _request_info
        - _database
        - _database_cursor
    
    """
    
    def __init__(self, request_info):
        self._request_info = request_info

    def _get_database_entrance(self):
        """ get a cursor to mysql database
            NOTICE: please call _close_database_entrance after using database.
        """
        self._database = pymysql.connect(database_info['host'], \
                database_info['user'], database_info['password'], \
                database_info['database'], \
                cursorclass = pymysql.cursors.DictCursor)
        self._database_cursor = self._database.cursor()
        return self._database_cursor 

    def _close_database_entrance(self):
        """ close database connection
        """
        self._database_cursor.close()
        self._database.close()
    
    def _xml_special_symbol_normalize(self, origin):
        """ replace special symbol of xml
        Arguments are:
        * origin: str to convert
        symbol list:
            &           &amp;        
            <           &lt;        
            >           &gt;        
            "           &quot;      
            '           &apos;
        """
        result = origin.replace("&", "&amp;")
        result = result.replace("<", "&lt;")
        result = result.replace(">", "&gt;")
        result = result.replace("\"", "&quot;")
        result = result.replace("\'", "&apos;")
        return result
    
    def _decode_form(self):
        """ decode posted form
            return urldecoded dictionary
        """
        result = {}
        for info in self._request_info['Contents'].decode('utf-8').split('&'):
            key,data = info.split('=',1)
            result[key] = urldecode(data)
        return result
    
    def _vaild_user(self):
        """ valid login
            return id, nickname if pass
            return None, None if fail
        """
        
        Valid_User_SQL ="""
            SELECT validation, nickname FROM user
            WHERE user_id = %d;
        """
        if 'Cookie' not in self._request_info:
            return None,None
        id, valid= self._request_info['Cookie'].split('=')[1].split('&')
        try:
            self._get_database_entrance()
            self._database_cursor.execute(Valid_User_SQL %int(id))
            inquiry_result = self._database_cursor.fetchone()
            if valid == str(inquiry_result['validation']):
                return id, inquiry_result['nickname']
            return None,None
        except:
            print("_vaild_user failed")
            return None,None
        finally:
            self._close_database_entrance()
    
    def handle(self):
        """ should return response_info(dict form)
        """
        return {}


# which cgi class to use
cgi = AbstractCGI