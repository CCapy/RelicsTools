import json
import time
import urllib.parse
import urllib.request
from unittest import result

import pydirectinput

from config import Config
from filter import Filter, Item
from hook import Hook
from log import Log
from reader import Reader


class Fast:

    def __init__(self, config,  terminal, hook: Hook, reader: Reader):
        self.terminal = terminal
        self.config = config
        self.hook = hook
        self.entry = self.config.get_entry_data()
        self.reader = reader
        self.filter = Filter(self.config.get_filter_data())
        self.match = self.config.get_filter_data()
        self.debug = self.config.get_debug_data()
        self.times = self.debug.get("fast", 1)

    def start(self):

        start_time = time.time()
        pydirectinput.press("f")

        anhen = self.reader.get_anhen()
        wangzheng = self.reader.get_wangzheng()
        quantity = self.reader.get_quantity()
        self.reader.set_quantity(self.times)
        self.hook.filter_start = True
        self.hook.items = []
        pydirectinput.press("f")
        new_anhen = self.reader.get_anhen()
        unit = int((anhen - new_anhen)/self.times) 
        pydirectinput.press("f")
        
        match_count = 0
        self.match = self.config.get_filter_data()
        count = 0 
        last_game_item  = None
        for i in range(self.times):
            count += 1
            gameItem = self.hook.get_data()
            if gameItem == None:
                continue
            if last_game_item == gameItem:
                break
            last_game_item = gameItem
            item = Item.from_dict(gameItem)
            is_matched, score = self.filter.match(item)
            self.terminal.logs(f"第{i+1}个得分:{score}")
            if is_matched:
                match_count += 1
                pydirectinput.press("2")
                pydirectinput.press("right")
            else:
                pydirectinput.press("3")
        pydirectinput.press("f")
        self.terminal.logs(f"匹配成功数:{match_count}/{count}")
        self.terminal.logs("-"*15)
        end_time = time.time()
        cost_time = end_time - start_time
        self.terminal.logs(f"总耗时:{cost_time:.2f}秒")
        self.terminal.logs(f"每个物品耗时:{(cost_time/self.times):.2f}秒")
        # 发送到服务器
        if self.debug.get("total", False):
            self.terminal.logs("正在发送数据到服务器...")
            self.filter.total.send_to_server()
            self.terminal.logs("数据发送完成")
        else:
            self.terminal.logs("未开启统计数据发送")
        # 清空统计数据
        self.filter.total.clear()
        self.terminal.logs("原本数据:")
        self.terminal.logs(f"暗痕:{anhen}")
        self.terminal.logs(f"王证:{wangzheng}")
        self.terminal.logs(f"匹配:{match_count}/{self.times}")
        if not self.debug.get("debug", False):
            new_anhen = self.reader.get_anhen()
            new_wangzheng = self.reader.get_wangzheng()

            pay = unit * match_count
            if new_anhen != anhen:
                if pay > anhen:
                    new_anhen = 0
                else:
                    new_anhen = anhen - pay
                self.reader.set_anhen(new_anhen)
                self.terminal.logs(f"已消耗{pay}个暗痕")
            if new_wangzheng != wangzheng:
                if pay > wangzheng:
                    new_wangzheng = 0
                else:
                    new_wangzheng = wangzheng - pay
                self.terminal.logs(f"已消耗{pay}个王证")
                self.reader.set_wangzheng(new_wangzheng)
        else:
            self.reader.set_anhen(anhen)
            self.reader.set_wangzheng(wangzheng)
        self.terminal.logs("-"*15)

    def get_tag_name(self, tag_id: str | int) -> str:
        return self.entry.get(tag_id, {}).get("name", "")
