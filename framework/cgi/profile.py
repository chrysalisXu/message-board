"""
refresh profile html
"""

# Author: XuJing shiyuchongf@126.com


from .abstract_cgi import AbstractCGI

class ProfileCGI(AbstractCGI):
    """ cgi class to handle Register
    """
    
    # constant SQL 
    _Select_SQL ="""
        SELECT nickname, email FROM user
        WHERE user_id=%d;
    """
    
    _Result_xml = """<?xml version="1.0" encoding="UTF-8"?><CATALOG><status>%s</status>%s</CATALOG>"""
    
    
    def handle(self):
        """ Refresh Profile
        """
        # init
        result = {}
        result['Content-Type'] = 'application/xml'
        inquiry_result = {}
        
        #valid
        id, nickname = self._vaild_user()
        if not nickname:
            result['Contents'] = (ProfileCGI._Result_xml %("Valid Fail","")).encode('utf-8')
            return result
        
        # sql
        try:
            self._get_database_entrance()
            self._database_cursor.execute(ProfileCGI._Select_SQL %int(id))
            inquiry_result = self._database_cursor.fetchone()
            if not inquiry_result:
                result['Contents'] = (ProfileCGI._Result_xml %("Invalid User","")).encode('utf-8')
                return result
        except Exception as e:
            # debug
            print("Refresh Profile failed")
            print(e)
        finally:
            self._close_database_entrance()
        
        user_info = "<name>"+self._xml_special_symbol_normalize(inquiry_result["nickname"])+"</name>"
        user_info += "<email>"+self._xml_special_symbol_normalize(inquiry_result["email"])+"</email>"
        result['Contents'] = (ProfileCGI._Result_xml %("OK",user_info)).encode('utf-8')
        return result

# which cgi class to use as entrance.
cgi = ProfileCGI