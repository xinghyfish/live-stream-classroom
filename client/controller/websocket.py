import sys
import os.path
from datetime import datetime
import time
import json
from abc import ABC
sys.path.append(os.path.pardir)

from model import db
from tornado.websocket import WebSocketHandler


class Pool:
    users = set()
    user_dict = dict()


class WSHandler(WebSocketHandler, ABC):
    pools = dict()

    def file_path(self, user, type) -> str:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        if type == "message":
            filepath = os.path.join(os.getcwd(), "resources/history/%s/%s/" % (teacherName, courseName))
            filename = self.pools[teacherName][courseName].user_dict[user] + ".txt"    
        elif type == "signup":
            filepath = os.path.join(os.getcwd(), "resources/history/%s/" % (teacherName))
            filename = courseName + ".txt"
        else:
            print("Wrong command!")
            return None
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath + filename

    def open(self):
        """When connect is built, add websocket object to users set"""
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        if not self.pools.get(teacherName):
            self.pools[teacherName] = dict()
        if not self.pools[teacherName].get(courseName):
            self.pools[teacherName][courseName] = Pool()
            self.pools[teacherName][courseName].users = set()
            self.pools[teacherName][courseName].user_dict = dict()
        self.pools[teacherName][courseName].users.add(self)
        self.pools[teacherName][courseName].user_dict[self] = self.get_cookie("username")

        # 课程信息：修改课程状态
        username = self.get_cookie("username")
        if teacherName == username:
            courseID = db.query_data(f"""
                select id
                from course
                where name = '{ courseName }'
            """)
            db.insert_or_update_data(f"""
                update TC
                set status = 1
                where courseID = '{ courseID[0]["id"] }'
            """)
        
        # 签到信息：增加课程时间
        filepath = self.file_path(self, "signup")
        if username == teacherName:
            with open(filepath, 'a', encoding='utf-8') as fp:
                fp.write(str(datetime.today().date()) + '\n')
        
        # 课程人数信息：修改课程人数
        size = len(self.pools[teacherName][courseName].users)
        print(size)
        for user in self.pools[teacherName][courseName].users:
            user.write_message(json.dumps({ "type": "count-change", "count": size}))

    def on_message(self, message):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        tm = time.asctime(time.localtime(time.time()))[-13:-4]
        filepath = self.file_path(self, "message")

        jsonMessage = json.loads(message)
        if jsonMessage["type"] == "open-connection":
            # 打开连接
            self.pools[teacherName][courseName].user_dict[self] = jsonMessage["account"]
            if os.path.exists(filepath):
                fp = open(filepath, 'r', encoding='utf-8')
                history = fp.read()
                fp.close()
                self.write_message(history)
            else:
                fp = open(filepath, 'w', encoding='utf-8')
                fp.close()
            send_message = tm + '【' + self.pools[teacherName][courseName].user_dict[self] + '】已进入直播间！' + '\n'
            for user in self.pools[teacherName][courseName].users:
                filepath = self.file_path(user, "message")
                user.write_message(send_message)
                fp = open(filepath, 'a', encoding='utf-8')
                fp.write(send_message)
                fp.close()
        elif jsonMessage["type"] == "user-message":
            # 通过聊天室发送的信息
            send_message = tm + self.pools[teacherName][courseName].user_dict[self] + ': ' + message + '\n'
            for user in self.pools[teacherName][courseName].users:
                user.write_message(send_message)
                fp = open(filepath, 'a', encoding='utf-8')
                fp.write(send_message)
                fp.close()
        elif jsonMessage["type"] == "offer-signup":
            for user in self.pools[teacherName][courseName].users:
                if user != self:
                    user.write_message(json.dumps({ "type": "answer-signup"} ))
        elif jsonMessage["type"] == "answer-signup":
            filepath = self.file_path(self, "signup")
            student = jsonMessage["account"]
            signuptime = jsonMessage["start-time"]
            with open(filepath, 'a', encoding='utf-8') as fp:
                if jsonMessage["status"] == 'confirm':
                    fp.write("%s 已签到 %s\n" % (student, signuptime))
                elif jsonMessage["status"] == 'refuse':
                    fp.write("%s 未签到\n" % student)
                else:
                    print("Json Wrong command code")
        elif jsonMessage["type"] == "offer-member-list":
            memberList = list(set(self.pools[teacherName][courseName].user_dict.values()))
            self.write_message(json.dumps({
                "type": "answer-member-list",
                "memberlist": memberList
            }))
        


    def on_close(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        username = self.get_cookie("username")

        self.pools[teacherName][courseName].users.discard(self)
        filepath = self.file_path(self, "message")
        action_time = time.asctime(time.localtime(time.time()))[-13:-4]
        send_message = action_time + '【' + self.pools[teacherName][courseName].user_dict[self] + '】已离开直播间'
        fp = open(file=filepath, mode='a', encoding='utf-8')
        fp.write(send_message)
        fp.close()
        for user in self.pools[teacherName][courseName].users:
            filepath = self.file_path(user, "message")
            user.write_message(send_message)
            fp = open(filepath, 'a', encoding='utf-8')
            fp.write(send_message)
            fp.close()
        self.pools[teacherName][courseName].user_dict.pop(self)

        if teacherName == username:
            courseID = db.query_data(f"""
                select id
                from course
                where name = '{ courseName }'
            """)
            db.insert_or_update_data(f"""
                update TC
                set status = 0
                where courseID = '{ courseID[0]["id"] }'
            """)
            for user in self.pools[teacherName][courseName].users:
                self.write_message(json.dumps({ "type": "close-connection" }));
