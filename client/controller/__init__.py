import sys
sys.path.append("..")
from abc import ABC
import tornado.web
from model import db


class HelloHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.write("<h1>Hello, %s!</h1>" % self.get_cookie("username"))


class IndexHandler(tornado.web.RequestHandler, ABC):
    # add get()
    def get(self):
        self.render("login.html", err_msg="")


class LoginHandler(tornado.web.RequestHandler, ABC):
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


class RegisterHandler(tornado.web.RequestHandler, ABC):
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


class DrawHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        return self.render("tools/draw.html")


class LiveHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        # 通过查询字符串风格的url获取前端传递的参数
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        return self.render("live.html", teacherName=teacherName, courseName=courseName)
