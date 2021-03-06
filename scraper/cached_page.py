import os
import urllib
import logging

log = logging.getLogger(__name__)


class CachedPage(object):
    BASE_DIR = os.path.dirname(__file__)
    CACHE_DIR = os.path.join(BASE_DIR, "cached_pages")

    def __init__(self, cache_file_name, url):
        self.cache_path = os.path.join(CachedPage.CACHE_DIR, cache_file_name)
        self.url = url

    def __mkdir(self):
        if not os.path.isdir(CachedPage.CACHE_DIR):
            os.mkdir(CachedPage.CACHE_DIR)

    def __read_cached(self):
        cached = open(self.cache_path)
        log.debug("reading cached page %s ..." % self.cache_path)
        text = cached.read()
        cached.close()
        return text

    def __read_and_cache(self):
        page = urllib.urlopen(self.url)
        log.debug("reading URL %s ..." % self.url)
        text = page.read()
        page.close()
        self.__mkdir()
        cached = open(self.cache_path, "w")
        log.debug("writing %d characters to %s ..." % (len(text), self.cache_path))
        cached.write(text)
        cached.close()
        return text

    def read(self):
        try:
            return self.__read_cached()
        except IOError:
            return self.__read_and_cache()
