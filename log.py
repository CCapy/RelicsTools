class Log:

    def __init__(self):
        pass

    def prints(self, message, log_type=None):
        if log_type == "error":
            self.error(message)
        else:
            self.success(message)

    def error(self, message):
        print(f"\033[31m {message}\033[0m")

    def success(self, message):
        print(f"\033[32m {message}\033[0m")
