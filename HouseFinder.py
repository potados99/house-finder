from LHCrawler import LHCrawler


class HouseFinder:
    def __init__(self, on_detect_new):
        self._crawler = LHCrawler()
        self._on_detect_new = on_detect_new
        self._previous

    def check_anything_new(self):
        pass

    def _beautify_announcement(self, announcement: dict):
        return f''
        pass
