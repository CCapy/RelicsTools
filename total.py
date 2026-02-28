from config import Config


class Total:
    def __init__(self, config):
        self.config = config
        self.total = self.config.get_total_data()
        if not isinstance(self.total, dict):
            self.total = {}
    
    def add(self, item_id):
        key = str(item_id)
        self.total[key] = self.total.get(key, 0) + 1
    
    def get(self, item_id):
        return self.total.get(str(item_id), 0)
    
    def get_all(self):
        return self.total