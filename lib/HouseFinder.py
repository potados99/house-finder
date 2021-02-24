from .AnnouncementRepository import AnnouncementRepository
from .Announcement import Announcement
from typing import List, Callable
from datetime import datetime


class HouseFinder:
    """
    새 공고가 발견되면 지정된 일을 합니다.
    """
    def __init__(self, on_detect_new: Callable[[List[Announcement]], None]):
        self._repo = AnnouncementRepository()
        self._on_detect_new = on_detect_new
        self._previous_ids = set()

    def check_anything_new(self):
        print(f'{datetime.now().strftime("%Y.%m.%d %H:%M:%S")} 공고 확인!')

        all_announcements = self._repo.get_active_announcements()
        all_ids = set([a.id for a in all_announcements])

        if all_ids > self._previous_ids:
            new_ids = all_ids - self._previous_ids
            new_announcements = [a for a in all_announcements if a.id in new_ids]

            print(f'새 공고 {len(new_ids)}개 발견!')

            self._on_detect_new(new_announcements)
        else:
            print(f'새 공고 없음.')

        self._previous_ids = all_ids
