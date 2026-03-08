import json

import requests


class Total:
    def __init__(self):
        self.total = {}
    
    def add(self, item_id):
        key = str(item_id)
        self.total[key] = self.total.get(key, 0) + 1
    
    def clear(self):
        self.total = {}
    
    def get_all(self):
        return self.total
    
    def send_to_server(self):
        url = 'https://ern.capys.cn/add.php'
        if not self.total:
            print("没有统计数据需要发送")
            return
        
        # 转换为批量数据格式
        batch_data = []
        for item_id, count in self.total.items():
            batch_data.append({'i': item_id, 'c': count})
        
        try:
            response = requests.post(url, json=batch_data)
            result = response.json()
            print(result)
        except Exception as e:
            print(f"发送请求失败: {e}")
        # 发送成功后清空统计
        self.clear()