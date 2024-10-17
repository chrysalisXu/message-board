"""
This file rewrite http relative contents from http module.
Modified to use my own server framework(rewrite almost 
everything, though I initially only prepared to rewrite IO
part).

NOTICE: NOT COMPATIABLE WITH HTTP MODULE !!! 

For commercial usage, please use python http module instead.
"""

# Author: XuJing shiyuchongf@126.com


import selectors
import time
import copy
import importlib
import pymysql

from .server import BaseRequestHandler
from .mysql_info import database_info

__version__ = "0.1"
DEFAULT_RESPONSE = {
    'Status_code'   : '200',
    'Status'        : 'OK', 
    'Contents'      : """
        <!DOCTYPE HTML>
        <html>
        <h1>DEFAULT_RESPONSE</h1>
        </html>
    """.encode('utf-8'),
    'Content-Type'  : 'text/html'
}
DEFAULT_RESPONSE['Content-Length'] = str(len(DEFAULT_RESPONSE['Contents']))


class HTTPRequestHandler(BaseRequestHandler):
    """
    
    Methods for the caller:
    
    - __init__(connection, client_address, server, bufsize=2048)
    - read()
    - write()
    - init_database()
    
    Methods should not be called outside this class:
    
    - _process_request()
    - _start_reading()
    - _start_writing()
    - _assemble_response(response_info)
    - _get_file(path)
    - _refresh()
    - _handle_get()
    - _handle_post()
    
    Class variables:
    
    - _io_buffer
    - _request_info
    - _keep_alive
    - _select_bitmask
    
    """
    
    
    # constant
    # http head ending
    HEAD_END = b'\r\n\r\n'
    # http version 
    HTTP_VERSION = "HTTP/1.1"
    # server version
    SERVER_VERSION = 'XuJing_HTTP_SERVER'+__version__
    # keys should not be in response head
    NOT_HEAD_KEY = ['Status_code', 'Status', 'Contents']

    def __init__(self, connection, \
            client_address, server, bufsize=2048):
        """ initiation
        """
        BaseRequestHandler.__init__(self, connection, client_address, server)
        
        # new variable initiation
        self._io_buffer = b''
        self._request_info = None
        self._keep_alive = False

        # read request
        self._start_reading()
        
    def read(self):
        """ recv data from socket and parse request.
            return immediately.
            call self._process_request() when receive finished
        """
        try:
            
            raw_data = self._connection.recv(self._bufsize)
            # print(raw_data)

            # in case connection closed by client
            if not raw_data:
                print('close connection from %s' %str(self._client_address))
                self.finish()
                return
            
            # data
            if self._request_info:
                self._io_buffer += raw_data
                
            # head
            else:
                if HTTPRequestHandler.HEAD_END in raw_data:
                    divided_data = raw_data.split(HTTPRequestHandler.HEAD_END, 1)
                    self._request_info = {}
                    data = (self._io_buffer+divided_data[0]).decode('utf-8').split('\r\n')
                    first_line = data[0].split(' ')
                    self._request_info['Method'] = first_line[0]
                    if len(first_line) == 3:
                        self._request_info['URL'] = first_line[1]
                        self._request_info['Version'] = first_line[2]
                    else:
                        self._request_info['Version'] = first_line[1]
                    for line in data[1:]:
                        key_value = line.split(':')
                        if key_value[1][0] is ' ':
                            key_value[1] = key_value[1][1:]
                        self._request_info[key_value[0]] = key_value[1]
                    self._io_buffer = divided_data[1]
                else:
                    self._io_buffer += raw_data
            
            #end
            if self._request_info:
                if 'Content-Length' not in self._request_info:
                    self._request_info['Content-Length'] = 0
                if len(self._io_buffer) == int(self._request_info['Content-Length']):
                    self._request_info['Contents'] = self._io_buffer
                    self._io_buffer = b''
                    self._select_bitmask ^= BaseRequestHandler.CONNECTION_R
                    if self._select_bitmask == BaseRequestHandler.CONNECTION_NO:
                        self._server._selector.unregister(self._connection)
                    else:
                        print("reading in writing?")
                    self._process_request()
                
        # mainly for debug.
        except BlockingIOError:
            print ('weird problem that can not read from buffer')
        # in case connection closed by client   
        except ConnectionResetError:
            print('close connection from %s' %str(self._client_address))
            self.finish()
        except Exception as e:
            print(e)
        
        return
    
    def _process_request(self):
        """ handle parsed request
        """
        
        # keep_alive
        if 'Connection' in self._request_info:
            if self._request_info['Connection'] == 'keep-alive':
                self._keep_alive = True
        
        # method
        if self._request_info['Method']=="GET":
            handler = self._handle_get
        elif self._request_info['Method']=="POST":
            handler = self._handle_post
        else:
            print("method have not implemented %s." %self._request_info['Method'])
        
        self._translate_path(self._request_info['URL'])
        response_info = handler()
        
        # common response part
        response_info['Server'] = HTTPRequestHandler.SERVER_VERSION
        response_info['Date'] = \
                time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        
        self._io_buffer = self._assemble_response(response_info)
        self._start_writing()
        
    def _start_reading(self):
        """ signal to start writing
        """
        self._select_bitmask |= BaseRequestHandler.CONNECTION_R 
        self._server._selector.register(self._connection, \
                selectors.EVENT_READ, self.read)

    def _start_writing(self):
        """ signal to start writing
        """
        self._select_bitmask |= BaseRequestHandler.CONNECTION_W
        self._server._selector.register(self._connection, \
                selectors.EVENT_WRITE, self.write)
        
    def _assemble_response(self, response_info):
        """ assemble everything in a bytes object
            then return it.
        """
        
        # assemble first line
        first_line = HTTPRequestHandler.HTTP_VERSION \
                + ' ' + response_info['Status_code'] \
                + ' ' + response_info['Status']
        # assemble head
        head = ''
        for key in response_info.keys():
            if key not in HTTPRequestHandler.NOT_HEAD_KEY:
                head += '\r\n' + key + ': ' + response_info[key]
        # return
        return (first_line + head).encode('utf-8') \
                + HTTPRequestHandler.HEAD_END + response_info['Contents']
    
    def write(self):
        """ send response
            response should be stored in _io_buffer before calling
        """
        try:
            sent_data = self._connection.send(self._io_buffer)
            self._io_buffer = self._io_buffer[sent_data:]
        except:
            print("response failed in %s" %str(self._client_address))
            self.finish()
            return
        
        if len(self._io_buffer)==0:
            self._select_bitmask ^= BaseRequestHandler.CONNECTION_W
            if self._select_bitmask == BaseRequestHandler.CONNECTION_NO:
                self._server._selector.unregister(self._connection)
            else:
                print("writing in reading?")
            # alive or close
            if self._keep_alive:
                self._refresh()
                self._start_reading()
            else:
                self.finish()
    
    def _get_file(self, path):
        """ load file content and return
        """
        with open(path, 'rb') as f:
            return f.read()
    
    def _refresh(self):
        """ in keep-alive mode, clean all data in last request
        """
        self._io_buffer = b''
        self._request_info = None
        self._keep_alive = False
        
    def _translate_path(self, path):
        """ Translate url to path
        """
        if '#' in path:
            path,self._request_info['URL_location'] = path.split('#',1)
        if '?' in path:
            path,after = path.split('?',1)
            self._request_info['URL_elements'] = after.split('&')
        
        if path == '/':
            path += 'index.html'
        # resource type
        if path.split('.',1)[1] == 'html':
            path = 'static'+path
        elif path.split('.',1)[1] == 'py':
            path = 'framework/cgi'+path
            path = path.split('.',1)[0]
            path = path.replace('/','.')
        else:
            # for future extension
            path = 'static'+path
        self._request_info['URL_path'] = path
        return path
    
    def _handle_get(self):
        """ Handle GET request
            assume GET will only require static HTML
        """
        response_info = DEFAULT_RESPONSE
        try:
            response_info['Contents'] = \
                    self._get_file(self._request_info['URL_path'])
            response_info['Content-Length'] = \
                    str(len(response_info['Contents']))
        except:
            response_info['Status_code'] = '404'
            response_info['Status'] = 'Not Found'
            print("not found %s" %self._request_info['URL_path'])
            
        return response_info
    
    def _handle_post(self):
        """ Handle POST request
            assume POST url will always be .py
        """
        response_info = copy.deepcopy(DEFAULT_RESPONSE)
        try:
            mod = importlib.import_module(self._request_info['URL_path'])
            handler = mod.cgi(self._request_info)
            try:
                fresh = handler.handle()
                for key in fresh.keys():
                    response_info[key] = fresh[key]
                response_info['Content-Length'] = str(len(response_info['Contents']))
            except Exception as e:
                response_info['Status_code'] = '500'
                response_info['Status'] = "Internal Server Error"
                print("handle request failed. Request detail:")
                print(e)
                print(self._request_info)
        except:
            response_info['Status_code'] = '404'
            response_info['Status'] = 'Not Found'
            print("not found %s" %self._request_info['url_path'])
            return response_info
        
        return response_info

    @staticmethod
    def init_database():
        """ init database.
        """ 
        db = pymysql.connect(database_info['host'], \
                database_info['user'],database_info['password'],database_info['database'])
        cursor = db.cursor()
        try:
            create_user_sql = \
                """ CREATE TABLE IF NOT EXISTS `user`(
                        `user_id` INT UNSIGNED AUTO_INCREMENT,
                        `nickname` VARCHAR(30) UNIQUE KEY NOT NULL,
                        `password` VARCHAR(30) NOT NULL,
                        `email` VARCHAR(80) UNIQUE KEY NOT NULL,
                        `validation` INT,
                        PRIMARY KEY ( `user_id` )
                    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
                """
            create_message_sql = \
                """ CREATE TABLE IF NOT EXISTS `message`(
                        `message_id` INT UNSIGNED AUTO_INCREMENT,
                        `from_user_id` INT UNSIGNED NOT NULL,
                        `to_message_id` INT UNSIGNED NOT NULL,
                        `reply_num` INT NOT NULL,
                        `content` TEXT NOT NULL,
                        `comment_time` DATETIME NOT NULL,
                        PRIMARY KEY ( `message_id` )
                    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
                """
            insert_admin_sql = \
                """ INSERT INTO user
                    (nickname,password,email)
                    SELECT '管理员','1919810','shiyuchongf@126.com'
                    FROM dual
                    WHERE NOT EXISTS (SELECT * FROM user 
                    WHERE user.nickname='管理员');
                """
            cursor.execute(create_user_sql)
            cursor.execute(create_message_sql)
            cursor.execute(insert_admin_sql)
            db.commit()
        except:
            db.rollback()
            print('server database initiation failed')
        cursor.close()
        db.close()