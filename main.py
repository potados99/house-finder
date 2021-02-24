from lib.Announcement import Announcement
from lib.HouseFinder import HouseFinder
from lib.messaging import send_lms
from datetime import datetime
from typing import List
from time import sleep
from os import environ
import schedule


def on_detect(new: List[Announcement]):
    print('아싸 새 공고다!')

    receiver = environ['SMS_RECEIVER']
    title = '병준이가 알려주는 LH임대 공고'
    body = f'새 공고 {len(new)}개 발견!\n'\
           + '\n'.join([f'\n- {a.name}(공고문: {a.pdf_url})' for a in new])

    send_lms(receiver, title, body)


def heartbeat():
    print(f'{datetime.now().strftime("%Y.%m.%d %H:%M:%S")} 현재 잘 작동하고 있습니다 :)')


if __name__ == '__main__':
    finder = HouseFinder(on_detect)

    heartbeat()
    finder.check_anything_new()

    schedule.every(1).hours.do(heartbeat)
    schedule.every(6).hours.do(finder.check_anything_new)

    while True:
        schedule.run_pending()
        sleep(1)
