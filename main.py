from framework.server import Server
from framework.httphandler import HTTPRequestHandler

#PORT
PORT = 8000

#version
__version__ = "0.1"


if __name__ == '__main__':

    Handler = HTTPRequestHandler

    with Server(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()