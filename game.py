import psutil
import win32gui
import win32process
import win32con


class Game:
    def __init__(self, config, terminal):
        self.config = config
        self.terminal = terminal

    def get_game_pid(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'nightreign.exe':
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return None

    def get_hwnd_by_pid(self, pid):
        hwnd_list = []

        def callback(hwnd, extra):
            window_pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            if window_pid == extra and win32gui.IsWindowVisible(hwnd):
                hwnd_list.append(hwnd)
            return True
        win32gui.EnumWindows(callback, pid)
        return hwnd_list[0] if hwnd_list else 0
