from .base import BaseHandler


class GreatHandler(BaseHandler):

    def handle(self, *args):
        print("Hello Akrom all right")
        return "Hello Akrom all right"
