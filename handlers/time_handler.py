from .base import BaseHandler
from controllers.time_service import get_time


class CurrentTimeHandler(BaseHandler):
    def handle(self, *args):
        result = get_time()
        print(result)
        return result
