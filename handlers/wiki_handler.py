from .base import BaseHandler
from controllers.wiki import search_wikipedia


class WikiHandler(BaseHandler):

    def handle(self, *args):
        return search_wikipedia(args)
