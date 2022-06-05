import sys
from datetime import datetime
import os.path
import time
from abc import ABC
import tornado
from tornado.websocket import WebSocketHandler


class Pool:
    users = set()
    user_dict = dict()


class ChatHandler(WebSocketHandler, ABC):
    pools = dict()

    def message_file_path(self, user) -> str:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        return "hello.txt"
        # return './resources//history//%s//%s//%s.txt' % \
        #        (teacherName, courseName, self.pools[teacherName][courseName].user_dict[user])

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

    def on_message(self, message):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        tm = time.asctime(time.localtime(time.time()))[-13:-4]
        filepath = self.message_file_path(self)

        if message.endswith('**#*'):
            # account information ends with '**#*'
            self.pools[teacherName][courseName].user_dict[self] = message[:-4]
            # if os.path.exists(filepath):
            #     fp = open(filepath, 'a', encoding='utf-8')
            #     history = fp.read()
            #     fp.close()
            #     self.write_message(history)
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


class SignupHandler(WebSocketHandler, ABC):
    pools = dict()

    def record_file_path(self) -> str:
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        return "hello.txt"
        # return './resources//signup//%s//%s.txt' % \
        #        (teacherName, courseName)

    def open(self):
        teacherName = self.get_argument("teacherName")
        courseName = self.get_argument("courseName")
        filepath = self.record_file_path()
        with open(filepath, 'a', encoding='utf-8') as fp:
            fp.write("%s\n" % datetime.today())

        if not self.pools.get(teacherName):
            self.pools[teacherName] = dict()
        if not self.pools[teacherName].get(courseName):
            self.pools[teacherName][courseName] = Pool()
            self.pools[teacherName][courseName].users = set()
            self.pools[teacherName][courseName].user_dict = dict()
        self.pools[teacherName][courseName].users.add(self)
        self.pools[teacherName][courseName].user_dict[self] = self.get_cookie("username")

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
            time = message_arr[2]
            if header == 'confirm-signup':
                fp.write("%s 已签到 %s" % (student, time))
            elif header == 'refuse-signup':
                fp.write("%s 未签到" % student)
            else:
                pass
            fp.close()
        
    def on_close(self):
        teacherName = self.get_argument("teacherName")
        username = self.get_cookie("username")
        if teacherName == username:
            filepath = self.record_file_path()
            with open(filepath, 'a', encoding='utf-8') as fp:
                fp.write("\n");