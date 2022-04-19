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
        self.render("../templates/index.html", )


if __name__ == '__main__':
    # create an app object
    app = tornado.web.Application([(r'/', IndexHandler)])
    tornado.options.parse_config_file('./etc/server.conf')
    http_server = HTTPServer(app)
    http_server.bind(tornado.options.options.port)
    http_server.start(1)
    # start a web app, listen the socket
    tornado.ioloop.IOLoop.current().start()