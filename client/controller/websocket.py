import sys
import os.path
from datetime import datetime
import time
from abc import ABC
sys.path.append(os.path.pardir)

from model import db
from tornado.websocket import WebSocketHandler


class Pool:
    users = set()
    user_dict = dict()


class ChatHandler(WebSocketHandler, ABC):
    pools = dict()

    def message_file_path(self, user) -> str:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        filepath = os.path.join(os.getcwd(), "resources/history/%s/%s/" % (teacherName, courseName))
        filename = self.pools[teacherName][courseName].user_dict[user] + ".txt"
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
            

    def on_message(self, message):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        tm = time.asctime(time.localtime(time.time()))[-13:-4]
        filepath = self.message_file_path(self)

        if message.endswith('**#*'):
            # account information ends with '**#*'
            self.pools[teacherName][courseName].user_dict[self] = message[:-4]
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
                filepath = self.message_file_path(user)
                user.write_message(send_message)
                fp = open(filepath, 'a', encoding='utf-8')
                fp.write(send_message)
                fp.close()
        else:
            send_message = tm + self.pools[teacherName][courseName].user_dict[self] + ': ' + message + '\n'
            for user in self.pools[teacherName][courseName].users:
                user.write_message(send_message)
                fp = open(filepath, 'a', encoding='utf-8')
                fp.write(send_message)
                fp.close()

    def on_close(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        username = self.get_cookie("username")

        self.pools[teacherName][courseName].users.discard(self)
        filepath = self.message_file_path(self)
        action_time = time.asctime(time.localtime(time.time()))[-13:-4]
        send_message = action_time + '【' + self.pools[teacherName][courseName].user_dict[self] + '】已离开直播间'
        fp = open(file=filepath, mode='a', encoding='utf-8')
        fp.write(send_message)
        fp.close()
        for user in self.pools[teacherName][courseName].users:
            filepath = self.message_file_path(user)
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
                self.write_message("##*#");


class SignupHandler(WebSocketHandler, ABC):
    pools = dict()

    def record_file_path(self) -> str:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        filepath = os.path.join(os.getcwd(), "resources/signup/%s/" % teacherName)
        filename = courseName + ".txt"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath + filename

    def open(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        username = self.get_cookie("username")
        filepath = self.record_file_path()

        if not self.pools.get(teacherName):
            self.pools[teacherName] = dict()
        if not self.pools[teacherName].get(courseName):
            self.pools[teacherName][courseName] = Pool()
            self.pools[teacherName][courseName].users = set()
            self.pools[teacherName][courseName].user_dict = dict()
        self.pools[teacherName][courseName].users.add(self)
        self.pools[teacherName][courseName].user_dict[self] = self.get_cookie("username")

        if username == teacherName:
            with open(filepath, 'a', encoding='utf-8') as fp:
                fp.write(str(datetime.today().date()) + '\n')

    def on_message(self, message):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")

        message_arr = message.split(' ')
        header = message_arr[0]
        filepath = self.record_file_path()

        if header == 'start-signup':
            for user in self.pools[teacherName][courseName].users:
                if user != self:
                    user.write_message("start")
        else:
            fp = open(filepath, 'a', encoding='utf-8')
            student = message_arr[1]
            time = message_arr[6]
            if header == 'confirm-signup':
                fp.write("%s 已签到 %s\n" % (student, time))
            elif header == 'refuse-signup':
                fp.write("%s 未签到\n" % student)
            else:
                pass
            fp.close()
        
    def on_close(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")

        username = self.get_cookie("username")
        if teacherName == username:
            filepath = self.record_file_path()
            with open(filepath, 'a', encoding='utf-8') as fp:
                fp.write("\n");
        self.pools[teacherName][courseName].user_dict.pop(self)
        self.pools[teacherName][courseName].users.discard(self)


class MediaWebSocket(WebSocketHandler, ABC):
    # 存储所有的socket状态
    pools = dict()

    # 连接，需要通知客户端人数的变化
    def open(self) -> None:
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

        size = len(self.pools[teacherName][courseName].users)
        for user in self.pools[teacherName][courseName].users:
            user.write_message("count-change#$#" + str(size))
    
    def on_message(self, message):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")

        message_arr = message.split()
        if message_arr[0] == "get-member-list":
            memberList = list(set(self.pools[teacherName][courseName].user_dict.values()))
            self.write_message("member-list#$#" + str(memberList))
        else:
            pass
            

    def on_close(self) -> None:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")

        self.pools[teacherName][courseName].user_dict.pop(self)
        self.pools[teacherName][courseName].users.discard(self)
        for user in self.pools[teacherName][courseName].users:
            size = len(self.pools[teacherName][courseName].users)
            user.write_message("count-change#$#" + str(size))