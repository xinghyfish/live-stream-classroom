import tornado.web
from client.model import db

class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<h1>Hello, %s!</h1>" % self.get_cookie("username"))


class IndexHandler(tornado.web.RequestHandler):
    # add get()
    def get(self):
        self.render("index.html", err_msg="")


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        self.username = self.get_argument("account")
        self.password = self.get_argument("passwd")
        try:
            ret = db.query_data(f"""
                select * from userinfo
                where username='{self.username}' and passwd='{self.password}'
            """)
            if len(ret) == 0:
                self.render("index.html", err_msg="密码错误，请重新输入")
            else:
                self.set_cookie("username", self.username)
                self.set_cookie("passwd", self.password)
                self.redirect("/hello")
        except Exception as e:
            self.write("DB error: %s" % e)


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        post_data = self.request.body_arguments
        user = {x: post_data.get(x)[0].decode("utf-8") for x in post_data.keys()}
        print(user)
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
        else:
            res = db.query_data(f"""
                select * from userinfo
                where username = '{user["username"]}'
            """)
            if len(res):
                self.write("用户名已存在，请重新输入")
            else:
                for p in user.items():
                    self.set_cookie(p[0], p[1])

                db.insert_or_update_data(f"""
                    insert into userinfo(username, passwd, nickname, avatar, email, type, school, userID)
                    values('{user["username"]}', '{user["passwd"]}', '{user["nickname"]}', '{user["avatar"]}', '{user["email"]}', '{user["type"]}', '{user["school"]}', '{user["userID"]}')
                """)

                self.redirect('/')