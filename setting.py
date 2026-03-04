import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


class ConfigManager:
    def __init__(self):
        self.config_path = Path("config/config.json")
        self.config = self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取配置文件失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        return {
            "filter_options": {
                "3 必选": 30,
                "2 必选 | 1 可选": 21,
                "2 必选": 20,
                "1 必选 | 2 可选": 12,
                "1 必选 | 1 可选": 11,
                "1 必选": 10,
                "3 可选": 3,
                "2 可选": 2,
                "1 可选": 1,
                "无": 0
            },
            "default_build": {
                "name": "新构筑",
                "must": [],
                "extra": [],
                "ban": [],
                "score": 0
            },
            "window": {
                "title": "编辑构筑",
                "width": 900,
                "height": 700
            },
            "file_paths": {
                "filters": "config/filters.json",
                "entries": "asset/entry.json",
                "blacklist": "asset/blacklist.json",
                "icon": "asset/setting.png"
            }
        }
    
    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# 全局配置管理器
config_manager = ConfigManager()


class BuildSelector:
    def __init__(self, parent, main_app, current_index, filter_options, on_build_selected):
        self.parent = parent
        self.main_app = main_app
        self.current_index = current_index
        self.filter_options = filter_options
        self.on_build_selected = on_build_selected
        
        self.frame = ttk.Frame(parent, padding="5")
        self.frame.pack(fill=tk.X)
        
        ttk.Label(self.frame, text="选择构筑:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        
        self.build_options = []
        self.build_var = tk.StringVar()
        
        # 增加宽度以更好地利用空间
        self.build_combobox = ttk.Combobox(self.frame, textvariable=self.build_var, width=60, state="readonly")
        self.build_combobox.pack(side=tk.LEFT, expand=True, anchor=tk.W)
        self.build_combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)
        
        ttk.Button(self.frame, text="复制", command=self.copy_build, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.frame, text="添加", command=self.add_build, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.frame, text="删除", command=self.delete_build, width=5).pack(side=tk.LEFT, padx=2)
        
        self.update_build_options()
    
    def update_build_options(self):
        self.build_options = []
        for i, build in enumerate(self.main_app.filters):
            name = build.get("name", "")
            must_len = len(build.get("must", []))
            extra_len = len(build.get("extra", []))
            ban_len = len(build.get("ban", []))
            score = build.get("score", 0)
            
            filter_text = self.get_filter_text(score)
            option_text = f"{name}|{must_len}必选|{extra_len}可选|{ban_len}黑名单|满足{filter_text}"
            self.build_options.append((option_text, i))
        
        self.build_combobox['values'] = [option[0] for option in self.build_options]
        
        current_option = None
        for option_text, i in self.build_options:
            if i == self.current_index:
                current_option = option_text
                break
        if current_option:
            self.build_var.set(current_option)
    
    def get_filter_text(self, score):
        for option, score_value in self.filter_options.items():
            if score_value == score:
                return option
        return "无"
    
    def on_combobox_selected(self, event):
        selected_option = self.build_var.get()
        for option_text, i in self.build_options:
            if option_text == selected_option:
                self.on_build_selected(i)
                break
    
    def copy_build(self):
        # 检查当前索引是否有效
        if not self.main_app.filters or self.current_index >= len(self.main_app.filters):
            messagebox.showerror("错误", "没有可复制的构筑")
            return None
        
        current_build = self.main_app.filters[self.current_index]
        copied_build = current_build.copy()
        original_name = copied_build.get("name", "新构筑")
        copied_build["name"] = f"{original_name} 副本"
        
        self.main_app.filters.append(copied_build)
        self.main_app.save_filters()
        
        # 更新选择框选项
        self.update_build_options()
        # 设置焦点到新复制的构筑
        new_index = len(self.main_app.filters) - 1
        self.current_index = new_index
        # 更新选择框显示
        if self.build_options:
            self.build_var.set(self.build_options[-1][0])
        # 通知 EditFilterWindow 切换构筑
        self.on_build_selected(new_index)
        return new_index
    
    def add_build(self):
        new_build = config_manager.get("default_build").copy()
        self.main_app.filters.append(new_build)
        self.main_app.save_filters()
        
        # 更新选择框选项
        self.update_build_options()
        # 设置焦点到新创建的构筑
        new_index = len(self.main_app.filters) - 1
        self.current_index = new_index
        # 更新选择框显示
        if self.build_options:
            self.build_var.set(self.build_options[-1][0])
        # 通知 EditFilterWindow 切换构筑
        self.on_build_selected(new_index)
        return new_index
    
    def delete_build(self):
        # 检查当前索引是否有效
        if not self.main_app.filters or self.current_index >= len(self.main_app.filters):
            messagebox.showerror("错误", "没有可删除的构筑")
            return None
        
        # 弹出确认对话框
        result = messagebox.askyesno("删除构筑", "确定要删除当前构筑吗？")
        if not result:
            return None
        
        if len(self.main_app.filters) == 1:
            current_build = self.main_app.filters[0]
            is_empty = len(current_build.get("must", [])) == 0 and len(current_build.get("extra", [])) == 0 and len(current_build.get("ban", [])) == 0
            
            if is_empty:
                messagebox.showinfo("提示", "至少需要保留一个构筑")
                return None
            else:
                # 删除当前构筑并创建一个空的构筑
                self.main_app.filters.pop(self.current_index)
                empty_build = config_manager.get("default_build").copy()
                self.main_app.filters.append(empty_build)
                self.main_app.save_filters()
                
                # 更新选择框选项并设置聚焦到新创建的空构筑
                self.current_index = 0
                self.update_build_options()
                # 通知 EditFilterWindow 切换构筑
                self.on_build_selected(0)
                return 0
        else:
            # 删除当前构筑
            self.main_app.filters.pop(self.current_index)
            self.main_app.save_filters()
            
            # 更新选择框选项并设置聚焦到第一个构筑
            self.current_index = 0
            self.update_build_options()
            # 通知 EditFilterWindow 切换构筑
            self.on_build_selected(0)
            return 0


