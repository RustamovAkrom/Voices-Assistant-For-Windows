from .base import BaseHandler


class WeatherHandler(BaseHandler):
    def handle(self, *args):
        print("WeatherHandler")