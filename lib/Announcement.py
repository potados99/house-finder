from dataclasses import dataclass


@dataclass
class Announcement:
    """
    공고입니다.
    """
    id: int
    name: str
    region: str
    start_date: str
    end_date: str
    status: str
    pdf_url: str
    views: int
