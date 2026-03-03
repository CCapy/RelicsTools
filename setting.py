import json
import tkinter as tk
from tkinter import ttk, messagebox

class FilterEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("构筑编辑器")
        self.root.geometry("600x400")
        
        # 窗口居中
        self.center_window(self.root, 600, 400)
        
        # 读取filters.json文件
        self.filters_path = "config/filters.json"
        self.filters = self.load_filters()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview组件
        self.tree = ttk.Treeview(self.main_frame, columns=("name", "must", "extra", "ban", "score"), show="headings")
        
        # 设置列标题
        self.tree.heading("name", text="构筑名", anchor=tk.CENTER)
        self.tree.heading("must", text="必选词条", anchor=tk.CENTER)
        self.tree.heading("extra", text="可选词条", anchor=tk.CENTER)
        self.tree.heading("ban", text="黑名单词条", anchor=tk.CENTER)
        self.tree.heading("score", text="得分", anchor=tk.CENTER)
        
        # 设置列宽和对齐方式
        self.tree.column("name", width=100, anchor=tk.CENTER)
        self.tree.column("must", width=100, anchor=tk.CENTER)
        self.tree.column("extra", width=100, anchor=tk.CENTER)
        self.tree.column("ban", width=100, anchor=tk.CENTER)
        self.tree.column("score", width=100, anchor=tk.CENTER)
        
        # 填充数据
        self.populate_tree()
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.edit_filter)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.pack(fill=tk.X)
        
        # 添加按钮
        self.add_button = ttk.Button(self.button_frame, text="添加", command=self.add_filter)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮
        self.delete_button = ttk.Button(self.button_frame, text="删除", command=self.delete_filter)
        self.delete_button.pack(side=tk.LEFT, padx=5)
    
    def center_window(self, window, width, height):
        # 获取屏幕宽度和高度
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算窗口位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_filters(self):
        try:
            with open(self.filters_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"读取文件失败: {e}")
            return []
    
    def save_filters(self):
        try:
            with open(self.filters_path, "w", encoding="utf-8") as f:
                json.dump(self.filters, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def populate_tree(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充新数据
        for i, filter_data in enumerate(self.filters):
            name = filter_data.get("name", "")
            must_len = len(filter_data.get("must", []))
            extra_len = len(filter_data.get("extra", []))
            ban_len = len(filter_data.get("ban", []))
            score = filter_data.get("score", 0)
            
            self.tree.insert("", tk.END, iid=str(i), values=(name, must_len, extra_len, ban_len, score))
    
    def add_filter(self):
        # 这里可以添加添加新构筑的逻辑
        # 暂时只添加一个空构筑
        new_filter = {
            "name": "新构筑",
            "must": [],
            "extra": [],
            "ban": [],
            "score": 0
        }
        self.filters.append(new_filter)
        self.save_filters()
        self.populate_tree()
    
    def delete_filter(self):
        # 获取选中的项
        selected_item = self.tree.selection()
        if selected_item:
            # 获取选中项的索引
            index = int(selected_item[0])
            # 删除对应的过滤器
            if 0 <= index < len(self.filters):
                self.filters.pop(index)
                self.save_filters()
                self.populate_tree()
                # 重新选中合适的项
                if len(self.filters) > 0:
                    # 如果删除后还有后续项，则向下聚焦（保持在当前索引，因为后续项会前移）
                    # 如果删除的是最后一项，则向上聚焦到前一个索引
                    new_index = index if index < len(self.filters) else index - 1
                    self.tree.selection_set(str(new_index))
                    self.tree.focus(str(new_index))
    
    def edit_filter(self, event):
        # 获取选中的项
        selected_item = self.tree.selection()
        if selected_item:
            # 获取选中项的索引
            index = int(selected_item[0])
            # 创建编辑窗口
            EditFilterWindow(self.root, self.filters[index], index, self)

class EditFilterWindow:
    def __init__(self, parent, filter_data, index, main_app):
        self.parent = parent
        self.filter_data = filter_data.copy()
        self.original_data = filter_data.copy()
        self.index = index
        self.main_app = main_app
        
        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("编辑构筑")
        self.window.geometry("900x600")
        
        # 窗口居中
        self.center_window(self.window, 900, 600)
        
        # 设置窗口关闭时的处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左右布局
        self.left_frame = ttk.Frame(self.main_frame, width=450)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.right_frame = ttk.Frame(self.main_frame, width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 第一行：构筑名
        self.name_frame = ttk.Frame(self.left_frame, padding="5")
        self.name_frame.pack(fill=tk.X)
        
        ttk.Label(self.name_frame, text="构筑:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))
        self.name_var = tk.StringVar(value=self.filter_data.get("name", ""))
        ttk.Entry(self.name_frame, textvariable=self.name_var, width=40).pack(side=tk.LEFT, expand=True, anchor=tk.W)
        
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
        
        # 过滤选项
        self.filter_options = {
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
        }
        
        # 创建下拉框
        self.filter_var = tk.StringVar()
        # 默认选中"2 必选"
        self.filter_var.set("2 必选")
        # 更新score值
        self.filter_data["score"] = self.filter_options["2 必选"]
        
        filter_combobox = ttk.Combobox(self.filter_frame, textvariable=self.filter_var, values=list(self.filter_options.keys()), width=38, state="readonly")
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
        
        # 第三行：词条池子
        self.entry_pool_frame = ttk.LabelFrame(self.left_frame, text="词条池子", padding="5")
        self.entry_pool_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 词条池子Treeview
        self.entry_pool_tree = ttk.Treeview(self.entry_pool_frame, columns=("id", "name", "superposability"), show="headings")
        self.entry_pool_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.entry_pool_tree.heading("name", text="词条名", anchor=tk.CENTER)
        self.entry_pool_tree.heading("superposability", text="叠加", anchor=tk.CENTER)
        
        self.entry_pool_tree.column("id", width=100, anchor=tk.CENTER)
        self.entry_pool_tree.column("name", width=200, anchor=tk.CENTER)
        self.entry_pool_tree.column("superposability", width=100, anchor=tk.CENTER)
        
        # 绑定双击事件
        self.entry_pool_tree.bind("<Double-1>", self.move_to_build_pool)
        
        # 滚动条
        entry_pool_scrollbar = ttk.Scrollbar(self.entry_pool_frame, orient=tk.VERTICAL, command=self.entry_pool_tree.yview)
        self.entry_pool_tree.configure(yscroll=entry_pool_scrollbar.set)
        entry_pool_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entry_pool_tree.pack(fill=tk.BOTH, expand=True)
        
        # 第四行：构筑池子
        self.build_pool_frame = ttk.LabelFrame(self.left_frame, text="构筑池子", padding="5")
        self.build_pool_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 构筑池子Treeview
        self.build_pool_tree = ttk.Treeview(self.build_pool_frame, columns=("id", "name", "superposability"), show="headings")
        self.build_pool_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.build_pool_tree.heading("name", text="词条名", anchor=tk.CENTER)
        self.build_pool_tree.heading("superposability", text="叠加", anchor=tk.CENTER)
        
        self.build_pool_tree.column("id", width=100, anchor=tk.CENTER)
        self.build_pool_tree.column("name", width=200, anchor=tk.CENTER)
        self.build_pool_tree.column("superposability", width=100, anchor=tk.CENTER)
        
        # 绑定双击事件
        self.build_pool_tree.bind("<Double-1>", self.move_to_entry_pool)
        
        # 滚动条
        build_pool_scrollbar = ttk.Scrollbar(self.build_pool_frame, orient=tk.VERTICAL, command=self.build_pool_tree.yview)
        self.build_pool_tree.configure(yscroll=build_pool_scrollbar.set)
        build_pool_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.build_pool_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右边：详情页
        self.detail_frame = ttk.LabelFrame(self.right_frame, text="详情", padding="10")
        self.detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 详情内容
        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定列表点击事件
        self.entry_pool_tree.bind("<<TreeviewSelect>>", self.update_detail)
        self.build_pool_tree.bind("<<TreeviewSelect>>", self.update_detail)
        
        # 保存按钮
        self.save_button = ttk.Button(self.right_frame, text="保存", command=self.save)
        self.save_button.pack(side=tk.BOTTOM, pady=10)
        
        # 加载数据
        self.load_entries()
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
            with open("asset/entry.json", "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            
            with open("asset/blacklist.json", "r", encoding="utf-8") as f:
                self.blacklist = json.load(f)
        except Exception as e:
            print(f"读取词条文件失败: {e}")
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
        # 清空词条池子
        for item in self.entry_pool_tree.get_children():
            self.entry_pool_tree.delete(item)
        
        # 清空构筑池子
        for item in self.build_pool_tree.get_children():
            self.build_pool_tree.delete(item)
        
        # 获取当前类型
        current_type = self.type_var.get()
        
        # 获取搜索关键词
        search_keyword = self.search_var.get().lower()
        
        # 加载词条池子
        if current_type == "ban":
            # 黑名单使用blacklist.json
            for entry_id, entry_data in self.blacklist.items():
                # 检查是否已在构筑池子中
                if entry_id not in self.filter_data.get(current_type, []):
                    # 检查搜索关键词
                    if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                        self.entry_pool_tree.insert("", tk.END, iid=entry_id, values=(
                            entry_id, 
                            entry_data.get("name", ""), 
                            entry_data.get("superposability", "")
                        ))
        else:
            # 必选和可选使用entry.json
            for entry_id, entry_data in self.entries.items():
                # 检查是否已在构筑池子中
                # 必选和可选互斥
                if current_type == "must":
                    # 检查是否在必选或可选池子中
                    if entry_id not in self.filter_data.get("must", []) and entry_id not in self.filter_data.get("extra", []):
                        # 检查搜索关键词
                        if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                            self.entry_pool_tree.insert("", tk.END, iid=entry_id, values=(
                                entry_id, 
                                entry_data.get("name", ""), 
                                entry_data.get("superposability", "")
                            ))
                elif current_type == "extra":
                    # 检查是否在必选或可选池子中
                    if entry_id not in self.filter_data.get("must", []) and entry_id not in self.filter_data.get("extra", []):
                        # 检查搜索关键词
                        if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                            self.entry_pool_tree.insert("", tk.END, iid=entry_id, values=(
                                entry_id, 
                                entry_data.get("name", ""), 
                                entry_data.get("superposability", "")
                            ))
        
        # 加载构筑池子
        current_pool = self.filter_data.get(current_type, [])
        for entry_id in current_pool:
            # 获取词条数据
            if current_type == "ban":
                entry_data = self.blacklist.get(entry_id, {})
            else:
                entry_data = self.entries.get(entry_id, {})
            
            # 检查搜索关键词
            if not search_keyword or search_keyword in entry_id or search_keyword in entry_data.get("name", "").lower():
                self.build_pool_tree.insert("", tk.END, iid=entry_id, values=(
                    entry_id, 
                    entry_data.get("name", ""), 
                    entry_data.get("superposability", "")
                ))
    
    def move_to_build_pool(self, event):
        # 获取选中的项
        selected_item = self.entry_pool_tree.selection()
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
            items = self.entry_pool_tree.get_children()
            current_index = -1
            if items:
                try:
                    current_index = items.index(entry_id)
                except ValueError:
                    pass
            
            # 更新池子
            self.update_pool()
            
            # 自动聚焦到下一项
            new_items = self.entry_pool_tree.get_children()
            if new_items:
                # 计算新的聚焦索引
                new_index = current_index if current_index < len(new_items) else current_index - 1
                if new_index < 0:
                    new_index = 0
                # 聚焦到新的项
                self.entry_pool_tree.selection_set(new_items[new_index])
                self.entry_pool_tree.focus(new_items[new_index])
    
    def move_to_entry_pool(self, event):
        # 获取选中的项
        selected_item = self.build_pool_tree.selection()
        if selected_item:
            entry_id = selected_item[0]
            current_type = self.type_var.get()
            
            # 从构筑池子中移除
            if current_type in self.filter_data and entry_id in self.filter_data[current_type]:
                self.filter_data[current_type].remove(entry_id)
            
            # 保存当前选中项的索引
            items = self.build_pool_tree.get_children()
            current_index = -1
            if items:
                try:
                    current_index = items.index(entry_id)
                except ValueError:
                    pass
            
            # 更新池子
            self.update_pool()
            
            # 自动聚焦到下一项
            new_items = self.build_pool_tree.get_children()
            if new_items:
                # 计算新的聚焦索引
                new_index = current_index if current_index < len(new_items) else current_index - 1
                if new_index < 0:
                    new_index = 0
                # 聚焦到新的项
                self.build_pool_tree.selection_set(new_items[new_index])
                self.build_pool_tree.focus(new_items[new_index])
    
    def update_detail(self, event):
        # 清空详情
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        # 检查是哪个树被点击
        widget = event.widget
        selected_item = widget.selection()
        
        if selected_item:
            entry_id = selected_item[0]
            current_type = self.type_var.get()
            
            # 获取词条数据
            if current_type == "ban":
                entry_data = self.blacklist.get(entry_id, {})
            else:
                entry_data = self.entries.get(entry_id, {})
            
            # 构建详情文本
            detail_text = f"ID: {entry_id}\n"
            detail_text += f"词条名: {entry_data.get('name', '')}\n"
            detail_text += f"分类: {entry_data.get('type', '')}\n"
            detail_text += f"介绍: {entry_data.get('explanation', '')}\n"
            detail_text += f"备注: {entry_data.get('note', '')}\n"
            detail_text += f"叠加: {entry_data.get('superposability', '')}\n"
            
            # 显示详情
            self.detail_text.insert(tk.END, detail_text)
        
        self.detail_text.config(state=tk.DISABLED)
    
    def save(self):
        # 更新构筑名
        self.filter_data["name"] = self.name_var.get()
        
        # 保存到主应用
        self.main_app.filters[self.index] = self.filter_data
        self.main_app.save_filters()
        self.main_app.populate_tree()
        
        # 关闭窗口
        self.window.destroy()
    
    def on_close(self):
        # 检查是否有修改
        if self.filter_data != self.original_data or self.name_var.get() != self.original_data.get("name", ""):
            # 提示用户是否保存
            result = messagebox.askyesnocancel("保存", "是否保存修改？")
            if result is True:
                self.save()
            elif result is False:
                self.window.destroy()
            # 如果是取消，则不关闭窗口
        else:
            self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FilterEditor(root)
    root.mainloop()