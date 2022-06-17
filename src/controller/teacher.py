from abc import ABC
from http.client import HTTPResponse
import tornado.web
from model import db


class TeacherUserWebHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        username = self.get_cookie("username")
        user = db.query_data(f"""
            select username, nickname, avatar, email, school, userID
            from user
            where username = '{username}'
        """)[0]
        # print(bytes(user["avatar"]))
        return self.render("teacher/user-web.html", user=user)


class TeacherCourseInfoHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        teacherName = self.get_cookie("username")
        courseIDs = db.query_data(f"""
            select courseID from TC 
            where teacherName = '{teacherName}'
        """)
        courses = []
        for courseID in courseIDs:
            courseInfos = db.query_data(f"""
                select name, credit, class, count
                from course
                where id = '{courseID['courseID']}'
            """)
            courseTimes = db.query_data(f"""
                select clock from TC
                where teacherName = '{teacherName}' and courseID = '{courseID["courseID"]}'
            """)
            for courseTime in courseTimes:
                courseInfos[0]["clock"] = courseTime["clock"]
                courses.extend(courseInfos)

        return self.render("teacher/course-info.html", courses=courses)


class TeacherAboutHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        return self.render("teacher/about.html")


class TeacherAddCourseHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        return self.render("teacher/add-course.html")

    def post(self):
        post_data = self.request.body_arguments
        course = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        teacherName = self.get_cookie("username")
        start_time = course["hour1"] + ":" + course["minute1"]
        end_time = course["hour2"] + ":" + course["minute2"]
        time = course["day"] + " " + start_time + "-" + end_time
        visited = db.query_data(f"""
            select id from course
            where id = '{course["id"]}'
        """)
        # new course
        if not visited:
            db.insert_or_update_data(f"""
                insert into course(id, name, credit, class, count, ps)
                values('{course["id"]}', '{course["name"]}', {course["credit"]}, '{course["class"]}', 
                {course["count"]}, '{course["ps"]}')
            """)
        visited = db.query_data(f"""
            select * from TC
            where teacherName = '{teacherName}' and 
                  courseID = '{course["id"]}' and
                  clock = '{time}'
        """)
        if not visited:
            # update Teacher-Course
            db.insert_or_update_data(f"""
                insert into TC(teacherName, courseID, clock)
                values('{teacherName}', '{course["id"]}', '{time}')
            """)
            # update
        return self.redirect("/teacher/course-info")
