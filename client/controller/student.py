from abc import ABC
from http.client import HTTPResponse
import tornado.web
from model import db
from controller.websocket import *


class StudentHandler(tornado.web.RequestHandler, ABC):
    current_course = dict()

    def get(self):
        username = self.get_cookie("username")
        user = db.query_data(f"""
            select username, nickname, avatar, email, school, userID
            from user
            where username = '{username}'
        """)[0]
        TCs = db.query_data(f"""
            select teacherName, courseID
            from SC
            where studentName = '{username}'
        """)
        courses = []
        current_course = None
        for TC in TCs:
            courseID = TC["courseID"]
            course = db.query_data(f"""
                select name from course
                where id = '{courseID}'
            """)[0]
            course["id"] = courseID
            course["teacherName"] = TC["teacherName"]
            res = db.query_data(f"""
                select clock, status from TC
                where teacherName = '{TC["teacherName"]}' and courseID = '{courseID}'
            """)[0]
            course["clock"], course["status"] = res["clock"], res["status"]
            if course["status"]:
                self.current_course["name"] = course["name"]
                self.current_course["teacherName"] = course["teacherName"]
                self.current_course["id"] = courseID
            courses.append(course)
        return self.render("student/user-web.html", user=user, courses=courses, current_course=self.current_course)

    def post(self):
        username = self.get_cookie("username")
        teacherName = self.current_course["teacher"]
        courseName = self.current_course["courseName"]
        if username not in ChatHandler.pools[(teacherName, courseName)].user:
            return self.redirect("/live?teacherName=%s&courseName=%s" % (teacherName, courseName))
