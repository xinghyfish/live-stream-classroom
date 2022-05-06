from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

@gen.coroutine
def coroutine_visit():
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch("www.bing.com")
    print(response.body)


def bad_call():
    coroutine_visit()


@gen.coroutine
def outer_coroutine():
    print("start call another coroutine")
    yield coroutine_visit()
    print("end call outer_coroutine")


def func_normal():
    print("start to call a coroutine")
    IOLoop.current().run_sync(lambda: coroutine_visit())
    print("end of calling a coroutine")