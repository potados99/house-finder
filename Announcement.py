from dataclasses import dataclass


@dataclass
class Announcement:
    id: str
    name: str
    region: str
    start_date: str
    end_date: str
    status: str
    pdf_url: str
    views: int
