from .LHCrawler import *
from .Announcement import Announcement
from typing import List


class AnnouncementRepository:
    """
    공고를 가져오는 저장소입니다.
    """
    def __init__(self):
        self._crawler = LHCrawler()

    def get_active_announcements(self) -> List[Announcement]:
        raw_announcements = self._crawler.collect_list(
            ListParams(region_code=28, status='공고중', period=62)
        )

        return [self._to_announcement(raw) for raw in raw_announcements]

    def _to_announcement(self, raw: dict) -> Announcement:
        return Announcement(
            id=int(raw['PAN_ID']),
            name=raw['PAN_NM'],
            region=raw['CNP_CD_NM'],
            start_date=raw['PAN_DT'],
            end_date=raw['CLSG_DT'],
            status=raw['PAN_SS'],
            pdf_url=self._crawler.collect_pdf_link(
                DetailsParams(item_id=raw['PAN_ID'])
            ),
            views=int(raw['INQ_CNT'])
        )
