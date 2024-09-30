import tkinter as tk
from tkinter import messagebox, ttk
import time
import csv

WINDOW_WIDTH = 400  # 定义窗口宽度
WINDOW_HEIGHT = 600
WINDOW_HEIGHT_MIN = 300


class TimeTrackerApp:
    def __init__(self, root):

        self.root = root
        self.root.title("项目时间追踪")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT_MIN}")  # 设置主窗口宽度和初始高度

        self.projects = ["Project_1"]
        self.init_projects()
        self.current_project = tk.StringVar(value=self.projects[0])
        self.is_running = False
        self.start_time = None
        self.records = []

        # 用于管理窗口的引用
        self.settings_window = None
        self.records_window = None
        self.settings_dialog = None

        # 项目选择器
        self.project_selector = tk.OptionMenu(root, self.current_project, *self.projects)
        self.project_selector.pack(pady=10)

        # 设置和记录按钮放在同一行
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.settings_button = tk.Button(button_frame, text="设置", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.records_button = tk.Button(button_frame, text="记录", command=self.show_records)
        self.records_button.pack(side=tk.LEFT, padx=5)

        # 置于最前的按钮
        self.topmost_button = tk.Button(button_frame, text="置顶", command=self.toggle_topmost)
        self.topmost_button.pack(side=tk.LEFT, padx=5)

        # 开始/暂停按钮
        self.start_pause_button = tk.Button(root, text="开始", command=self.toggle_timer)
        self.start_pause_button.pack(pady=10)

        # 秒表标签
        self.timer_label = tk.Label(root, text="00:00:00", font=("Helvetica", 20))
        self.timer_label.pack(pady=10)

        # 显示一个标签 为 备注
        self.notes_label = tk.Label(root, text="备注")
        self.notes_label.pack(pady=0)
        # 多行文本框
        self.notes_text = tk.Text(root, height=4, width=50)
        self.notes_text.pack(pady=0)

        # 确认退出时使用
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def init_projects(self):
        # 如果有projects.conf 文件，读取项目名称
        try:
            with open("projects.conf") as f:
                self.projects = f.read().splitlines()
        except FileNotFoundError:
            pass

    def confirm_exit(self):
        if messagebox.askokcancel("退出", "你确定要退出吗？请在\"记录\"中\"导出存档\""):
            self.root.destroy()

    def update_timer(self):
        if self.is_running:
            current_time = time.time()
            elapsed = current_time - self.start_time
            formatted_time = self.format_duration(elapsed)
            self.timer_label.config(text=formatted_time)
            self.timer_update_id = self.root.after(1000, self.update_timer)

    def format_duration(self, seconds):
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f"{int(hours):02}:{int(mins):02}:{int(secs):02}"

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()

            self.settings_window = tk.Toplevel(self.root)
            self.settings_window.title("设置项目名称")
            self.settings_window.geometry(f"{WINDOW_WIDTH}x300+{main_x+20}+{main_y+20}")  # 设置窗口宽度和初始高度

            self.tree = ttk.Treeview(self.settings_window, columns=("project"), show="headings")
            self.tree.heading("project", text="项目名称")
            self.tree.column("project", anchor="center", width=200)
            self.tree.pack(fill=tk.BOTH, expand=True)

            for i, project in enumerate(self.projects):
                self.tree.insert("", "end", iid=i, values=(project))

            self.tree.bind("<Double-1>", lambda event: self.edit_project_name(event))

            # 按钮框架
            button_frame = tk.Frame(self.settings_window)
            button_frame.pack(pady=5)

            add_button = tk.Button(button_frame, text="添加项目", command=self.add_project)
            add_button.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(button_frame, text="删除选中项目", command=self.delete_selected_project)
            delete_button.pack(side=tk.LEFT, padx=5)

            # save_button = tk.Button(button_frame, text="返回", command=lambda: self.save_projects(self.settings_window))
            # save_button.pack(side=tk.LEFT, padx=5)

            # 确认关闭时使用
            self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_window_close)

        else:
            self.settings_window.lift()  # 拉到最上面
            self.settings_window.focus_force()  # 使设置窗口成为活动窗口

    def on_settings_window_close(self):
        # if messagebox.askokcancel("关闭", "你确定要关闭设置窗口吗？"):.
        self.save_projects_setting()
        self.tree.destroy()
        self.settings_window.destroy()
        self.settings_window = None  # 重置窗口引用

    def edit_project_name(self, event):
        if self.settings_dialog is None or not self.settings_dialog.winfo_exists():
            selected_item = self.tree.selection()[0]
            current_value = self.tree.item(selected_item, "values")[0]
            main_x = self.settings_window.winfo_x()
            main_y = self.settings_window.winfo_y()
            self.settings_dialog = tk.Toplevel(self.settings_window)
            self.settings_dialog.title("编辑项目名称")
            self.settings_dialog.geometry(f"300x100+{main_x+20}+{main_y+20}")
            self.settings_dialog.resizable(False, False)

            # 创建输入框
            self.settings_name_entry = tk.Entry(self.settings_dialog)
            self.settings_name_entry.insert(0, current_value)
            self.settings_name_entry.pack(pady=10)

            # 创建保存按钮
            save_button = tk.Button(self.settings_dialog, text="保存", command=self.settings_save_name)
            save_button.pack(pady=10)

            self.settings_dialog.protocol("WM_DELETE_WINDOW", self.on_settings_dialog_close)

            # 必须先处理本窗口的关闭事件，才能处理其他窗口的其他事件
            self.settings_dialog.grab_set()

        else:
            self.settings_dialog.lift()
            self.settings_dialog.focus_force()

    def settings_save_name(self):
        new_value = self.settings_name_entry.get()
        self.tree.item(self.tree.selection()[0], values=(new_value))
        self.projects[self.tree.index(self.tree.selection()[0])] = new_value
        self.update_project_selector()
        self.settings_dialog.destroy()
        self.settings_dialog = None

    def on_settings_dialog_close(self):
        self.settings_dialog.destroy()
        self.settings_dialog = None

    def add_project(self):
        new_project_name = f"Project {len(self.projects) + 1}"
        # 替换空格为下划线
        new_project_name = new_project_name.replace(" ", "_")
        self.projects.append(new_project_name)
        self.tree.insert("", "end", values=(new_project_name))
        self.update_project_selector()

    def delete_selected_project(self):
        selected_items = self.tree.selection()
        if selected_items:
            for selected_item in selected_items:
                record_index = self.tree.index(selected_item)
                self.tree.delete(selected_item)
                del self.projects[record_index]
            self.update_project_selector()
        else:
            messagebox.showerror("错误", "请选择要删除的项目！")

    def save_projects_setting(self):
        with open("projects.conf", "w") as f:
            for project in self.projects:
                f.write(f"{project}\n")

    def update_project_selector(self):
        self.project_selector['menu'].delete(0, 'end')

        for project in self.projects:
            self.project_selector['menu'].add_command(label=project, command=tk._setit(self.current_project, project))

        # 如果没有项目，设置默认项目为Project 1
        if not self.projects or len(self.projects) == 0:
            self.projects = ["Project_1"]
            self.tree.insert("", "end", values=("Project_1"))

        self.current_project.set(self.projects[0])

    def toggle_topmost(self):
        is_topmost = self.root.winfo_toplevel().attributes("-topmost")
        self.root.winfo_toplevel().attributes("-topmost", not is_topmost)
        # 按钮变激活或非激活
        self.topmost_button.config(relief=tk.SUNKEN if not is_topmost else tk.RAISED)

    def toggle_timer(self):
        if not self.is_running:
            self.start_time = int(time.time())
            self.start_pause_button.config(text="暂停")
            self.start_pause_button.config(relief=tk.SUNKEN)
            self.settings_button.config(state=tk.DISABLED)
            self.project_selector.config(state=tk.DISABLED)
            # 重置notes
            self.notes_text.delete("1.0", "end")
        else:
            end_time = int(time.time())
            elapsed_time = end_time - self.start_time
            self.records.append({
                "project": self.current_project.get(),
                "start_time": time.strftime('%H:%M:%S', time.localtime(self.start_time)),
                "end_time": time.strftime('%H:%M:%S', time.localtime(end_time)),
                "duration": self.format_duration(elapsed_time),
                "notes": self.notes_text.get("1.0", "end-1c")
            })
            # 在记录窗口中显示记录
            if self.records_window:
                self.show_records()
            self.start_pause_button.config(text="开始")
            self.start_pause_button.config(relief=tk.RAISED)
            self.settings_button.config(state=tk.NORMAL)
            self.project_selector.config(state=tk.NORMAL)
        self.is_running = not self.is_running
        self.update_timer()

    def show_records(self):
        if not self.records_window:
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()

            self.records_window = tk.Toplevel(self.root)
            self.records_window.title("记录")
            self.records_window.geometry(f"{WINDOW_WIDTH*2}x{WINDOW_HEIGHT_MIN}+{main_x + 20}+{main_y + 20}")  # 设置窗口宽度和初始高度

            # 创建Treeview来显示记录
            tree = ttk.Treeview(self.records_window, columns=("项目", "开始时间", "结束时间", "持续时间", "备注"), show="headings")

            # 设置每一列的标题和宽度
            tree.heading("项目", text="项目")
            tree.column("项目", width=100)

            tree.heading("开始时间", text="开始时间")
            tree.column("开始时间", width=120)

            tree.heading("结束时间", text="结束时间")
            tree.column("结束时间", width=120)

            tree.heading("持续时间", text="持续时间")
            tree.column("持续时间", width=100)

            tree.heading("备注", text="备注")
            tree.column("备注", width=150)

            tree.pack(fill=tk.BOTH, expand=True)

            for record in self.records:
                record_text = record["notes"].replace("\n", " ")
                tree.insert("", "end",
                            values=(record["project"], record["start_time"], record["end_time"], record["duration"],
                                    (record_text[0:20] + "...") if len(record_text) >= 20 else record_text
                                    ))

            # 按钮框架
            button_frame = tk.Frame(self.records_window)
            button_frame.pack(pady=5)

            delete_button = tk.Button(button_frame, text="删除选中记录", command=lambda: self.delete_records(tree))
            delete_button.pack(side=tk.LEFT, padx=10)

            archive_button = tk.Button(button_frame, text="导出存档", command=self.export_records)
            archive_button.pack(side=tk.LEFT, padx=10)

            copy_button = tk.Button(button_frame, text="复制到剪贴板", command=lambda: self.copy_treeview_to_clipboard(tree))
            copy_button.pack(side=tk.LEFT, padx=10)

            # 确认关闭时使用
            self.records_window.protocol("WM_DELETE_WINDOW", self.on_records_window_close)

            # 拉到最上面
            self.records_window.lift()
            self.records_window.focus_force()
        else:
            self.records_window.lift()  # 拉到最上面
            # 更新Treeview的记录
            tree = self.records_window.winfo_children()[0]
            tree.delete(*tree.get_children())
            for record in self.records:
                tree.insert("", "end",
                            values=(record["project"], record["start_time"], record["end_time"], record["duration"], record["notes"]))
            self.records_window.focus_force()

    def on_records_window_close(self):
        self.records_window.destroy()
        self.records_window = None

    def export_records(self):
        if not self.records:
            messagebox.showwarning("警告", "没有记录可以存档！")
            return
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = f"records_{timestamp}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['project', 'start_time', 'end_time', 'duration', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records:
                writer.writerow(record)
        messagebox.showinfo("存档成功", f"记录已保存为 {filename}")

    def delete_records(self, tree):
        selected_item = tree.selection()
        if selected_item:
            if messagebox.askokcancel("删除", "确定要删除选中的记录吗？"):
                for item in selected_item:
                    self.records.pop(tree.index(item))
                    tree.delete(item)
        else:
            messagebox.showerror("错误", "请选择要删除的记录！")

    # 定义复制功能
    def copy_treeview_to_clipboard(self, tree):
        # 初始化一个空字符串用于存储数据
        clipboard_data = ""
        # 遍历 Treeview 中的所有行
        for child in tree.get_children():
            # 获取每一行的值
            row_values = tree.item(child)["values"]
            # 将行数据格式化为制表符分隔的字符串
            row_string = "\t".join(map(str, row_values))
            # 将每行数据加到结果字符串中，并以换行符分隔
            clipboard_data += row_string + "\n"
        # 清空剪贴板
        root.clipboard_clear()
        # 将数据添加到剪贴板
        root.clipboard_append(clipboard_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
