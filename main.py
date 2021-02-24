from lib.Announcement import Announcement
from lib.HouseFinder import HouseFinder
from lib.messaging import send_lms
from datetime import datetime
from typing import List
from time import sleep
from os import environ
import schedule


def on_detect(new: List[Announcement]):
    receiver = environ['SMS_RECEIVER']
    title = '병준이가 알려주는 LH임대 공고'
    body = f'새 공고 {len(new)}개 발견!\n'\
           + '\n'.join([f'\n- {a.name}(공고문: {a.pdf_url})' for a in new])

    try:
        send_lms(receiver, title, body)
        print('알림 메시지 발송 성공!')

    except Exception as e:
        print(f'알림 메시지 발송 실패: {e}')


def heartbeat():
    print(f'{datetime.now().strftime("%Y.%m.%d %H:%M:%S")} 현재 잘 작동하고 있습니다 :)')


if __name__ == '__main__':
    finder = HouseFinder(on_detect)

    # 실행 직후 상태를 출력한 다음 공고를 확인합니다.
    heartbeat()
    finder.check_anything_new()

    # 한 시간마다 상태를 출력하고
    schedule.every(1).hours.do(heartbeat)

    # 여섯 시간마다 새 공고를 확인합니다.
    schedule.every(6).hours.do(finder.check_anything_new)

    while True:
        schedule.run_pending()
        sleep(1)
