import json
import os
from config import Config
from log import Log
from pathlib import Path
import shutil
from pathlib import Path
from terminal import Terminal


class Save:
    def __init__(self, config, terminal: Terminal):
        self.path = "./config/save.json"
        self.config = config
        self.terminal = terminal
        self.data = self.config.get_save_data()
        self.id = None
        self.save_path = None
        self.save_path_backup = None
        self.save_bak_path = None
        self.save_bak_path_backup = None

        if not self.data:
            raise Exception("初始化Save时发生错误：无法获取配置数据")

    def save(self):
        pass

    def load(self):
        pass

    def check_id(self):
        if not self.data:
            self.reload_config()
        self.id = self.data.get("id", "")
        if self.id:
            return True
        else:
            return False

    def check_path(self):
        """检查存档文件是否存在"""
        if not self.data:
            self.reload_config()

        if not self.id:
            raise Exception("检查存档文件路径时发生错误：ID未设置")
            return False

        appdata_path = os.environ.get("APPDATA")

        prefix = Path(appdata_path) / "Nightreign"

        path = prefix / self.id / "NR0000.sl2"

        backup = prefix / "backup" / self.id / "NR0000.sl2"

        self.save_path = path
        self.save_path_backup = backup

        self.save_bak_path = path.with_suffix(path.suffix + ".bak")
        self.save_bak_path_backup = backup.with_suffix(backup.suffix + ".bak")

        result = path.is_file()
        self.terminal.logs(
            f"检查存档文件路径: {bool(result)}")
        return result

    def reload_config(self):
        self.data = self.config.get_save_data()
        if not self.data:
            raise Exception("重新加载配置数据时发生错误：无法获取配置数据")
            return False
        return True

    def backup(self):
        """备份存档文件"""
        try:
            if not self.save_path or not self.save_bak_path:
                result = self.check_path()
                if not result:
                    raise Exception("备份存档失败：存档文件不存在!")
                    return False

            result = self._copy_file(self.save_path, self.save_path_backup)
            if not result:
                raise Exception("备份存档失败：复制存档文件失败!")
                return False
            result = self._copy_file(
                self.save_bak_path, self.save_bak_path_backup)
            if not result:
                raise Exception("备份存档失败：复制备份存档文件失败!")
                return False

            return True
        except Exception as e:
            self.log.error(f"备份存档文件失败: {str(e)}")
            return False

    def load(self):
        """加载存档文件"""
        try:
            if not self.save_path_backup or not self.save_bak_path_backup:
                result = self.check_path()
                if not result:
                    raise Exception("加载存档文件失败：存档文件路径无效")
                    return False

            if self.save_path and not os.path.exists(self.save_path):
                self.save_path_backup.mkdir(parents=True, exist_ok=True)

            if self.save_bak_path and not os.path.exists(self.save_bak_path):
                self.save_bak_path_backup.mkdir(parents=True, exist_ok=True)

            shutil.copy2(self.save_path_backup, self.save_path)
            shutil.copy2(self.save_bak_path_backup, self.save_bak_path)
            return True
        except Exception as e:
            self.terminal.logs(f"加载存档文件失败: {str(e)}", log_type="error")
            return False

    def _copy_file(self, src: str, dst: str):
        try:
            if not os.path.isfile(src):
                raise Exception(f"原文件不存在: {src}")
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.terminal.logs(f"复制文件失败: {str(e)}", log_type="error")
            return False
