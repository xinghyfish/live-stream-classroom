# -*- coding:utf-8 -*-
import os.path
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.httpserver import HTTPServer
from controller import *
from controller.websocket import *
from controller.student import *
from controller.teacher import *

# define a global tornado configuration
tornado.options.define('port', default=8000, type=int, help="This is the port >for application")

if __name__ == '__main__':
    # create an app object
    handlers = [
        (r'/', IndexHandler),
        (r'/log', LoginHandler),
        (r'/register', RegisterHandler),
        (r'/teacher/user-web', TeacherUserWebHandler),
        (r'/teacher/course-info', TeacherCourseInfoHandler),
        (r'/teacher/about', TeacherAboutHandler),
        (r'/teacher/add-course', TeacherAddCourseHandler),
        (r'/draw', DrawHandler),
        (r'/student/user-web', StudentHandler),
        (r'/student/add-course', StudentAddCourseHander),
        (r'/live', LiveHandler),
        (r'/uploadFile', UpLoadFileHandler),
        (r'/ws', WSHandler),
    ]
    template_path = os.path.join(os.path.dirname(__file__), "view")
    static_path = os.path.join(os.path.dirname(__file__), "static")

    app = tornado.web.Application(handlers=handlers, template_path=template_path, static_path=static_path, debug=True)
    tornado.options.parse_config_file("conf/server.conf")
    http_server = HTTPServer(app)
    http_server.bind(tornado.options.options.port)
    http_server.start(1)
    # start a web app, listen the socket
    tornado.ioloop.IOLoop.current().start()
