import tkinter as tk
import json
import os
import time
import keyboard
import pydirectinput
import cv2
import numpy as np
from PIL import ImageGrab
from typing import List
from lock import GameLocker
from ocr import OCREngine

class ScreenRecognizer:
    def __init__(self):
        # 初始化根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        
        self.config_file = 'config.json'
        self.current_index = 0
        self.is_running = False
        
        # 初始化OCR引擎
        try:
            self.ocr_engine = OCREngine()
        except Exception as e:
            print(f"初始化OCR引擎失败: {e}")
            self.ocr_engine = None
        
        # 初始化锁定功能
        self.locker = GameLocker(self.update_float_window)
        self.is_locked = False
        
        # 创建漂浮窗口
        self.create_float_window()
        
        # 绑定全局快捷键
        self.setup_shortcuts()
        
        # 检查并生成路径
        self.check_and_generate_path()
        
        # 设置初始状态
        self.update_float_window("就绪 - 按 Alt+1 开始识别", clear=True)
    
    def check_and_generate_path(self):
        """检查并生成路径"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查并生成路径
            if not config.get('path', ''):
                user_profile = os.environ.get('USERPROFILE', '')
                user_id = config.get('id', '')
                if user_profile and user_id:
                    path = os.path.join(user_profile, 'AppData', 'Roaming', 'Nightreign', user_id)
                    config['path'] = path
                    # 写入更新后的配置
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    self.update_float_window(f"生成路径：{path}")
                    print(f"生成路径：{path}")
        except Exception as e:
            error_msg = f"路径检查错误：{str(e)}"
            self.update_float_window(error_msg)
            print(error_msg)
    
    def create_float_window(self):
        """创建漂浮窗口"""
        # 创建顶级窗口作为漂浮窗
        self.float_window = tk.Toplevel(self.root)
        self.float_window.title("识别状态")
        
        # 设置窗口属性
        self.float_window.attributes('-topmost', True)  # 始终在最上层
        self.float_window.attributes('-alpha', 0.8)  # 半透明
        self.float_window.overrideredirect(True)  # 无标题栏
        
        # 设置位置和大小（右上角，400x600）
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - 420
        y = 20
        self.float_window.geometry(f"400x500+{x}+{y}")
        
        # 创建文本框用于显示信息，设置高度为600
        self.float_text = tk.Text(self.float_window, font=('微软雅黑', 9), bg='#333333', fg='#ffffff', wrap=tk.WORD, height=60)
        self.float_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 强制更新窗口布局
        self.float_window.update_idletasks()
    
    def update_float_window(self, message, clear=False):
        """更新漂浮窗口信息"""
        if clear:
            self.float_text.delete(1.0, tk.END)
        
        # 添加时间戳
        timestamp = time.strftime('%H:%M:%S')
        self.float_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # 自动滚动到底部
        self.float_text.see(tk.END)
        
        # 限制显示行数（保持窗口大小），增加到30行以充分利用600高度
        lines = int(self.float_text.index('end-1c').split('.')[0])
        if lines > 30:
            self.float_text.delete(1.0, 2.0)
    
    def setup_shortcuts(self):
        """设置全局快捷键"""
        def on_alt_num_1():
            """Alt+小键盘1快捷键回调函数"""
            if not self.is_running:
                self.start_recognition()
        
        def on_alt_num_0():
            """Alt+小键盘0快捷键回调函数，关闭软件"""
            # 强制设置is_running为False
            self.is_running = False
            # 先清理快捷键
            keyboard.unhook_all()
            # 然后退出程序
            import os
            import sys
            # 强制退出程序
            os._exit(0)
        
        def on_alt_q():
            """Alt+Q快捷键回调函数，终止当前任务"""
            if self.is_running:
                self.stop_current_task()
        
        def on_alt_num_2():
            """Alt+小键盘2快捷键回调函数，切换锁定状态"""
            self.toggle_lock()
        
        # 使用keyboard库绑定全局快捷键
        keyboard.add_hotkey('alt+num 1', on_alt_num_1)  # 只保留小键盘的1
        keyboard.add_hotkey('alt+num 2', on_alt_num_2)  # 只保留小键盘的2
        keyboard.add_hotkey('alt+num 0', on_alt_num_0)  # 只保留小键盘的0
        keyboard.add_hotkey('alt+q', on_alt_q)
    
    def start_recognition(self):
        """开始识别流程"""
        if self.is_running:
            return
        
        # 检查OCR引擎是否初始化成功
        if not self.ocr_engine:
            error_msg = "错误：OCR引擎初始化失败"
            self.update_float_window(error_msg)
            return
        
        self.is_running = True
        self.current_index = 0
        start_msg = "开始识别..."
        self.update_float_window(start_msg, clear=True)
        
        # 读取配置文件
        if not os.path.exists(self.config_file):
            error_msg = f"错误：{self.config_file} 文件不存在"
            self.update_float_window(error_msg)
            self.is_running = False
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'actions' not in config:
                error_msg = "错误：配置文件格式错误"
                self.update_float_window(error_msg)
                self.is_running = False
                return
            
            # 检查是否需要锁定
            if config.get('lock', False):
                self.update_float_window("配置文件中lock为true，尝试执行锁定")
                success = self.locker.start()
                if success:
                    self.is_locked = True
                    self.update_float_window("锁定成功")
                else:
                    self.update_float_window("锁定失败")
            
            tasks = config['actions']
            if not tasks:
                error_msg = "错误：任务列表为空"
                self.update_float_window(error_msg)
                self.is_running = False
                return
            
            # 获取执行次数，默认为1
            execute_times = int(config.get('times', 1))
            self.update_float_window(f"加载到 {len(tasks)} 个任务，执行 {execute_times} 次")
            print(f"加载到 {len(tasks)} 个任务，执行 {execute_times} 次")
            
            # 执行指定次数
            for i in range(execute_times):
                if not self.is_running:
                    break
                self.update_float_window(f"开始执行第 {i+1} 轮任务")
                print(f"开始执行第 {i+1} 轮任务")
                # 重置任务索引
                self.current_index = 0
                # 执行任务
                self.process_tasks(tasks, config)
                # 如果不是最后一次，等待一段时间
                if i < execute_times - 1 and self.is_running:
                    wait_time = 1.0  # 等待1秒后开始下一轮
                    self.update_float_window(f"等待 {wait_time} 秒后开始下一轮任务")
                    print(f"等待 {wait_time} 秒后开始下一轮任务")
                    time.sleep(wait_time)
            
            # 所有任务执行完成后，将is_running设置为False
            if self.is_running:
                self.is_running = False
        except Exception as e:
            error_msg = f"错误：{str(e)}"
            self.update_float_window(error_msg)
            self.is_running = False
    
    def process_tasks(self, tasks, config):
        """处理识别任务"""
        print(f"\n=== 开始处理任务列表 ===")
        print(f"总任务数：{len(tasks)}")
        
        current_task_index = -1
        
        while self.is_running and self.current_index < len(tasks):
            task = tasks[self.current_index]
            
            # 获取任务类型，默认为word
            task_type = task.get('type', 'word')
            
            # 对于不同类型的任务，检查不同的必要字段
            if task_type == 'word':
                if 'coords' not in task or 'word' not in task:
                    error_msg = f"错误：任务 {self.current_index + 1} 格式错误，缺少 coords 或 word 字段"
                    self.update_float_window(error_msg)
                    print(error_msg)
                    self.current_index += 1
                    current_task_index = -1
                    continue
                coords = task['coords']
            elif task_type == 'image':
                if 'coords' not in task:
                    error_msg = f"错误：任务 {self.current_index + 1} 格式错误，缺少 coords 字段"
                    self.update_float_window(error_msg)
                    print(error_msg)
                    self.current_index += 1
                    current_task_index = -1
                    continue
                coords = task['coords']
            # action类型的任务只需要key字段
            elif task_type == 'action':
                # 不需要coords字段
                coords = [0, 0, 0, 0]  # 占位符，避免后续代码出错
            # roll类型的任务，使用config.json中regions的坐标进行识别
            elif task_type == 'roll':
                # 不需要coords字段，使用regions.coords的坐标
                coords = config.get('regions', {}).get('coords', [0, 0, 0, 0])
            # enter类型的任务，需要coords和image字段
            elif task_type == 'enter':
                if 'coords' not in task or 'image' not in task:
                    error_msg = f"错误：任务 {self.current_index + 1} 格式错误，缺少 coords 或 image 字段"
                    self.update_float_window(error_msg)
                    print(error_msg)
                    self.current_index += 1
                    current_task_index = -1
                    continue
                coords = task['coords']
                # 处理图像路径，确保它是正确的相对路径格式
                image_path = task['image']
                # 如果路径以'/'开头，去掉它，使用相对路径
                if image_path.startswith('/'):
                    image_path = image_path[1:]
                threshold = task.get('threshold', 0.8)
            # save类型的任务，不需要特殊字段
            elif task_type == 'save':
                # 不需要coords字段
                coords = [0, 0, 0, 0]  # 占位符，避免后续代码出错
            # load类型的任务，不需要特殊字段
            elif task_type == 'load':
                # 不需要coords字段
                coords = [0, 0, 0, 0]  # 占位符，避免后续代码出错
            else:
                error_msg = f"错误：未知的任务类型 {task_type}"
                self.update_float_window(error_msg)
                print(error_msg)
                self.current_index += 1
                current_task_index = -1
                continue
            
            # 获取key字段，roll类型任务可能没有key字段
            key = task.get('key', '')
            # 获取delay值，默认为0.5秒
            delay = float(task.get('delay', 0.5))
            # 获取tips信息
            tips = task.get('tips', '')
            
            # 只在开始处理一个新任务时打印信息
            if self.current_index != current_task_index:
                task_msg = f"处理任务 {self.current_index + 1}/{len(tasks)}"
                if tips:
                    task_msg += f" - {tips}"
                self.update_float_window(task_msg)
                print(f"\n{task_msg}")
                # 任务开始前等待指定的延迟时间
                print(f"等待 {delay} 秒...")
                time.sleep(delay)
                current_task_index = self.current_index
            
            # 执行识别
            if task_type == 'word':
                word = task['word']
                # 静默执行识别，不显示详细信息
                success = self.recognize_screen_silent(coords, word)
            elif task_type == 'image':
                # 检查template字段，如果没有则使用word字段（兼容用户的错误配置）
                template = task.get('template', task.get('word', ''))
                if not template:
                    error_msg = f"错误：图片匹配任务缺少模板路径"
                    self.update_float_window(error_msg)
                    print(error_msg)
                    self.current_index += 1
                    current_task_index = -1
                    continue
                threshold = task.get('threshold', 0.8)
                # 静默执行图片匹配，不显示详细信息
                success = self.match_pattern_silent(coords, template, threshold)
            elif task_type == 'action':
                # 直接执行按键操作
                times = int(task.get('times', 1))
                # 执行按键操作
                self.execute_action(key, times)
                # 任务成功
                success = True
            elif task_type == 'roll':
                # 使用paddleocr进行识别，根据regions.name的坐标进行屏幕识别
                try:
                    # 获取times字段，默认为1
                    times = int(task.get('times', 1))
                    # 标记是否执行过success操作
                    has_success = False
                    
                    # 执行指定次数
                    for i in range(times):
                        # 获取item配置
                        item_config = config.get('item', {})
                        color_config = item_config.get('color', [])
                        size_config = item_config.get('size', [])
                        
                        # 初始化text_list
                        text_list = []
                        
                        # 检查是否需要识别名称
                        need_recognize_name = True
                        if (len(color_config) == 0 and len(size_config) == 0) or (len(color_config) == 4 and len(size_config) == 3):
                            need_recognize_name = False
                        
                        # 如果需要识别名称，先识别regions.name
                        if need_recognize_name:
                            name_coords = config.get('regions', {}).get('name', [])
                            if name_coords:
                                name_text_list = self.ocr_engine.recognize_area(name_coords)
                                if name_text_list:
                                    text_list.extend(name_text_list)
                                    name_text = name_text_list[0]
                                    self.update_float_window(f"识别名称：{name_text}")
                                    print(f"识别名称：{name_text}")
                                else:
                                    self.update_float_window("识别名称：无")
                                    print("识别名称：无")
                        
                        # 识别词条（使用regions.coords）
                        coords = config.get('regions', {}).get('coords', [])
                        if coords:
                            coords_text_list = self.ocr_engine.recognize_area(coords)
                            if coords_text_list:
                                # 如果需要识别名称，coords_text_list中的所有元素都是词条
                                # 如果不需要识别名称，coords_text_list中的第0个元素也作为词条
                                text_list.extend(coords_text_list)
                        
                        # 检查是否需要过滤
                        match_success = False
                        failure_reason = ""
                        if text_list:
                            # 执行过滤逻辑，获取匹配结果和失败原因
                            match_success, failure_reason = self.filter_recognize_result(text_list, config)
                            if match_success:
                                self.update_float_window("匹配成功")
                                print("匹配成功")
                                # 标记执行过success
                                has_success = True
                                # 执行success操作
                                success_action = task.get('success', {})
                                if success_action:
                                    self.execute_action_sequence(success_action)
                            else:
                                self.update_float_window(f"匹配失败：{failure_reason}")
                                print(f"匹配失败：{failure_reason}")
                                # 执行failure操作
                                failure_action = task.get('failure', {})
                                if failure_action:
                                    self.execute_action_sequence(failure_action)
                        
                        # 如果不是最后一次，等待一段时间
                        if i < times - 1:
                            time.sleep(0.5)
                    
                    # 根据是否执行过success更新配置
                    config['save'] = has_success
                    config['load'] = not has_success
                    # 写入更新后的配置
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    self.update_float_window(f"更新配置：save={has_success}, load={not has_success}")
                    print(f"更新配置：save={has_success}, load={not has_success}")
                    
                    # 任务成功
                    success = True
                except Exception as e:
                    error_msg = f"识别错误：{str(e)}"
                    self.update_float_window(error_msg)
                    print(error_msg)
                    success = False
            elif task_type == 'enter':
                # 循环执行图像匹配，直到成功
                success = False
                while self.is_running and not success:
                    # 静默执行图片匹配
                    success = self.match_pattern_silent(coords, image_path, threshold)
                    if not success:
                        # 图像匹配失败，模拟按下key
                        if key:
                            self.press_key_silent(key)
                        # 等待指定的时间后重试
                        wait_time = float(task.get('wait', 0.5))
                        time.sleep(wait_time)
            elif task_type == 'save':
                # 检查save是否为true
                if config.get('save', False):
                    try:
                        # 获取路径
                        path = config.get('path', '')
                        if not path:
                            self.update_float_window("错误：路径未设置")
                            print("错误：路径未设置")
                            success = False
                        else:
                            # 源文件路径
                            src_file = os.path.join(path, 'NR0000.sl2')
                            src_bak_file = os.path.join(path, 'NR0000.sl2.bak')
                            # 备份目录路径
                            backup_dir = os.path.join(os.path.dirname(path), 'backup')
                            # 目标文件路径
                            dst_file = os.path.join(backup_dir, 'NR0000.sl2')
                            dst_bak_file = os.path.join(backup_dir, 'NR0000.sl2.bak')
                            
                            # 创建备份目录
                            if not os.path.exists(backup_dir):
                                os.makedirs(backup_dir)
                                self.update_float_window(f"创建备份目录：{backup_dir}")
                                print(f"创建备份目录：{backup_dir}")
                            
                            # 备份文件
                            import shutil
                            if os.path.exists(src_file):
                                shutil.copy2(src_file, dst_file)
                                self.update_float_window(f"备份文件：{src_file} -> {dst_file}")
                                print(f"备份文件：{src_file} -> {dst_file}")
                            if os.path.exists(src_bak_file):
                                shutil.copy2(src_bak_file, dst_bak_file)
                                self.update_float_window(f"备份文件：{src_bak_file} -> {dst_bak_file}")
                                print(f"备份文件：{src_bak_file} -> {dst_bak_file}")
                            
                            # 更新配置
                            config['save'] = False
                            with open(self.config_file, 'w', encoding='utf-8') as f:
                                json.dump(config, f, indent=4, ensure_ascii=False)
                            self.update_float_window("更新配置：save=False")
                            print("更新配置：save=False")
                            
                            success = True
                    except Exception as e:
                        error_msg = f"备份错误：{str(e)}"
                        self.update_float_window(error_msg)
                        print(error_msg)
                        success = False
                else:
                    self.update_float_window("save=false，跳过备份")
                    print("save=false，跳过备份")
                    success = True
            elif task_type == 'load':
                # 检查load是否为true
                if config.get('load', False):
                    try:
                        # 获取路径
                        path = config.get('path', '')
                        if not path:
                            self.update_float_window("错误：路径未设置")
                            print("错误：路径未设置")
                            success = False
                        else:
                            # 目标文件路径
                            dst_file = os.path.join(path, 'NR0000.sl2')
                            dst_bak_file = os.path.join(path, 'NR0000.sl2.bak')
                            # 备份目录路径
                            backup_dir = os.path.join(os.path.dirname(path), 'backup')
                            # 源文件路径
                            src_file = os.path.join(backup_dir, 'NR0000.sl2')
                            src_bak_file = os.path.join(backup_dir, 'NR0000.sl2.bak')
                            
                            # 还原文件
                            import shutil
                            if os.path.exists(src_file):
                                shutil.copy2(src_file, dst_file)
                                self.update_float_window(f"还原文件：{src_file} -> {dst_file}")
                                print(f"还原文件：{src_file} -> {dst_file}")
                            if os.path.exists(src_bak_file):
                                shutil.copy2(src_bak_file, dst_bak_file)
                                self.update_float_window(f"还原文件：{src_bak_file} -> {dst_bak_file}")
                                print(f"还原文件：{src_bak_file} -> {dst_bak_file}")
                            
                            # 更新配置
                            config['load'] = False
                            with open(self.config_file, 'w', encoding='utf-8') as f:
                                json.dump(config, f, indent=4, ensure_ascii=False)
                            self.update_float_window("更新配置：load=False")
                            print("更新配置：load=False")
                            
                            success = True
                    except Exception as e:
                        error_msg = f"还原错误：{str(e)}"
                        self.update_float_window(error_msg)
                        print(error_msg)
                        success = False
                else:
                    self.update_float_window("load=false，跳过还原")
                    print("load=false，跳过还原")
                    success = True
            else:
                error_msg = f"错误：未知的任务类型 {task_type}"
                self.update_float_window(error_msg)
                print(error_msg)
                self.current_index += 1
                current_task_index = -1
                continue
            
            if success:
                # 对于action类型的任务，已经在execute_action中执行了按键操作
                # 对于enter类型的任务，已经在任务处理逻辑中处理了按键操作
                if task_type != 'action' and task_type != 'roll' and task_type != 'enter' and key:
                    # 静默执行按键（roll类型任务不需要执行按键）
                    self.press_key_silent(key)
                # 任务成功后立即执行下一个任务，不再等待
                self.current_index += 1
                current_task_index = -1
            else:
                # 识别失败，等待固定的0.5秒后重试（避免刷屏）
                time.sleep(0.5)
        
        if self.is_running:
            complete_msg = "所有任务完成"
            self.update_float_window(complete_msg)
            print("\n=== 所有任务处理完成 ===")
        # 不要在这里将self.is_running设置为False，因为可能还有下一轮任务要执行
    
    def recognize_screen(self, coords, expected_word):
        """屏幕识别"""
        try:
            # 使用OCREngine的recognize_area方法进行识别
            text_list = self.ocr_engine.recognize_area(coords)
            
            # 检查是否匹配
            if expected_word == '[number]':
                # 只要识别到数值即可
                for text in text_list:
                    if any(char.isdigit() for char in text):
                        match_msg = f"匹配成功：识别到数字 '{text}'"
                        print(match_msg)
                        self.update_float_window(match_msg)
                        return True
                return False
            else:
                # 检查是否包含关键字
                for text in text_list:
                    if expected_word in text:
                        match_msg = f"匹配成功：识别到 '{text}' 包含关键字 '{expected_word}'"
                        print(match_msg)
                        self.update_float_window(match_msg)
                        return True
                return False
        except Exception as e:
            error_msg = f"识别错误：{str(e)}"
            print(error_msg)
            self.update_float_window(error_msg)
            return False
    
    def match_pattern(self, bbox, template_path, threshold=0.8):
        """图案匹配"""
        try:
            # 修正坐标顺序
            x1, y1, x2, y2 = bbox
            x1, x2 = (x1, x2) if x1 < x2 else (x2, x1)
            y1, y2 = (y1, y2) if y1 < y2 else (y2, y1)
            bbox = (x1, y1, x2, y2)
            
            # 截取屏幕区域
            screen_crop = ImageGrab.grab(bbox)
            screen_width, screen_height = screen_crop.size
            
            if screen_width < 10 or screen_height < 10:
                print("错误：截取的屏幕区域太小")
                return False
            
            # 转换为OpenCV格式
            screen_img = cv2.cvtColor(np.array(screen_crop), cv2.COLOR_RGB2BGR)
            
            # 加载模板图像
            template = cv2.imread(template_path)
            if template is None:
                print(f"错误：无法加载模板图像 {template_path}")
                self.update_float_window(f"错误：无法加载模板图像 {template_path}")
                return False
            
            template_height, template_width = template.shape[:2]
            
            if template_width > screen_width or template_height > screen_height:
                print("错误：模板图像大于截取的屏幕区域")
                self.update_float_window("错误：模板图像大于截取的屏幕区域")
                return False
            
            # 模板匹配
            result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"匹配度：{max_val:.4f}")
            print(f"阈值：{threshold}")
            
            # 判断是否匹配成功
            if max_val >= threshold:
                print("图案匹配成功！")
                self.update_float_window(f"图案匹配成功，匹配度：{max_val:.4f} ≥ 阈值：{threshold}")
                return True
            else:
                print("图案匹配失败！")
                return False
                
        except Exception as e:
            error_msg = f"图案匹配错误：{str(e)}"
            print(error_msg)
            self.update_float_window(error_msg)
            return False
    
    def match_pattern_silent(self, bbox, template_path, threshold=0.8):
        """静默执行图案匹配"""
        try:
            # 修正坐标顺序
            x1, y1, x2, y2 = bbox
            x1, x2 = (x1, x2) if x1 < x2 else (x2, x1)
            y1, y2 = (y1, y2) if y1 < y2 else (y2, y1)
            bbox = (x1, y1, x2, y2)
            
            # 截取屏幕区域
            screen_crop = ImageGrab.grab(bbox)
            screen_width, screen_height = screen_crop.size
            
            if screen_width < 10 or screen_height < 10:
                return False
            
            # 转换为OpenCV格式
            screen_img = cv2.cvtColor(np.array(screen_crop), cv2.COLOR_RGB2BGR)
            
            # 加载模板图像
            template = cv2.imread(template_path)
            if template is None:
                return False
            
            template_height, template_width = template.shape[:2]
            
            if template_width > screen_width or template_height > screen_height:
                return False
            
            # 模板匹配
            result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 判断是否匹配成功
            return max_val >= threshold
            
        except Exception:
            return False
    
    def recognize_screen_silent(self, coords, expected_word):
        """静默执行文字识别"""
        try:
            # 使用OCREngine的recognize_area方法进行识别
            text_list = self.ocr_engine.recognize_area(coords)
            
            # 检查是否匹配
            if expected_word == '[number]':
                # 只要识别到数值即可
                for text in text_list:
                    if any(char.isdigit() for char in text):
                        return True
                return False
            else:
                # 检查是否包含关键字
                for text in text_list:
                    if expected_word in text:
                        return True
                return False
        except Exception:
            return False
    
    def press_key(self, key):
        """模拟按键"""
        try:
            # 检查是否需要停止
            if not self.is_running:
                return
            
            press_msg = f"执行按键操作：{key}"
            print(press_msg)
            self.update_float_window(press_msg)
            
            pydirectinput.keyDown(key)
            time.sleep(0.05)  # 短暂按下
            pydirectinput.keyUp(key)
            time.sleep(0.1)  # 按键后短暂延迟
        except Exception as e:
            error_msg = f"按键错误：{str(e)}"
            print(error_msg)
            self.update_float_window(error_msg)
    
    def press_key_silent(self, key):
        """静默执行按键操作"""
        try:
            # 检查是否需要停止
            if not self.is_running:
                return
            
            pydirectinput.keyDown(key)
            time.sleep(0.05)  # 短暂按下
            pydirectinput.keyUp(key)
            time.sleep(0.1)  # 按键后短暂延迟
        except Exception:
            pass
    
    def execute_action(self, key, times=1):
        """执行按键操作指定次数"""
        try:
            for i in range(times):
                # 检查是否需要停止
                if not self.is_running:
                    break
                pydirectinput.keyDown(key)
                time.sleep(0.05)  # 短暂按下
                pydirectinput.keyUp(key)
                if i < times - 1:
                    time.sleep(0.1)  # 按键间隔
        except Exception:
            pass
    
    def execute_action_sequence(self, action):
        """执行action序列，包括等待和按键操作"""
        try:
            # 检查是否需要停止
            if not self.is_running:
                return
            
            # 获取delay值，默认为0.1秒
            delay = float(action.get('delay', 0.1))
            # 等待指定时间
            time.sleep(delay)
            
            # 检查是否需要停止
            if not self.is_running:
                return
            
            # 获取key字段
            keys = action.get('key', [])
            # 确保keys是一个列表
            if not isinstance(keys, list):
                keys = [keys]
            # 获取times字段，默认为1
            times = int(action.get('times', 1))
            # 执行按键操作
            for key in keys:
                if key:
                    self.execute_action(key, times)
                    # 检查是否需要停止
                    if not self.is_running:
                        break
        except Exception as e:
            error_msg = f"执行操作失败：{str(e)}"
            self.update_float_window(error_msg)
            print(error_msg)
    
    def stop_current_task(self):
        """终止当前任务"""
        if self.is_running:
            self.is_running = False
            stop_msg = "任务已终止！"
            self.update_float_window(stop_msg)
            print(stop_msg)
            # 重置任务索引，下次按下alt+1时从头开始
            self.current_index = 0
    
    def toggle_lock(self):
        """切换锁定状态"""
        if self.is_locked:
            # 当前已锁定，需要解锁
            self.locker.stop()
            self.is_locked = False
            self.update_float_window("已解除锁定")
            # 更新config.json文件
            self.update_config_lock(False)
        else:
            # 当前未锁定，需要尝试锁定
            self.update_float_window("尝试执行锁定")
            success = self.locker.start()
            if success:
                self.is_locked = True
                self.update_float_window("锁定成功")
                # 更新config.json文件
                self.update_config_lock(True)
            else:
                self.update_float_window("锁定失败")
    
    def update_config_lock(self, lock_value):
        """更新config.json文件中的lock字段值"""
        try:
            # 读取config.json文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新lock字段
            config['lock'] = lock_value
            
            # 写回config.json文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # 打印更新信息
            lock_status = "开启" if lock_value else "关闭"
            self.update_float_window(f"已更新配置文件，锁定状态：{lock_status}")
        except Exception as e:
            error_msg = f"更新配置文件失败：{str(e)}"
            self.update_float_window(error_msg)
            print(error_msg)
    
    def filter_recognize_result(self, text_list, config):
        """过滤识别结果，根据item配置检查是否匹配"""
        # 定义映射关系
        size_map = {
            '辽阔': 'b',
            '端正': 'm',
            '细腻': 's'
        }
        
        color_map = {
            '火燃': 'r',
            '光耀': 'y',
            '水滴': 'b',
            '幽静': 'g'
        }
        
        # 从识别结果中提取size和color（使用第0个元素）
        detected_size = None
        detected_color = None
        
        if text_list:
            # 使用第0个元素判断大小和颜色
            name_text = text_list[0]
            # 检查size
            for size_key, size_value in size_map.items():
                if size_key in name_text:
                    detected_size = size_value
                    break
            
            # 检查color
            for color_key, color_value in color_map.items():
                if color_key in name_text:
                    detected_color = color_value
                    break
        
        # 获取配置的item
        item_config = config.get('item', {})
        color_config = item_config.get('color', [])
        size_config = item_config.get('size', [])
        
        # 检查颜色是否匹配
        color_match = True
        if color_config:
            color_match = detected_color in color_config
            if not color_match:
                return False, "颜色不匹配"
        
        # 检查大小是否匹配
        size_match = True
        if size_config:
            size_match = detected_size in size_config
            if not size_match:
                return False, "大小不匹配"
        
        # 颜色和大小匹配成功，继续匹配bd规则
        return self.match_bd_rules(text_list, item_config)
    
    def match_bd_rules(self, text_list, item_config):
        """匹配bd规则"""
        try:
            # 处理词条：删除空格，将"減"替换为"减"
            processed_keywords = []
            if text_list and len(text_list) > 1:
                # 从第1个元素开始处理，第0个元素用于判断大小和颜色
                for text in text_list[1:]:
                    # 确保text是字符串类型
                    if isinstance(text, str):
                        # 删除所有空格
                        text = text.replace(' ', '')
                        # 将"減"替换为"减"
                        text = text.replace('減', '减')
                        if text:
                            processed_keywords.append(text)
            
            # 打印处理后的词条
            self.update_float_window("-----------------------------------")
            print("-----------------------------------")
            for i, keyword in enumerate(processed_keywords):
                self.update_float_window(f"词条{i+1}：{keyword}")
                print(f"词条{i+1}：{keyword}")
            if not processed_keywords:
                self.update_float_window("无词条")
                print("无词条")
            self.update_float_window("-----------------------------------")
            print("-----------------------------------")
            
            # 检查blacklist
            blacklist = item_config.get('blacklist', [])
            if blacklist:
                for keyword in processed_keywords:
                    for blacklist_keyword in blacklist:
                        if blacklist_keyword in keyword:
                            return False, f"包含黑名单'{blacklist_keyword}'"
            
            # 检查bd规则
            bd_rules = item_config.get('bd', [])
            if not bd_rules:
                return True, ""
            
            # 遍历所有bd规则，只要有一个匹配成功即可
            for rule_index, rule in enumerate(bd_rules):
                # 获取当前规则的key1-key3
                key1 = rule.get('key1', [])
                key2 = rule.get('key2', [])
                key3 = rule.get('key3', [])
                
                # 检查当前规则是否匹配
                success, reason = self.match_single_bd_rule(processed_keywords, key1, key2, key3)
                if success:
                    return True, ""
            
            # 所有规则都不匹配
            return False, "词条不满足条件"
        except Exception as e:
            error_msg = f"匹配bd规则失败：{str(e)}"
            return False, error_msg
    
    def match_single_bd_rule(self, keywords, key1, key2, key3):
        """匹配单个bd规则"""
        # 复制关键字列表，用于标记已使用的词条
        available_keywords = keywords.copy()
        
        # 检查key1
        if key1:
            success, used_index = self.match_keyword_group(available_keywords, key1)
            if not success:
                return False, "key1不满足"
            # 移除已使用的词条
            if isinstance(used_index, int) and used_index >= 0:
                available_keywords.pop(used_index)
        
        # 检查key2
        if key2:
            success, used_index = self.match_keyword_group(available_keywords, key2)
            if not success:
                return False, "key2不满足"
            # 移除已使用的词条
            if isinstance(used_index, int) and used_index >= 0:
                available_keywords.pop(used_index)
        
        # 检查key3
        if key3:
            success, used_index = self.match_keyword_group(available_keywords, key3)
            if not success:
                return False, "key3不满足"
            # 移除已使用的词条
            if isinstance(used_index, int) and used_index >= 0:
                available_keywords.pop(used_index)
        
        # 所有key都满足
        return True, ""
    
    def match_keyword_group(self, keywords, keyword_group):
        """匹配关键词组，返回是否匹配成功和使用的词条索引"""
        # 确保keyword_group是一个列表
        if not isinstance(keyword_group, list):
            keyword_group = [keyword_group]
        
        # 遍历所有可用词条
        for i, keyword in enumerate(keywords):
            # 确保keyword是字符串类型
            if isinstance(keyword, str):
                # 检查当前词条是否包含任何关键词
                for group_keyword in keyword_group:
                    # 确保group_keyword是字符串类型
                    if isinstance(group_keyword, str):
                        if group_keyword in keyword:
                            return True, i
        
        # 没有匹配到
        return False, -1
    
    def recognize_region(self, coords):
        """识别一个区域，返回正面词条和负面词条"""
        try:
            # 使用OCREngine的recognize_area方法进行识别
            text_list = self.ocr_engine.recognize_area(coords)
            
            # 处理分割符「和|
            new_texts = []
            for text in text_list:
                split_text = text.replace('「', '|')
                parts = [t.strip() for t in split_text.split('|') if t.strip()]
                new_texts.extend(parts)
            text_list = new_texts
            
            # 提取正面和负面词条
            positive_keywords = []
            negative_keywords = []
            
            if text_list:
                # 第一行是正面词条
                positive_keywords.append(text_list[0])
                # 第二行及以后都是负面词条
                if len(text_list) > 1:
                    for i in range(1, len(text_list)):
                        negative_keywords.append(text_list[i])
            
            # 如果只有一行文本，尝试使用split_keywords函数分割
            if len(text_list) == 1:
                recognize_text = text_list[0]
                keywords = self.split_keywords(recognize_text)
                if len(keywords) > 1:
                    # 如果分割出了多个词条，重新分配
                    positive_keywords = [keywords[0]]
                    negative_keywords = keywords[1:]
            
            return positive_keywords, negative_keywords
        except Exception:
            return [], []
    
    def split_keywords(self, text):
        """分割词条，支持换行、「、|和空格分割"""
        # 替换分割符
        text = text.replace('「', '\n').replace('|', '\n')
        # 按换行分割
        lines = text.split('\n')
        # 过滤空行并去除首尾空格
        lines = [line.strip() for line in lines if line.strip()]
        # 合并所有行
        merged_text = ' '.join(lines)
        # 处理多个连续空格
        while '  ' in merged_text:
            merged_text = merged_text.replace('  ', ' ')
        
        # 手动分割词条，针对用户的具体案例
        keywords = []
        
        # 定义负面词条关键词
        negative_keywords = [
            '瀕死时', '连续闪避时', '闪避后的当下', '持续减少血量',
            '降低血量上限', '降低减伤率', '减少血量', '降低攻击力',
            '增加受到的伤害', '减少防御力', '降低抗性', '减少魔法值'
        ]
        
        # 检查是否包含负面词条关键词
        found_negative = False
        for negative_key in negative_keywords:
            if negative_key in merged_text:
                # 分割为正面和负面词条
                parts = merged_text.split(negative_key)
                if len(parts) >= 2:
                    positive = parts[0].strip()
                    negative = negative_key + parts[1].strip()
                    # 确保正面词条不为空
                    if positive:
                        keywords.append(positive)
                    keywords.append(negative)
                    found_negative = True
                    break
        
        # 如果没有找到负面词条关键词，使用通用分割策略
        if not found_negative:
            # 尝试按分号分割
            semicolon_pos = merged_text.find(';')
            if semicolon_pos >= 0:
                # 分号之前的内容作为正面词条
                positive = merged_text[:semicolon_pos].strip()
                keywords.append(positive)
                # 分号之后的内容作为负面词条
                negative = merged_text[semicolon_pos+1:].strip()
                if negative:
                    keywords.append(negative)
            else:
                # 尝试按逗号分割
                comma_pos = merged_text.find(',')
                if comma_pos >= 0:
                    # 第一个逗号之前的内容作为正面词条
                    positive = merged_text[:comma_pos+1].strip()
                    keywords.append(positive)
                    # 第一个逗号之后的内容作为负面词条
                    negative = merged_text[comma_pos+1:].strip()
                    if negative:
                        keywords.append(negative)
                else:
                    # 尝试按空格分割，寻找可能的负面词条
                    words = merged_text.split()
                    if len(words) > 1:
                        # 检查是否有明显的负面词汇
                        for i, word in enumerate(words):
                            if any(neg_key in word for neg_key in ['降低', '减少', '增加受到', '降低抗性']):
                                # 分割为正面和负面词条
                                positive = ' '.join(words[:i]).strip()
                                negative = ' '.join(words[i:]).strip()
                                if positive:
                                    keywords.append(positive)
                                if negative:
                                    keywords.append(negative)
                                found_negative = True
                                break
                    # 如果仍然没有找到负面词条，整个文本作为正面词条
                    if not found_negative:
                        keywords.append(merged_text)
        
        # 最多返回2个词条
        return keywords[:2]
    

    
    def match_keyword_group_with_index(self, positive_keywords, keyword_group, used_indices):
        """匹配关键词组，keyword_group内部是或关系，同时记录使用的词条索引"""
        # 确保keyword_group是一个列表
        if not isinstance(keyword_group, list):
            keyword_group = [keyword_group]
        
        # 检查是否有任何一个关键词在未使用的正面词条中
        for i, positive_keyword in enumerate(positive_keywords):
            # 跳过已经使用过的词条
            if i in used_indices:
                continue
            # 检查当前词条是否包含任何关键词
            for keyword in keyword_group:
                if keyword in positive_keyword:
                    return True, "", i
        
        # 没有匹配到，返回失败原因
        return False, "词条不满足条件", -1
    
    def run(self):
        """运行主循环"""
        try:
            self.root.mainloop()
        finally:
            # 清理快捷键
            keyboard.unhook_all()

if __name__ == "__main__":
    # 检查是否安装了 PaddleOCR 相关依赖
    try:
        import paddleocr
    except Exception:
        print("错误：未找到 PaddleOCR，请确保已安装相关依赖")
        exit(1)
    
    app = ScreenRecognizer()
    app.run()
