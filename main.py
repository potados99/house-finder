from AnnouncementRepository import AnnouncementRepository


if __name__ == '__main__':
    repo = AnnouncementRepository()

    all = repo.get_current_announcements()

    print(all)

