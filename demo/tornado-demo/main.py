#-*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler

# define a global tornado configuration
tornado.options.define('port', default=8888, type=int, help="This is the port >for application")

class WebSocketServer(WebSocketHandler):

    onlineCount = 1

    webSocketDict = dict()


# define handler type
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("./index.html")


class ProfileHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.database = database

    def get(self):
        pass

    def post(self):
        pass

class DetailHandler(tornado.web.RequestHandler):
    def get(self):
        remote_ip = self.request.remote_ip
        host = self.request.host


if __name__ == '__main__':
    # create an app object
    app = tornado.web.Application(
        [
            (r'/', IndexHandler),
            (r'/ws', WebSocketServer),
        ]
    )
    tornado.options.parse_config_file('./etc/server.conf')
    http_server = HTTPServer(app)
    http_server.bind(tornado.options.options.port)
    http_server.start(1)
    # start a web app, listen the socket
    tornado.ioloop.IOLoop.current().start()