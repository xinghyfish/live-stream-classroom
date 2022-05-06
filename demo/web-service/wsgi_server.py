from wsgiref.simple_server import make_server
from webapp import application

server = make_server('', 8080, application)
server.serve_forever()