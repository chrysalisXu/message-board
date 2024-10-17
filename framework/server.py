"""
This module is inspired by Python socketserver module, 
with only necessary interface for my project implemented.
It is not designed to be compatible with code using socketserver.
(though they share many common ideas)
I implement it only for studying web framework.
For commercial usage, please use asyncio or socketserver instead.
"""

# Author: XuJing shiyuchongf@126.com

__version__ = "0.1"


import socket
import selectors


class Server:
    
    """ server class 
    
    Methods for the caller:
    
    - __init__(ip, port, request_handler, backlog)
    - serving_forever()
    - close_server()
    - request_finished(now_handler)
    
    Methods should not be called outside this class:
    - _server_close()
    - _handle_request()
    - _server_close()
    
    Class variables:
    - _socket
    - _handler
    - _ip
    - _selector
    - _shutdown_server_request
    - _port 
    - _handler_list
    """
    
    def __init__(self, ip_port, request_handler):
        """ initiation
        Arguments are
        * ip:               ip address
        * port:             port
        * request_handler:  RequestHandler class to handle request
        """
        
        # socket initiation
        sock = socket.socket()
        try:    
            sock.bind(ip_port)
        except Exception:
            print("socket can not bind, please check ip and port.")
            sock.close()
            raise Exception
        sock.setblocking(False)
        
        # Class variables
        self._socket = sock
        self._handler = request_handler
        self._ip = ip_port[0]
        self._port = ip_port[1]
        self._selector = selectors.DefaultSelector()
        self._shutdown_server_request = False
        self._handler_list = []

        # init handlers' database:
        self._handler.init_database()
        
    def serve_forever(self, max_wait=0.5, backlog=100):
        """ serving forever until shut down signal.
        Arguments are:
        * max_wait: when receive shutdown signal, close socket in max_wait seconds
        * backlog:  the number of unaccepted connections that the system will 
                    allow before refusing new connections.
        """
        self._socket.listen(backlog)
        self._selector.register(self._socket, selectors.EVENT_READ, self._handle_request)
        while True:
            events = self._selector.select(max_wait)
            if self._shutdown_server_request:
                self._shutdown_server_request = False
                break
            for key, mask in events:
                callback = key.data
                callback()
        
        self._server_close()
    
    def _handle_request(self):
        """ handle a single request.
        """
        request, client_address = self._socket.accept()
        request.setblocking(False)
        try:
            now_handler = self._handler(request, client_address, self)
            self._handler_list.append(now_handler)
        except Exception as e:
            print("RequestHandler failed in %s" %str(client_address))
            print(e)
            raise e
    
    def close_server(self):
        """ inform server to shutdown.
        """
        self._shutdown_server_request = True
        
    def _server_close(self):
        """ actually shutdown.
        """
        for now_handler in self._handler_list:
            now_handler.finish()
        self._handler_list = []
        self._selector.unregister(self._socket)
        self._socket.close()
        
    def request_finished(self, now_handler):
        """ Called when request finished.
            Notice: when calling, request have not been closed yet.
                    unregister will be done by handler afterwards.
        """
        self._handler_list.remove(now_handler)
    
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.close_server()
        
        
class BaseRequestHandler:

    """ Base class for request handler classes.
        
        Server will call __init__() once per request
        call read()/write() after finished socket read/wirte
        call finish when shutdown server
        no other methods of this class should be called outside
        this class.
    
        Methods :
    
        - __init__(connection, client_address, server, bufsize=2048)
        - read()
        - write()
        - finish()
        - database()
    
        Class variables:
        - _connection
        - _client_address
        - _server
        - _select_bitmask   
        - _bufsize
    """
    
    # Constants
    CONNECTION_NO = 0
    CONNECTION_R = 1
    CONNECTION_W = 2
    
    def __init__(self, connection, \
            client_address, server, bufsize=4096):
        """ initiation
        
        """
        self._connection = connection
        self._client_address = client_address
        self._server = server
        self._select_bitmask = BaseRequestHandler.CONNECTION_NO
        self._bufsize = bufsize
        print('accept connection from %s' %str(self._client_address))
    
    def read(self):
        """ recv data from socket.
            when not done receiving, return immediately.
        """
        pass
        
        
    def write(self):
        """ send response
            when not done sending, return immediately.
        """
        pass
    
    def finish(self):
        """ what to do when finish request
        """
        if self._select_bitmask != BaseRequestHandler.CONNECTION_NO:
            print ("request canceled from %s" %str(self._client_address))
            self._server._selector.unregister(self._connection)
            self._select_bitmask = BaseRequestHandler.CONNECTION_NO
        self._server.request_finished(self)
        try:
            self._connection.shutdown(socket.SHUT_RDWR)             
        except:
            print("User Connection Lost!")
        self._connection.close()
    
    @staticmethod
    def init_database():
        """ init database.
        """
        pass
        