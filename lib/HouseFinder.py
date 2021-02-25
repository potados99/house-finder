from .AnnouncementRepository import AnnouncementRepository
from .Announcement import Announcement
from typing import List, Set, Callable
from datetime import datetime
from ast import literal_eval


class HouseFinder:
    """
    새 공고가 발견되면 지정된 일을 합니다.
    이전에 로드된 내용과 비교하기 위해 임시 저장소(파일)을 사용합니다.
    """
    def __init__(self, on_detect_new: Callable[[List[Announcement]], None]):
        self._repo = AnnouncementRepository()
        self._on_detect_new = on_detect_new

        self._previous_ids = self._restore_ids_from_file()

    def check_anything_new(self):
        print(f'{datetime.now().strftime("%Y.%m.%d %H:%M:%S")} 공고 확인!')

        all_announcements = self._repo.get_active_announcements()
        new_announcements = self._grab_new_announcements_and_remember(all_announcements)

        if new_announcements:
            print(f'새 공고 {len(new_announcements)}개 발견!')
            self._on_detect_new(new_announcements)
        else:
            print(f'새 공고 없음.')

    def _grab_new_announcements_and_remember(self, all_announcements: List[Announcement]):
        """
        self._previous_ids 와 비교하여 새 공고만을 추출하여 self._previous_ids 업데이트 후 반환합니다.

        :param all_announcements: 현재 모든 공고,
        :return: 새 공고,
        """
        # 새 공고만을 걸러냅니다.
        current_ids = set([a.id for a in all_announcements])
        new_ids = current_ids - self._previous_ids
        new_announcements = [a for a in all_announcements if a.id in new_ids]

        # 다음 실행을 위해 상태를 업데이트합니다.
        self._previous_ids = current_ids
        self._save_ids_to_file(current_ids)

        return new_announcements

    def _save_ids_to_file(self, ids: Set[int]):
        """
        파일에다가 씁니다.

        :param ids: id의 집합.
        :return:
        """
        # 파일이 없어도 일단 씁니다. 내용을 날리고 처음부터 씁니다.
        with open('.announcement_ids', 'w') as f:
            f.write(str(ids))

    def _restore_ids_from_file(self) -> Set[int]:
        """
        파일로부터 가져옵니다.
        파일이 없으면 뻗지는 않고, 빈 집합을 반환합니다.
        파일 내용이 이상해도 빈 집합을 반환합니다.

        :return: id의 집합.
        """
        try:
            # 파일 열기를 시도합니다. 없으면 FileNotFoundError를 던지며 뻗습니다.
            with open('.announcement_ids', 'r') as f:
                # 만약 내용이 불완전하거나 없으면 ValueError나 SyntaxError를 던지며 뻗습니다.
                return literal_eval(f.read())
        except (FileNotFoundError, ValueError, SyntaxError):
            # 뻗으면 비어있는 set을 기본값으로 반환합니다.
            return set()

