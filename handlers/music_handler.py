from .base import BaseHandler


class MusicHandler(BaseHandler):
    def handle(self, *args):
        print("MusicHandler: Handling music command")
