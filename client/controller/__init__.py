from http.client import HTTPResponse

import tornado.web
from client.model import db

class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<h1>Hello, %s!</h1>" % self.get_cookie("username"))


class IndexHandler(tornado.web.RequestHandler):
    # add get()
    def get(self):
        self.render("login.html", err_msg="")


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument("account")
        password = self.get_argument("passwd")
        try:
            ret = db.query_data(f"""
                select * from user
                where username='{username}' and passwd='{password}'
            """)[0]
            if len(ret) == 0:
                self.render("login.html", err_msg="密码错误，请重新输入")
            else:
                self.set_cookie("username", username)
                self.set_cookie("passwd", password)
                if ret["type"] == "学生":
                    self.redirect("/student/user-web")
                else:
                    self.redirect("/teacher/user-web")
        except Exception as e:
            self.write("DB error: %s" % e)


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        post_data = self.request.body_arguments
        user = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        if user["username"] == "":
            self.write("您的用户名为空!")
        elif user["passwd"] == "":
            self.write("您的密码为空!")
        elif user["confirm-passwd"] == "":
            self.write("您没有确认密码!")
        elif user["nickname"] == "":
            self.write("您的昵称为空！")
        elif user["passwd"] != user["confirm-passwd"]:
            self.write("您两次输入的密码不一致")
        elif len(user["type"]) == 0:
            self.write("您未选择您的身份!")
        else:
            res = db.query_data(f"""
                select * from user
                where username = '{user["username"]}'
            """)
            if len(res):
                self.write("用户名已存在，请重新输入")
            else:
                for p in user.items():
                    self.set_cookie(p[0], p[1])
                avatar = self.request.files.get("avatar", None)[0]
                save_to = '../static/avatars/' + user["username"] + '.{}'.format(avatar['filename']).split('.')[1]
                with open(save_to, 'wb') as f:
                    f.write(avatar['body'])
                db.insert_or_update_data(f"""
                    insert into user(username, passwd, nickname, email, type, school, userID)
                    values('{user["username"]}', '{user["passwd"]}', '{user["nickname"]}', 
                    '{user["email"]}', '{user["type"]}', '{user["school"]}', '{user["userID"]}') 
                """)

                self.redirect('/')


class TeacherUserWebHandler(tornado.web.RequestHandler):
    def get(self):
        username = self.get_cookie("username")
        user = db.query_data(f"""
            select username, nickname, avatar, email, school, userID
            from user
            where username = '{username}'
        """)[0]
        # print(bytes(user["avatar"]))
        return self.render("teacher/user-web.html", user=user)


class AvatarHandler(tornado.web.RequestHandler):
    def get(self, username):
        avatar = db.query_data(f"""
            select avatar
            from user
            where username = '{username}'
        """)[0]["avatar"]
        img = bytes(avatar)


class TeacherCourseInfoHandler(tornado.web.RequestHandler):
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


class TeacherAboutHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("teacher/about.html")


class TeacherAddCourseHandler(tornado.web.RequestHandler):
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


class DrawHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("tools/draw.html")


class StudentHandler(tornado.web.RequestHandler):
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
                current_course["name"] = course["name"]
                current_course["teacherName"] = course["teacherName"]
                current_course["id"] = courseID
            courses.append(course)
        return self.render("student/user-web.html", user=user, courses=courses, current_course=current_course)


class LiveHandler(tornado.web.RequestHandler):
    def get(self):
        # 通过查询字符串风格的url获取前端传递的参数
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        return self.render("index.html", teacherName=teacherName, courseName=courseName)
