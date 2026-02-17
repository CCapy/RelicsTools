import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import os

class SettingWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("设置")
        self.root.geometry("500x400")
        
        self.data_map = self.load_data_map()
        self.full_data = self.load_full_data()
        self.blacklist_map = self.load_blacklist_map()
        self.full_blacklist = self.load_full_blacklist()
        
        # 窗口居中
        self.center_window()
        
        # 创建主框架2
        main_frame = tk.Frame(self.root, padx=5, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 基础设置分组
        base_settings_frame = tk.LabelFrame(main_frame, text="基础设置")
        base_settings_frame.pack(fill=tk.X)
        
        # ID标签和输入框
        id_frame = tk.Frame(base_settings_frame)
        id_frame.pack(fill=tk.X, pady=5, padx=5)
        
        id_label = tk.Label(id_frame, text="ID", width=5)
        id_label.pack(side=tk.LEFT)
        
        self.id_entry = tk.Entry(id_frame)
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 保存按钮
        save_button = tk.Button(base_settings_frame, text="保存", command=self.save_id, width=10, height=1, padx=5, pady=5)
        save_button.pack(side=tk.BOTTOM, anchor=tk.E, pady=10, padx=10)
        
        # 加载当前ID
        self.load_id()
        

        
        # 词条过滤分组
        filter_frame = tk.LabelFrame(main_frame, text="词条过滤")
        filter_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = tk.Frame(filter_frame)
        button_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 添加按钮
        add_button = tk.Button(button_frame, text="创建", command=self.add_bd_item, width=10, height=1)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮（红色）
        delete_button = tk.Button(button_frame, text="删除", command=self.delete_selected_bd_item, width=10, height=1, fg="white", bg="red")
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 创建Treeview组件
        columns = ("index", "name", "key1", "key2", "key3", "blacklist")
        self.tree = ttk.Treeview(filter_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.tree.heading("index", text="索引", anchor=tk.CENTER)
        self.tree.heading("name", text="名字", anchor=tk.CENTER)
        self.tree.heading("key1", text="词条1", anchor=tk.CENTER)
        self.tree.heading("key2", text="词条2", anchor=tk.CENTER)
        self.tree.heading("key3", text="词条3", anchor=tk.CENTER)
        self.tree.heading("blacklist", text="黑名单", anchor=tk.CENTER)
        
        # 设置列宽度和对齐方式
        self.tree.column("index", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=100, anchor=tk.CENTER)
        self.tree.column("key1", width=60, anchor=tk.CENTER)
        self.tree.column("key2", width=60, anchor=tk.CENTER)
        self.tree.column("key3", width=60, anchor=tk.CENTER)
        self.tree.column("blacklist", width=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(filter_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 打包Treeview
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # 加载词条数据
        self.load_bd_data()
    
    def load_data_map(self):
        """加载data.json，建立key-name映射"""
        data_path = os.path.join(os.path.dirname(__file__), "data.json")
        data_map = {}
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if "name" in value:
                            data_map[key] = value["name"]
            except Exception as e:
                print(f"加载data.json失败: {e}")
        return data_map
    
    def load_full_data(self):
        """加载完整的data.json数据"""
        data_path = os.path.join(os.path.dirname(__file__), "data.json")
        full_data = {}
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    full_data = json.load(f)
            except Exception as e:
                print(f"加载data.json失败: {e}")
        return full_data
    
    def load_blacklist_map(self):
        """加载blacklist.json，建立key-name映射"""
        blacklist_path = os.path.join(os.path.dirname(__file__), "blacklist.json")
        blacklist_map = {}
        if os.path.exists(blacklist_path):
            try:
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if "name" in value:
                            blacklist_map[key] = value["name"]
            except Exception as e:
                print(f"加载blacklist.json失败: {e}")
        return blacklist_map
    
    def load_full_blacklist(self):
        """加载完整的blacklist.json数据"""
        blacklist_path = os.path.join(os.path.dirname(__file__), "blacklist.json")
        full_blacklist = {}
        if os.path.exists(blacklist_path):
            try:
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    full_blacklist = json.load(f)
            except Exception as e:
                print(f"加载blacklist.json失败: {e}")
        return full_blacklist
    
    def load_id(self):
        """加载当前ID从config.json"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "id" in config:
                        self.id_entry.insert(0, config["id"])
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def load_bd_data(self):
        """加载bd数组数据到Treeview"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "bd" in config and isinstance(config["bd"], list):
                        # 清空现有数据
                        for item in self.tree.get_children():
                            self.tree.delete(item)
                        
                        # 添加新数据
                        for i, item in enumerate(config["bd"]):
                            index = i + 1
                            name = item.get("name", "")
                            key1_len = len(item.get("key1", []))
                            key2_len = len(item.get("key2", []))
                            key3_len = len(item.get("key3", []))
                            blacklist_len = len(item.get("blacklist", []))
                            
                            self.tree.insert("", tk.END, values=(index, name, key1_len, key2_len, key3_len, blacklist_len))
            except Exception as e:
                print(f"加载bd数据失败: {e}")
    
    def on_tree_double_click(self, event):
        """双击Treeview内容时的处理"""
        # 获取双击的行
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # 获取行数据
        values = self.tree.item(item, "values")
        if not values:
            return
        
        # 获取索引（从1开始）
        index = int(values[0])
        # 转换为数组索引（从0开始）
        bd_index = index - 1
        
        # 读取config.json中的bd数据
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "bd" in config and isinstance(config["bd"], list):
                        if 0 <= bd_index < len(config["bd"]):
                            bd_item = config["bd"][bd_index]
                            
                            # 弹出词条设置窗口（模态）
                            self.open_term_setting_window(bd_item, bd_index)
            except Exception as e:
                print(f"读取bd数据失败: {e}")
    
    def confirm_delete(self, term_window, bd_index):
        """确认删除提示"""
        # 弹出确认对话框
        result = messagebox.askyesno("确认", "是否删除该条目？")
        if result:
            # 执行删除操作
            self.delete_bd_item(bd_index)
            # 关闭窗口
            term_window.destroy()
        # 否则对话框消失，不做任何操作
    
    def delete_bd_item(self, bd_index):
        """从bd中删除指定索引的元素"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                # 读取配置
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 删除元素
                if "bd" in config and isinstance(config["bd"], list):
                    if 0 <= bd_index < len(config["bd"]):
                        del config["bd"][bd_index]
                        
                        # 保存配置
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
                        
                        print(f"成功删除索引 {bd_index + 1} 的条目")
                        
                        # 刷新Treeview
                        self.load_bd_data()
            except Exception as e:
                print(f"删除条目失败: {e}")
                messagebox.showerror("错误", f"删除失败: {e}")
    
    def save_and_close(self, term_window, bd_index, name_value):
        """保存修改并关闭窗口"""
        # 保存构筑名字
        self.save_bd_name(bd_index, name_value)
        # 关闭窗口
        term_window.destroy()
    
    def save_bd_name(self, bd_index, name_value):
        """保存bd条目的名字"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                # 读取配置
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 更新名字
                if "bd" in config and isinstance(config["bd"], list):
                    if 0 <= bd_index < len(config["bd"]):
                        config["bd"][bd_index]["name"] = name_value
                        
                        # 保存配置
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
                        
                        # 刷新Treeview
                        self.load_bd_data()
            except Exception as e:
                print(f"保存名字失败: {e}")
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def add_bd_item(self):
        """在bd数组中添加空元素"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                # 读取配置
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 确保bd是数组
                if "bd" not in config or not isinstance(config["bd"], list):
                    config["bd"] = []
                
                # 创建空元素
                empty_item = {
                    "name": "",
                    "key1": [],
                    "key2": [],
                    "key3": [],
                    "blacklist": []
                }
                
                # 添加到数组
                config["bd"].append(empty_item)
                
                # 保存配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"成功添加新的空条目，当前总数: {len(config['bd'])}")
                
                # 刷新Treeview
                self.load_bd_data()
            except Exception as e:
                print(f"添加条目失败: {e}")
                messagebox.showerror("错误", f"添加失败: {e}")
    
    def delete_selected_bd_item(self):
        """删除选中的bd条目"""
        # 获取选中的行
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要删除的条目")
            return
        
        # 获取选中行的值
        values = self.tree.item(selected_items[0], "values")
        if not values:
            return
        
        # 获取索引（从1开始）
        index = int(values[0])
        # 转换为数组索引（从0开始）
        bd_index = index - 1
        
        # 弹出确认对话框
        result = messagebox.askyesno("确认", f"是否删除索引 {index} 的条目？")
        if result:
            # 执行删除操作
            self.delete_bd_item(bd_index)
    

    
    def open_term_setting_window(self, bd_item, bd_index):
        """打开词条设置模态窗口"""
        # 创建模态窗口
        term_window = tk.Toplevel(self.root)
        term_window.title("词条设置")
        term_window.geometry("1200x500")
        term_window.transient(self.root)  # 设置为主窗口的子窗口
        term_window.grab_set()  # 模态窗口，阻止操作主窗口
        
        # 窗口居中
        window_width = 1200
        window_height = 500
        screen_width = term_window.winfo_screenwidth()
        screen_height = term_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        term_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = tk.Frame(term_window, padx=5, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 构筑名字输入框
        name_frame = tk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = tk.Label(name_frame, text="构筑名字", width=10)
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_var = tk.StringVar(value=bd_item.get('name', ''))
        name_entry = tk.Entry(name_frame, textvariable=name_var)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 操作词条下拉选择框
        term_frame = tk.Frame(main_frame)
        term_frame.pack(fill=tk.X, pady=5)
        
        term_label = tk.Label(term_frame, text="操作词条", width=10)
        term_label.pack(side=tk.LEFT, padx=5)
        
        # 下拉选项：对应key1-key3和blacklist
        term_options = ["词条1", "词条2", "词条3", "黑名单"]
        term_var = tk.StringVar()
        term_dropdown = ttk.Combobox(term_frame, textvariable=term_var, values=term_options, state="readonly")
        term_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 使用after方法延迟设置值，确保窗口已完全创建
        term_window.after(100, lambda: term_dropdown.set(term_options[0]))
        term_window.after(100, lambda: term_dropdown.current(0))
        
        # 映射词条类型到bd字段
        term_field_map = {
            "词条1": "key1",
            "词条2": "key2",
            "词条3": "key3",
            "黑名单": "blacklist"
        }
        
        # 词条编辑区域
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧：所有词条
        left_frame = tk.Frame(edit_frame)
        left_frame.pack(fill=tk.BOTH, expand=True, pady=5, side=tk.LEFT, padx=5)
        
        # 所有词条列表
        result_frame = tk.LabelFrame(left_frame, text="所有词条")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 所有词条搜索（放在分组内）
        all_search_frame = tk.Frame(result_frame)
        all_search_frame.pack(fill=tk.X, pady=5, padx=5)
        
        all_search_label = tk.Label(all_search_frame, text="搜索", width=8)
        all_search_label.pack(side=tk.LEFT, padx=5)
        
        all_search_var = tk.StringVar()
        all_search_entry = tk.Entry(all_search_frame, textvariable=all_search_var)
        all_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 创建所有词条Treeview（移除key列）
        result_columns = ("name", "type", "explanation", "superposability", "note")
        result_tree = ttk.Treeview(result_frame, columns=result_columns, show="headings")
        result_tree.heading("name", text="名称", anchor=tk.CENTER)
        result_tree.heading("type", text="类型", anchor=tk.CENTER)
        result_tree.heading("explanation", text="说明", anchor=tk.CENTER)
        result_tree.heading("superposability", text="可叠加性", anchor=tk.CENTER)
        result_tree.heading("note", text="备注", anchor=tk.CENTER)
        
        result_tree.column("name", width=120, anchor=tk.CENTER)
        result_tree.column("type", width=80, anchor=tk.CENTER)
        result_tree.column("explanation", width=180, anchor=tk.CENTER)
        result_tree.column("superposability", width=80, anchor=tk.CENTER)
        result_tree.column("note", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_tree.yview)
        result_tree.configure(yscroll=result_scrollbar.set)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：当前词条
        right_frame = tk.Frame(edit_frame)
        right_frame.pack(fill=tk.BOTH, expand=True, pady=5, side=tk.RIGHT, padx=5)
        
        # 当前词条列表
        current_frame = tk.LabelFrame(right_frame, text="当前词条")
        current_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 当前词条搜索（放在分组内）
        current_search_frame = tk.Frame(current_frame)
        current_search_frame.pack(fill=tk.X, pady=5, padx=5)
        
        current_search_label = tk.Label(current_search_frame, text="搜索", width=8)
        current_search_label.pack(side=tk.LEFT, padx=5)
        
        current_search_var = tk.StringVar()
        current_search_entry = tk.Entry(current_search_frame, textvariable=current_search_var)
        current_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 创建当前词条Treeview（移除key列）
        current_columns = ("name", "type", "explanation", "superposability", "note")
        current_tree = ttk.Treeview(current_frame, columns=current_columns, show="headings")
        current_tree.heading("name", text="名称", anchor=tk.CENTER)
        current_tree.heading("type", text="类型", anchor=tk.CENTER)
        current_tree.heading("explanation", text="说明", anchor=tk.CENTER)
        current_tree.heading("superposability", text="可叠加性", anchor=tk.CENTER)
        current_tree.heading("note", text="备注", anchor=tk.CENTER)
        
        current_tree.column("name", width=120, anchor=tk.CENTER)
        current_tree.column("type", width=80, anchor=tk.CENTER)
        current_tree.column("explanation", width=180, anchor=tk.CENTER)
        current_tree.column("superposability", width=80, anchor=tk.CENTER)
        current_tree.column("note", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        current_scrollbar = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, command=current_tree.yview)
        current_tree.configure(yscroll=current_scrollbar.set)
        current_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        current_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定变量和方法
        term_field = term_field_map.get(term_var.get(), "key1")
        current_terms = bd_item.get(term_field, [])
        
        # 加载当前词条
        def load_current_terms():
            # 清空现有结果
            for item in current_tree.get_children():
                current_tree.delete(item)
            
            # 获取当前字段类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 根据字段类型选择数据来源
            data_source = self.full_blacklist if term_field == "blacklist" else self.full_data
            
            # 加载当前词条
            for key in current_terms:
                if key in data_source:
                    item_data = data_source[key]
                    name = item_data.get("name", key)
                    type_ = item_data.get("type", "")
                    explanation = item_data.get("explanation", "")
                    superposability = item_data.get("superposability", "")
                    note = item_data.get("note", "")
                    current_tree.insert("", tk.END, values=(name, type_, explanation, superposability, note))
        
        # 搜索所有词条（只显示不在当前词条中的）
        def search_all_terms():
            keyword = all_search_var.get()
            # 清空现有结果
            for item in result_tree.get_children():
                result_tree.delete(item)
            
            # 获取当前字段类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 根据字段类型选择数据来源
            data_source = self.full_blacklist if term_field == "blacklist" else self.full_data
            
            # 搜索匹配的词条，排除当前已有的
            for key, item_data in data_source.items():
                # 跳过当前已有的词条
                if key in current_terms:
                    continue
                
                # 如果是key1-key3字段，还要跳过其他key字段中已有的词条
                if term_field in ["key1", "key2", "key3"]:
                    # 检查其他key字段
                    for other_field in ["key1", "key2", "key3"]:
                        if other_field != term_field and key in bd_item.get(other_field, []):
                            continue
                
                # 检查搜索条件
                name = item_data.get("name", key)
                type_ = item_data.get("type", "")
                explanation = item_data.get("explanation", "")
                note = item_data.get("note", "")
                
                if not keyword or \
                   keyword.lower() in name.lower() or \
                   keyword.lower() in type_.lower() or \
                   keyword.lower() in explanation.lower() or \
                   keyword.lower() in note.lower() or \
                   keyword in key:
                    # 显示符合条件的词条，不包含key列
                    superposability = item_data.get("superposability", "")
                    result_tree.insert("", tk.END, values=(name, type_, explanation, superposability, note))
        
        # 搜索当前词条
        def search_current_terms():
            keyword = current_search_var.get()
            # 清空现有结果
            for item in current_tree.get_children():
                current_tree.delete(item)
            
            # 获取当前字段类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 根据字段类型选择数据来源
            data_source = self.full_blacklist if term_field == "blacklist" else self.full_data
            
            # 搜索匹配的当前词条
            for key in current_terms:
                if key in data_source:
                    item_data = data_source[key]
                    name = item_data.get("name", key)
                    type_ = item_data.get("type", "")
                    explanation = item_data.get("explanation", "")
                    note = item_data.get("note", "")
                    
                    if not keyword or \
                       keyword.lower() in name.lower() or \
                       keyword.lower() in type_.lower() or \
                       keyword.lower() in explanation.lower() or \
                       keyword.lower() in note.lower() or \
                       keyword in key:
                        # 显示符合条件的词条，不包含key列
                        superposability = item_data.get("superposability", "")
                        current_tree.insert("", tk.END, values=(name, type_, explanation, superposability, note))
        
        # 刷新所有列表
        def refresh_lists():
            # 更新词条字段
            term_field = term_field_map.get(term_var.get(), "key1")
            # 更新当前词条列表
            nonlocal current_terms
            current_terms = bd_item.get(term_field, [])
            # 重新加载当前词条
            load_current_terms()
            # 重新搜索所有词条
            search_all_terms()
        
        # 绑定所有词条搜索事件
        def on_all_search(*args):
            search_all_terms()
        
        all_search_var.trace_add("write", on_all_search)
        
        # 绑定当前词条搜索事件
        def on_current_search(*args):
            search_current_terms()
        
        current_search_var.trace_add("write", on_current_search)
        
        # 绑定下拉框变化事件
        def on_term_type_change(*args):
            refresh_lists()
        
        term_var.trace_add("write", on_term_type_change)
        
        # 绑定双击添加（从所有词条到当前词条）
        def on_result_double_click(event):
            # 使用事件对象获取鼠标点击的条目
            item = result_tree.identify_row(event.y)
            if not item:
                return
            
            # 选中点击的条目，提供视觉反馈
            result_tree.selection_set(item)
            
            # 获取点击条目的值
            values = result_tree.item(item, "values")
            if not values:
                return
            
            name = values[0]
            # 获取当前字段类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 根据字段类型选择数据来源
            data_source = self.full_blacklist if term_field == "blacklist" else self.full_data
            
            # 通过名称查找对应的key
            key = None
            for k, v in data_source.items():
                if v.get("name", "") == name:
                    key = k
                    break
            
            if not key:
                return
            
            # 检查是否已存在
            if key not in current_terms:
                # 如果是key1-key3字段，还要检查其他key字段
                if term_field in ["key1", "key2", "key3"]:
                    # 检查其他key字段
                    duplicate = False
                    for other_field in ["key1", "key2", "key3"]:
                        if other_field != term_field and key in bd_item.get(other_field, []):
                            duplicate = True
                            break
                    
                    if duplicate:
                        messagebox.showinfo("提示", f"该词条已存在于其他key字段中，不允许重复添加")
                        return
                
                # 添加小延迟，让用户看到选中效果
                def add_term():
                    current_terms.append(key)
                    # 更新显示
                    load_current_terms()
                    # 重新搜索所有词条
                    search_all_terms()
                
                term_window.after(100, add_term)
        
        result_tree.bind('<Double-1>', on_result_double_click)
        
        # 绑定双击删除（从当前词条中删除）
        def on_current_double_click(event):
            # 使用事件对象获取鼠标点击的条目
            item = current_tree.identify_row(event.y)
            if not item:
                return
            
            # 选中点击的条目，提供视觉反馈
            current_tree.selection_set(item)
            
            # 获取点击条目的值
            values = current_tree.item(item, "values")
            if not values:
                return
            
            name = values[0]
            # 获取当前字段类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 根据字段类型选择数据来源
            data_source = self.full_blacklist if term_field == "blacklist" else self.full_data
            
            # 通过名称查找对应的key
            key = None
            for k, v in data_source.items():
                if v.get("name", "") == name:
                    key = k
                    break
            
            if not key:
                return
            
            # 从列表中删除
            if key in current_terms:
                # 添加小延迟，让用户看到选中效果
                def remove_term():
                    current_terms.remove(key)
                    # 更新显示
                    load_current_terms()
                    # 重新搜索所有词条
                    search_all_terms()
                
                term_window.after(100, remove_term)
        
        current_tree.bind('<Double-1>', on_current_double_click)
        
        # 初始加载
        load_current_terms()
        search_all_terms()
        
        # 保存时更新词条
        def save_and_close_with_terms(term_window, bd_index, name_value):
            # 获取当前选中的词条类型
            term_field = term_field_map.get(term_var.get(), "key1")
            # 更新bd_item
            bd_item[term_field] = current_terms
            # 保存构筑名字
            self.save_bd_name(bd_index, name_value)
            # 保存整个bd条目
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                try:
                    # 读取配置
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 更新bd条目
                    if "bd" in config and isinstance(config["bd"], list):
                        if 0 <= bd_index < len(config["bd"]):
                            config["bd"][bd_index] = bd_item
                            
                            # 保存配置
                            with open(config_path, 'w', encoding='utf-8') as f:
                                json.dump(config, f, indent=2, ensure_ascii=False)
                            
                            
                            # 刷新主界面的Treeview组件
                            self.load_bd_data()
                except Exception as e:
                    print(f"保存词条数据失败: {e}")
                    messagebox.showerror("错误", f"保存失败: {e}")
            # 关闭窗口
            term_window.destroy()
        
        # 重新绑定保存方法
        self.save_and_close = save_and_close_with_terms
        
        # 按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        # 删除按钮（红色）
        delete_button = tk.Button(button_frame, text="删除", command=lambda: self.confirm_delete(term_window, bd_index), 
                                width=10, height=1, padx=5, pady=5, fg="white", bg="red")
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        exit_button = tk.Button(button_frame, text="退出", command=lambda: self.save_and_close(term_window, bd_index, name_var.get()), 
                               width=10, height=1, padx=5, pady=5)
        exit_button.pack(side=tk.RIGHT, padx=5)
        
        # 绑定窗口关闭事件
        term_window.protocol("WM_DELETE_WINDOW", lambda: self.save_and_close(term_window, bd_index, name_var.get()))
    
    def center_window(self):
        """窗口居中显示"""
        # 获取窗口尺寸
        window_width = 500
        window_height = 400
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def save_id(self):
        """保存ID到config.json"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        id_value = self.id_entry.get()
        
        try:
            # 读取现有配置
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # 更新ID
            config["id"] = id_value
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("提示", "ID保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingWindow(root)
    root.mainloop()