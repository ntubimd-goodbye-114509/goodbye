from django.core.management.base import BaseCommand
import os, time
from django.conf import settings

class Command(BaseCommand):
    help = '清除超過 3 小時未使用的裁切暫存圖片（crop 和 cropped）'

    def handle(self, *args, **kwargs):
        base_dirs = [
            os.path.join(settings.MEDIA_ROOT, 'crop'),
            os.path.join(settings.MEDIA_ROOT, 'cropped')
        ]

        # 3 小時前的 UNIX 時間戳記
        now = time.time()
        threshold = now - 3 * 60 * 60  # 秒數

        for base_dir in base_dirs:
            if not os.path.exists(base_dir):
                continue

            for user_folder in os.listdir(base_dir):
                user_path = os.path.join(base_dir, user_folder)

                if not os.path.isdir(user_path):
                    continue

                for file in os.listdir(user_path):
                    file_path = os.path.join(user_path, file)
                    try:
                        if os.path.isfile(file_path):
                            modified_time = os.path.getmtime(file_path)
                            if modified_time < threshold:
                                os.remove(file_path)
                                self.stdout.write(self.style.SUCCESS(f'已刪除：{file_path}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'刪除失敗：{file_path} — {e}'))
