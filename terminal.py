import tkinter as tk
import json


class Terminal:
    def __init__(self):
        with open('config/terminal.json', 'r', encoding='utf-8') as f:
            self.terminal_config = json.load(f)
        self.root = tk.Tk()
        self._setup_window()
        self._setup_widgets()
        self.lines = []

    def _setup_window(self):
        self.root.title('Terminal')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        bg_color = self.terminal_config['background']['color']
        alpha = self.terminal_config['background']['alpha']
        self.root.configure(bg=bg_color)
        self.root.attributes('-alpha', alpha)
        self.root.geometry(f"{self.terminal_config['width']}x{self.terminal_config['height']}+{self.root.winfo_screenwidth() - self.terminal_config['width'] - 10}+10")

    def _setup_widgets(self):
        font_config = ()
        if self.terminal_config['font']['name']:
            font_config = (self.terminal_config['font']['name'], self.terminal_config['font']['size'])
        elif self.terminal_config['font']['size']:
            font_config = (self.terminal_config['font']['size'],)
        
        self.text = tk.Text(self.root, bg=self.terminal_config['background']['color'], fg=self.terminal_config['font']['color'], font=font_config, padx=self.terminal_config['padding'], pady=self.terminal_config['padding'], highlightthickness=0, borderwidth=0)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.config(state=tk.DISABLED)
        self.log('终端启动成功')

    def log(self, message):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f'{message}\n')
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()
