#-*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.httpserver import HTTPServer

# define a global tornado configuration
tornado.options.define('port', default=8000, type=int, help="This is the port >for application")

# define handler type
class IndexHandler(tornado.web.RequestHandler):
    # add get()
    def get(self):
        self.write("好看的皮囊千篇一律，有趣的灵魂万里挑一。")

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
    app = tornado.web.Application([(r'/', IndexHandler)])
    tornado.options.parse_config_file('./etc/server.conf')
    http_server = HTTPServer(app)
    http_server.bind(tornado.options.options.port)
    http_server.start(1)
    # start a web app, listen the socket
    tornado.ioloop.IOLoop.current().start()