class EntryPool:
    def __init__(self, parent, entries, blacklist, filter_data, type_var, search_var, on_double_click):
        self.parent = parent
        self.entries = entries
        self.blacklist = blacklist
        self.filter_data = filter_data
        self.type_var = type_var
        self.search_var = search_var
        self.on_double_click = on_double_click
        
        self.frame = ttk.LabelFrame(parent, text="词条池子", padding="5")
        self.frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(self.frame, columns=("id", "name", "superposability"), show="headings")
        self.tree.heading("id", text="ID", anchor=tk.CENTER)
        self.tree.heading("name", text="词条名", anchor=tk.CENTER)
        self.tree.heading("superposability", text="叠加", anchor=tk.CENTER)
        
        # 增加列宽以更好地利用空间
        self.tree.column("id", width=70, anchor=tk.CENTER)
        self.tree.column("name", width=400)
        self.tree.column("superposability", width=100, anchor=tk.CENTER)
        
        self.tree.bind("<Double-1>", self.on_double_click)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def update(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        current_type = self.type_var.get()
        search_keyword = self.search_var.get().lower()
        
        if current_type == "ban":
            for entry_id, entry_data in self.blacklist.items():
                if entry_id not in self.filter_data.get(current_type, []):
                    if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                        self.tree.insert("", tk.END, iid=entry_id, values=(
                            entry_id, 
                            entry_data.get("name", ""), 
                            entry_data.get("superposability", "")
                        ))
        else:
            for entry_id, entry_data in self.entries.items():
                if current_type == "must":
                    if entry_id not in self.filter_data.get("must", []) and entry_id not in self.filter_data.get("extra", []):
                        if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                            self.tree.insert("", tk.END, iid=entry_id, values=(
                                entry_id, 
                                entry_data.get("name", ""), 
                                entry_data.get("superposability", "")
                            ))
                elif current_type == "extra":
                    if entry_id not in self.filter_data.get("must", []) and entry_id not in self.filter_data.get("extra", []):
                        if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                            self.tree.insert("", tk.END, iid=entry_id, values=(
                                entry_id, 
                                entry_data.get("name", ""), 
                                entry_data.get("superposability", "")
                            ))
    
    def get_selection(self):
        return self.tree.selection()
    
    def get_children(self):
        return self.tree.get_children()
    
    def selection_set(self, item):
        self.tree.selection_set(item)
    
    def focus(self, item):
        self.tree.focus(item)


class BuildPool:
    def __init__(self, parent, entries, blacklist, filter_data, type_var, search_var, on_double_click):
        self.parent = parent
        self.entries = entries
        self.blacklist = blacklist
        self.filter_data = filter_data
        self.type_var = type_var
        self.search_var = search_var
        self.on_double_click = on_double_click
        
        self.frame = ttk.LabelFrame(parent, text="构筑池子", padding="5")
        self.frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(self.frame, columns=("id", "name", "superposability"), show="headings")
        self.tree.heading("id", text="ID", anchor=tk.CENTER)
        self.tree.heading("name", text="词条名", anchor=tk.CENTER)
        self.tree.heading("superposability", text="叠加", anchor=tk.CENTER)
        
        # 增加列宽以更好地利用空间
        self.tree.column("id", width=70, anchor=tk.CENTER)
        self.tree.column("name", width=400)
        self.tree.column("superposability", width=100, anchor=tk.CENTER)
        
        self.tree.bind("<Double-1>", self.on_double_click)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def update(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        current_type = self.type_var.get()
        search_keyword = self.search_var.get().lower()
        
        current_pool = self.filter_data.get(current_type, [])
        for entry_id in current_pool:
            if current_type == "ban":
                entry_data = self.blacklist.get(entry_id, {})
            else:
                entry_data = self.entries.get(entry_id, {})
            
            if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                self.tree.insert("", tk.END, iid=entry_id, values=(
                    entry_id, 
                    entry_data.get("name", ""), 
                    entry_data.get("superposability", "")
                ))
    
    def get_selection(self):
        return self.tree.selection()
    
    def get_children(self):
        return self.tree.get_children()
    
    def selection_set(self, item):
        self.tree.selection_set(item)
    
    def focus(self, item):
        self.tree.focus(item)


class DetailView:
    def __init__(self, parent, entries, blacklist, type_var):
        self.parent = parent
        self.entries = entries
        self.blacklist = blacklist
        self.type_var = type_var
        
        self.frame = ttk.LabelFrame(parent, text="详情", padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.text = tk.Text(self.frame, wrap=tk.WORD, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)
    
    def update(self, entry_id):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        
        if entry_id:
            current_type = self.type_var.get()
            if current_type == "ban":
                entry_data = self.blacklist.get(entry_id, {})
            else:
                entry_data = self.entries.get(entry_id, {})
            
            detail_text = f"ID: {entry_id}\n"
            detail_text += f"词条名: {entry_data.get('name', '')}\n"
            detail_text += f"分类: {entry_data.get('type', '')}\n"
            detail_text += f"介绍: {entry_data.get('explanation', '')}\n"
            detail_text += f"备注: {entry_data.get('note', '')}\n"
            detail_text += f"叠加: {entry_data.get('superposability', '')}\n"
            
            self.text.insert(tk.END, detail_text)
        
        self.text.config(state=tk.DISABLED)


class MainApp:
    def __init__(self, root):
        self.root = root
        
        # 检查所需文件是否存在
        if not self.check_required_files():
            # 如果文件检查失败，退出程序
            root.destroy()
            return
        
        # 读取filters.json文件
        self.filters_path = Path(config_manager.get("file_paths.filters"))
        self.filters = self.load_filters()
        
        # 如果没有构筑，创建一个默认构筑
        if not self.filters:
            self.filters.append(config_manager.get("default_build"))
            self.save_filters()
        
        # 直接在主窗口中创建编辑界面
        self.edit_window = EditFilterWindow(root, self.filters[0], 0, self)
    
    def check_required_files(self):
        # 检查必要的目录和文件
        required_paths = [
            Path("config"),
            Path("asset"),
            Path(config_manager.get("file_paths.entries")),
            Path(config_manager.get("file_paths.blacklist")),
            Path(config_manager.get("file_paths.icon"))
        ]
        
        missing_files = []
        
        for path in required_paths:
            if not path.exists():
                missing_files.append(str(path))
        
        if missing_files:
            error_message = "缺少以下必要文件或目录：\n" + "\n".join(missing_files)
            messagebox.showerror("错误", error_message)
            return False
        
        return True
    
    def load_filters(self):
        try:
            with open(self.filters_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")
            return []
    
    def save_filters(self):
        try:
            # 确保目录存在
            self.filters_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filters_path, "w", encoding="utf-8") as f:
                json.dump(self.filters, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")

class EditFilterWindow:
    def __init__(self, parent, filter_data, index, main_app):
        self.parent = parent
        self.filter_data = filter_data.copy()
        self.original_data = filter_data.copy()
        self.index = index
        self.main_app = main_app
        
        # 加载配置
        self.window_title = config_manager.get("window.title")
        self.window_width = config_manager.get("window.width")
        self.window_height = config_manager.get("window.height")
        self.icon_path = config_manager.get("file_paths.icon")
        self.filter_options = config_manager.get("filter_options")
        self.entries_path = config_manager.get("file_paths.entries")
        self.blacklist_path = config_manager.get("file_paths.blacklist")
        
        # 直接使用主窗口
        self.window = parent
        self.window.title(self.window_title)
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        
        # 设置窗口图标
        try:
            logo = tk.PhotoImage(file=self.icon_path)
            self.window.iconphoto(True, logo)
        except Exception as e:
            messagebox.showerror("错误", f"设置图标失败: {e}")
        
        # 窗口居中
        self.center_window(self.window, self.window_width, self.window_height)
        
        # 设置窗口关闭时的处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 清空主窗口
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # 主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左右布局 - 左边占80%，右边占20%
        left_width = int(self.window_width * 0.8)
        right_width = self.window_width - left_width
        
        self.left_frame = ttk.Frame(self.main_frame, width=left_width)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.right_frame = ttk.Frame(self.main_frame, width=right_width)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 构筑选择器
        self.build_selector = BuildSelector(self.left_frame, self.main_app, self.index, self.filter_options, self.on_build_selected)
        
        # 第一行：构筑名
        self.name_frame = ttk.Frame(self.left_frame, padding="5")
        self.name_frame.pack(fill=tk.X)
        
        ttk.Label(self.name_frame, text="构筑:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        self.name_var = tk.StringVar(value=self.filter_data.get("name", ""))
        # 增加宽度以更好地利用空间
        ttk.Entry(self.name_frame, textvariable=self.name_var, width=60).pack(side=tk.LEFT, expand=True, anchor=tk.W)
        
        # 第二行：类型选择按钮
        self.type_frame = ttk.Frame(self.left_frame, padding="5")
        self.type_frame.pack(fill=tk.X)
        
        ttk.Label(self.type_frame, text="类型:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        
        self.type_var = tk.StringVar(value="must")
        type_buttons_frame = ttk.Frame(self.type_frame)
        type_buttons_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Radiobutton(type_buttons_frame, text="必选词条", value="must", variable=self.type_var, command=self.update_pool).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_buttons_frame, text="可选词条", value="extra", variable=self.type_var, command=self.update_pool).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_buttons_frame, text="黑名单词条", value="ban", variable=self.type_var, command=self.update_pool).pack(side=tk.LEFT, padx=5)
        
        # 过滤行
        self.filter_frame = ttk.Frame(self.left_frame, padding="5")
        self.filter_frame.pack(fill=tk.X)
        
        ttk.Label(self.filter_frame, text="过滤:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建下拉框
        self.filter_var = tk.StringVar()
        # 默认选中"2 必选"
        self.filter_var.set("2 必选")
        # 更新score值
        self.filter_data["score"] = self.filter_options["2 必选"]
        
        # 增加宽度以更好地利用空间
        filter_combobox = ttk.Combobox(self.filter_frame, textvariable=self.filter_var, values=list(self.filter_options.keys()), width=58, state="readonly")
        filter_combobox.pack(side=tk.LEFT, expand=True, anchor=tk.W)
        filter_combobox.bind("<<ComboboxSelected>>", self.on_filter_selected)
        
        # 搜索行
        self.search_frame = ttk.Frame(self.left_frame, padding="5")
        self.search_frame.pack(fill=tk.X)
        
        ttk.Label(self.search_frame, text="搜索:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry_frame = ttk.Frame(self.search_frame)
        search_entry_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry = ttk.Entry(search_entry_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self.update_pool)
        
        ttk.Button(self.search_frame, text="清空", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # 加载数据
        self.load_entries()
        
        # 词条池子
        self.entry_pool = EntryPool(self.left_frame, self.entries, self.blacklist, self.filter_data, self.type_var, self.search_var, self.move_to_build_pool)
        
        # 构筑池子
        self.build_pool = BuildPool(self.left_frame, self.entries, self.blacklist, self.filter_data, self.type_var, self.search_var, self.move_to_entry_pool)
        
        # 右边：详情页
        self.detail_view = DetailView(self.right_frame, self.entries, self.blacklist, self.type_var)
        
        # 绑定列表点击事件
        self.entry_pool.tree.bind("<<TreeviewSelect>>", self.update_detail)
        self.build_pool.tree.bind("<<TreeviewSelect>>", self.update_detail)
        
        # 按钮框架
        self.button_frame = ttk.Frame(self.right_frame, padding="5")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # 清空池子按钮
        self.clear_pool_button = ttk.Button(self.button_frame, text="清空池子", command=self.clear_pool)
        self.clear_pool_button.pack(side=tk.LEFT, padx=5)
        
        # 清空构筑按钮
        self.clear_build_button = ttk.Button(self.button_frame, text="清空构筑", command=self.clear_build)
        self.clear_build_button.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        self.save_button = ttk.Button(self.button_frame, text="保存", command=self.save)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # 更新池子
        self.update_pool()
    
    def center_window(self, window, width, height):
        # 获取屏幕宽度和高度
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算窗口位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_entries(self):
        # 加载entry.json和blacklist.json
        try:
            with open(self.entries_path, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            
            with open(self.blacklist_path, "r", encoding="utf-8") as f:
                self.blacklist = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取词条文件失败: {e}")
            self.entries = {}
            self.blacklist = {}
    
    def clear_search(self):
        # 清空搜索框
        self.search_var.set("")
        # 更新池子
        self.update_pool()
    
    def on_filter_selected(self, event):
        # 获取选中的选项
        selected_option = self.filter_var.get()
        # 更新score值
        if selected_option in self.filter_options:
            self.filter_data["score"] = self.filter_options[selected_option]
    
    def update_pool(self, event=None):
        # 更新 EntryPool 和 BuildPool 中的 filter_data 引用
        self.entry_pool.filter_data = self.filter_data
        self.build_pool.filter_data = self.filter_data
        # 更新词条池子
        self.entry_pool.update()
        # 更新构筑池子
        self.build_pool.update()
    
    def move_to_build_pool(self, event):
        # 获取选中的项
        selected_item = self.entry_pool.get_selection()
        if selected_item:
            entry_id = selected_item[0]
            current_type = self.type_var.get()
            
            # 必选和可选互斥
            if current_type == "must":
                # 如果词条在可选池子中，从可选池子中移除
                if "extra" in self.filter_data and entry_id in self.filter_data["extra"]:
                    self.filter_data["extra"].remove(entry_id)
            elif current_type == "extra":
                # 如果词条在必选池子中，从必选池子中移除
                if "must" in self.filter_data and entry_id in self.filter_data["must"]:
                    self.filter_data["must"].remove(entry_id)
            
            # 添加到构筑池子
            if entry_id not in self.filter_data.get(current_type, []):
                if current_type not in self.filter_data:
                    self.filter_data[current_type] = []
                self.filter_data[current_type].append(entry_id)
            
            # 保存当前选中项的索引
            items = self.entry_pool.get_children()
            current_index = -1
            if items:
                try:
                    current_index = items.index(entry_id)
                except ValueError:
                    pass
            
            # 更新池子
            self.update_pool()
            
            # 自动聚焦到下一项
            new_items = self.entry_pool.get_children()
            if new_items:
                # 计算新的聚焦索引
                new_index = current_index if current_index < len(new_items) else current_index - 1
                if new_index < 0:
                    new_index = 0
                # 聚焦到新的项
                self.entry_pool.selection_set(new_items[new_index])
                self.entry_pool.focus(new_items[new_index])
    
    def move_to_entry_pool(self, event):
        # 获取选中的项
        selected_item = self.build_pool.get_selection()
        if selected_item:
            entry_id = selected_item[0]
            current_type = self.type_var.get()
            
            # 从构筑池子中移除
            if current_type in self.filter_data and entry_id in self.filter_data[current_type]:
                self.filter_data[current_type].remove(entry_id)
            
            # 保存当前选中项的索引
            items = self.build_pool.get_children()
            current_index = -1
            if items:
                try:
                    current_index = items.index(entry_id)
                except ValueError:
                    pass
            
            # 更新池子
            self.update_pool()
            
            # 自动聚焦到下一项
            new_items = self.build_pool.get_children()
            if new_items:
                # 计算新的聚焦索引
                new_index = current_index if current_index < len(new_items) else current_index - 1
                if new_index < 0:
                    new_index = 0
                # 聚焦到新的项
                self.build_pool.selection_set(new_items[new_index])
                self.build_pool.focus(new_items[new_index])
    
    def update_detail(self, event):
        # 检查是哪个树被点击
        widget = event.widget
        selected_item = widget.selection()
        
        if selected_item:
            entry_id = selected_item[0]
            self.detail_view.update(entry_id)
        else:
            self.detail_view.update(None)
    
    def save(self):
        # 更新构筑名
        self.filter_data["name"] = self.name_var.get()
        
        # 保存到主应用
        self.main_app.filters[self.index] = self.filter_data
        self.main_app.save_filters()
        
        # 更新构筑选择下拉框
        self.build_selector.update_build_options()
    
    def clear_pool(self):
        # 弹出提示框
        result = messagebox.askyesno("清空池子", "是否清空当前构筑的池子？")
        if result:
            # 清空当前类型的池子
            current_type = self.type_var.get()
            if current_type in self.filter_data:
                self.filter_data[current_type] = []
            # 更新池子
            self.update_pool()
    
    def clear_build(self):
        # 弹出提示框
        result = messagebox.askyesno("清空构筑", "是否清空当前构筑？")
        if result:
            # 清空必选、可选、黑名单
            self.filter_data["must"] = []
            self.filter_data["extra"] = []
            self.filter_data["ban"] = []
            # 重置过滤为默认值（1必选1可选）
            self.filter_data["score"] = 11
            # 找到对应的过滤选项
            filter_text = "无"
            for option, score_value in self.filter_options.items():
                if score_value == 11:
                    filter_text = option
                    break
            self.filter_var.set(filter_text)
            # 重置搜索
            self.search_var.set("")
            # 更新池子
            self.update_pool()
    
    def on_build_selected(self, new_index):
        # 保存当前构筑的修改
        self.filter_data["name"] = self.name_var.get()
        # 检查索引是否有效
        if 0 <= self.index < len(self.main_app.filters):
            self.main_app.filters[self.index] = self.filter_data
            self.main_app.save_filters()
        
        # 检查新索引是否有效
        if 0 <= new_index < len(self.main_app.filters):
            # 更新当前窗口显示选中的构筑
            self.filter_data = self.main_app.filters[new_index].copy()
            self.original_data = self.main_app.filters[new_index].copy()
            self.index = new_index
            self.build_selector.current_index = new_index
            
            # 更新界面
            self.name_var.set(self.filter_data.get("name", ""))
            
            # 找到对应的过滤选项
            filter_text = "无"
            for option, score_value in self.filter_options.items():
                if score_value == self.filter_data.get("score", 0):
                    filter_text = option
                    break
            self.filter_var.set(filter_text)
            
            # 更新池子
            self.update_pool()
        else:
            messagebox.showerror("错误", "选中的构筑不存在")
    
    def copy_build(self):
        new_index = self.build_selector.copy_build()
        if new_index is not None:
            # 切换到新复制的构筑
            self.filter_data = self.main_app.filters[new_index].copy()
            self.original_data = self.main_app.filters[new_index].copy()
            self.index = new_index
            self.build_selector.current_index = new_index
            
            # 更新界面
            self.name_var.set(self.filter_data.get("name", ""))
            
            # 找到对应的过滤选项
            filter_text = "无"
            for option, score_value in self.filter_options.items():
                if score_value == self.filter_data.get("score", 0):
                    filter_text = option
                    break
            self.filter_var.set(filter_text)
            
            # 更新池子
            self.update_pool()
    
    def add_build(self):
        new_index = self.build_selector.add_build()
        if new_index is not None:
            # 切换到新构筑
            self.filter_data = self.main_app.filters[new_index].copy()
            self.original_data = self.main_app.filters[new_index].copy()
            self.index = new_index
            self.build_selector.current_index = new_index
            
            # 更新界面
            self.name_var.set(self.filter_data.get("name", ""))
            self.filter_var.set("无")
            
            # 更新池子
            self.update_pool()
    
    def delete_build(self):
        new_index = self.build_selector.delete_build()
        if new_index is not None:
            # 切换到新构筑
            self.filter_data = self.main_app.filters[new_index].copy()
            self.original_data = self.main_app.filters[new_index].copy()
            self.index = new_index
            self.build_selector.current_index = new_index
            
            # 更新界面
            self.name_var.set(self.filter_data.get("name", ""))
            
            # 找到对应的过滤选项
            filter_text = "无"
            for option, score_value in self.filter_options.items():
                if score_value == self.filter_data.get("score", 0):
                    filter_text = option
                    break
            self.filter_var.set(filter_text)
            
            # 更新池子
            self.update_pool()
    
    def on_close(self):
        # 检查是否有修改
        if self.filter_data != self.original_data or self.name_var.get() != self.original_data.get("name", ""):
            # 提示用户是否保存
            result = messagebox.askyesno("保存", "是否保存修改？")
            if result:
                self.save()
        # 关闭窗口
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()