from .base import BaseHandler
from controllers.youtube import search_youtube


class SearchHandler(BaseHandler):
    def handle(self, *args):
        search_youtube(*args)