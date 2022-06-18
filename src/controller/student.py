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
        self.current_course = dict()
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
            if course["status"] == 1:
                self.current_course["name"] = course["name"]
                self.current_course["teacherName"] = course["teacherName"]
                self.current_course["id"] = courseID
            courses.append(course)
        return self.render("student/user-web.html", user=user, courses=courses, current_course=self.current_course)

    def post(self):
        teacherName = self.current_course["teacherName"]
        courseName = self.current_course["name"]
        return self.redirect("/live?teacherName=%s&courseName=%s" % (teacherName, courseName))


class StudentAddCourseHander(tornado.web.RequestHandler):
    def post(self):
        post_data = self.request.body_arguments
        course = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        studentName = self.get_cookie("username")
        courseID = course["id"]
        teacherName = course["teacherName"]
        db.insert_or_update_data(f"""
            insert into SC(studentName, courseID, teacherName)
            values ('{studentName}', '{courseID}', '{teacherName}')
        """)
        return self.redirect("/student/user-web")
    
    def get(self):
        user = dict()
        username = self.get_cookie("username")
        user["username"] = username
        stu_courses = []
        courses = db.query_data(f"""
            select * from course
            where (
                select count(1) from SC
                where 
                    SC.studentName = '{ username }' 
                        and 
                    course.id = SC.courseID
            ) = 0
        """)
        for i in range(len(courses)):
            teacherNames = db.query_data(f"""
                select teacherName from TC
                where TC.courseID = '{courses[i]["id"]}' 
            """)
            for teacherName in teacherNames:
                courses[i]["teacherName"] = teacherName["teacherName"]
                stu_courses.append(dict(courses[i]))

        return self.render("student/add-course.html", courses=stu_courses, user=user)