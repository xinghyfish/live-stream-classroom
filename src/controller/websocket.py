import sys
import os.path
import os
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
            filepath = os.path.join(os.getcwd(), "static/resources/history/%s/%s/" % (teacherName, courseName))
            filename = self.pools[teacherName][courseName].user_dict[user] + ".txt"    
        elif type == "signup":
            filepath = os.path.join(os.getcwd(), "static/resources/signup/%s/" % (teacherName))
            filename = courseName + ".txt"
        elif type == "file":
            filepath = os.path.join(os.getcwd(), "static/resources/file/%s/%s/" % (teacherName, courseName))
            return os.listdir(filepath)
        else:
            print("Json Invalid Property <type>: expected \"message\" or \"signup\", but given \"%s\"" % type)
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
            send_message = tm + self.pools[teacherName][courseName].user_dict[self] + ': ' + jsonMessage["message"] + '\n'
            for user in self.pools[teacherName][courseName].users:
                if user != self:
                    user.write_message(jsonMessage)
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
            signuptime = jsonMessage["start_time"]
            with open(filepath, 'a', encoding='utf-8') as fp:
                if jsonMessage["status"] == 'confirm':
                    fp.write("%s 已签到 %s\n" % (student, signuptime))
                elif jsonMessage["status"] == 'refuse':
                    fp.write("%s 未签到\n" % student)
                else:
                    print("Json Invalid Property <status>: expected \"confirm\" or \"refuse\", but given \"%s\"" % jsonMessage["status"])
        elif jsonMessage["type"] == "offer-member-list":
            memberList = list(set(self.pools[teacherName][courseName].user_dict.values()))
            self.write_message(json.dumps({
                "type": "answer-member-list",
                "memberlist": memberList
            }))
        elif jsonMessage["type"] == "webrtc":
            for user in self.pools[teacherName][courseName].users:
                if user != self:
                    user.write_message(json.dumps({
                        "type": jsonMessage["type"],
                        "key": jsonMessage["key"],
                        "data": jsonMessage["data"]
                    }));
        elif jsonMessage["type"] == "offer-file-list":
            files = self.file_path(self, "file")
            self.write_message(json.dumps({
                "type": "answer-file-list",
                "filelist": files
            }))
        else:
            print("Json Invalid Property <type>: given \"%s\"" % jsonMessage["type"])
        


    def on_close(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        username = self.get_cookie("username")

        # 这里出现了一点点小问题，这行代码防止出现KeyError
        # 可能跟websocket协议挥手顺序有关，anyway，暂时就这么写着
        if self not in self.pools[teacherName][courseName].users:
            return

        action_time = time.asctime(time.localtime(time.time()))[-13:-4]
        send_message = action_time + '【' + self.pools[teacherName][courseName].user_dict[self] + '】已离开直播间'
        for user in self.pools[teacherName][courseName].users:
            filepath = self.file_path(user, "message")
            fp = open(filepath, 'a', encoding='utf-8')
            fp.write(send_message)
            fp.close()

        if teacherName == username:
            courseID = db.query_data(f"""
                select id
                from course
                where name = '{ courseName }'
            """)
            db.insert_or_update_data(f"""
                update TC
                set status = 0
                where courseID = '{ courseID[0]["id"] }' and teacherName = '{ teacherName }'
            """)
            for user in self.pools[teacherName][courseName].users:
                if user != self:
                    user.write_message(json.dumps({ "type": "close-connection" }));
        
        self.pools[teacherName][courseName].users.discard(self)
        self.pools[teacherName][courseName].user_dict.pop(self)