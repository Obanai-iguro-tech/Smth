import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]
class FocusPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusWeek | Weekly planner")
        self.root.geometry("1120x760")
        self.root.minsize(900, 650)

        self.tasks = []
        self.remaining = 25 * 60
        self.timer_running = False
        self.timer_job = None
        self.day_columns = {}
        self.day_stats = {}
        self.balance_task = None
        self.balance_target = None
        self.build_ui()
        self.refresh_week()
        self.update_score()

    def build_ui(self):
        self.root.option_add("*Font", "Arial 10")

        tk.Label(self.root, text="FocusWeek").pack(pady=(12, 2))
        tk.Label(self.root, text="Plan your week and track your progress").pack()
        tk.Label(self.root, text="Your week at a glance").pack(pady=(12, 4))

        coach = tk.Frame(self.root, bd=1, relief="groove", padx=8, pady=6)
        coach.pack(fill="x", padx=12, pady=6)
        tk.Label(coach, text="Balance coach:").pack(side="left")
        self.balance_label = tk.Label(
            coach, text="Add tasks to get a balance suggestion.", anchor="w"
        )
        self.balance_label.pack(side="left", fill="x", expand=True, padx=8)
        self.balance_button = tk.Button(
            coach, text="Move suggested task", command=self.apply_balance
        )
        self.balance_button.pack(side="right")

        area = tk.Frame(self.root)
        area.pack(fill="both", expand=True, padx=12, pady=6)
        self.canvas = tk.Canvas(area, highlightthickness=0)
        scroll = ttk.Scrollbar(
            area, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.week_frame = tk.Frame(self.canvas)
        self.week_window = self.canvas.create_window(
            (0, 0), window=self.week_frame, anchor="nw"
        )
        self.week_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_week)

        footer = tk.Frame(self.root, bd=1, relief="groove", padx=10, pady=8)
        footer.pack(fill="x", padx=12, pady=(4, 12))
        score = tk.Frame(footer)
        score.pack(side="left", fill="x", expand=True)
        summary = tk.Frame(score)
        summary.pack(fill="x")
        self.total_label = tk.Label(summary, text="0 planned")
        self.total_label.pack(side="left")
        self.done_label = tk.Label(summary, text="0 done")
        self.done_label.pack(side="left", padx=12)
        self.score_label = tk.Label(summary, text="0%")
        self.score_label.pack(side="right")
        self.progress = ttk.Progressbar(score, maximum=100)
        self.progress.pack(fill="x", pady=5)

        focus = tk.Frame(footer)
        focus.pack(side="left", padx=(16, 0))
        tk.Label(focus, text="Focus timer · 25 min").pack()
        timer_row = tk.Frame(focus)
        timer_row.pack(fill="x")
        self.clock_label = tk.Label(timer_row, text="25:00")
        self.clock_label.pack(side="left")
        tk.Button(timer_row, text="Start / Pause", command=self.toggle_timer,
                  ).pack(side="right", padx=4)
        tk.Button(timer_row, text="Reset", command=self.reset_timer,
                  ).pack(side="right")

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_week(self, event):
        self.canvas.itemconfigure(self.week_window, width=event.width)

    def refresh_week(self):
        for widget in self.week_frame.winfo_children():
            widget.destroy()
        self.day_columns = {}
        self.day_stats = {}

        for day in DAYS:
            is_today = day == datetime.now().strftime("%A")
            column = tk.Frame(
                self.week_frame, width=150, padx=6, pady=6,
                bd=2 if is_today else 1, relief="groove"
            )
            column.pack(side="left", fill="y", expand=True, padx=3)
            tk.Label(column, text=day).pack()
            if is_today:
                tk.Label(column, text="TODAY").pack()
            tk.Button(
                column, text="+ Add task", command=lambda d=day: self.add_task(d)
            ).pack(fill="x", pady=5)
            rows = tk.Frame(column)
            rows.pack(fill="both", expand=True)
            self.day_columns[day] = rows
            stats = tk.Frame(column)
            stats.pack(fill="x", pady=5)
            label = tk.Label(stats, text="0 / 0 done")
            label.pack(anchor="w")
            bar = ttk.Progressbar(stats, maximum=100)
            bar.pack(fill="x")
            self.day_stats[day] = (label, bar)
            self.draw_day(day)

    def draw_day(self, day):
        rows = self.day_columns[day]
        for widget in rows.winfo_children():
            widget.destroy()

        day_tasks = [task for task in self.tasks if task["day"] == day]
        if not day_tasks:
            tk.Label(rows, text="Nothing planned yet").pack(pady=12)

        for task in day_tasks:
            cell = tk.Frame(rows, bd=1, relief="ridge", padx=3, pady=3)
            cell.pack(fill="x", pady=2)
            done = tk.BooleanVar(value=task["done"])
            check = tk.Checkbutton(
                cell, text="", variable=done,
                command=lambda t=task, v=done:
                self.set_done(t, v)
            )
            check.pack(side="left")

            text = tk.StringVar(value=task["text"])
            entry = tk.Entry(cell, textvariable=text, width=11)
            entry.pack(side="left", fill="x", expand=True, ipady=4)
            text.trace_add("write", lambda *args, t=task, v=text:
                           self.edit_task(t, v))
            entry.bind("<Return>", lambda event: event.widget.tk_focusNext().focus())

            tk.Button(cell, text="x",
                      command=lambda t=task: self.delete_task(t)
                      ).pack(side="right")

    def add_task(self, day):
        task = {"day": day, "text": "", "done": False}
        self.tasks.append(task)
        self.draw_day(day)
        self.update_score()
        entries = self.day_columns[day].winfo_children()[-1].winfo_children()
        entries[1].focus_set()

    def edit_task(self, task, text_var):
        task["text"] = text_var.get()
        self.update_score()

    def set_done(self, task, variable):
        task["done"] = variable.get()
        self.draw_day(task["day"])
        self.update_score()

    def delete_task(self, task):
        day = task["day"]
        self.tasks.remove(task)
        self.draw_day(day)
        self.update_score()

    def update_score(self):
        written = [task for task in self.tasks if task["text"].strip()]
        total = len(written)
        done = sum(task["done"] for task in written)
        percent = round(done / total * 100) if total else 0
        self.total_label.config(text=f"{total} PLANNED")
        self.done_label.config(text=f"{done} DONE")
        self.score_label.config(text=f"{percent}%")
        self.progress["value"] = percent
        for day in DAYS:
            day_tasks = [task for task in written if task["day"] == day]
            day_total = len(day_tasks)
            day_done = sum(task["done"] for task in day_tasks)
            day_percent = round(day_done / day_total * 100) if day_total else 0
            label, bar = self.day_stats[day]
            label.config(text=f"{day_done} / {day_total} done")
            bar["value"] = day_percent
        self.update_balance()

    def update_balance(self):
        counts = {
            day: sum(task["day"] == day and bool(task["text"].strip())
                     for task in self.tasks)
            for day in DAYS
        }
        busiest = max(DAYS, key=counts.get)
        lightest = min(DAYS, key=counts.get)
        self.balance_task = None
        self.balance_target = None

        if sum(counts.values()) == 0:
            tip = "Add tasks to get a balance suggestion."
        elif counts[busiest] - counts[lightest] <= 1:
            tip = "Your tasks are spread pretty evenly across the week."
        else:
            candidates = [
                task for task in self.tasks
                if task["day"] == busiest and task["text"].strip()
                and not task["done"]
            ]
            if candidates:
                self.balance_task = candidates[-1]
                self.balance_target = lightest
                name = self.balance_task["text"].strip()
                tip = (f"{busiest} is busiest. Move '{name[:18]}' to "
                       f"{lightest} to spread things out?")
            else:
                tip = f"{busiest} is busiest, but its tasks are already done."

        self.balance_label.config(text=tip)
        state = "normal" if self.balance_task else "disabled"
        self.balance_button.config(state=state)

    def apply_balance(self):
        if not self.balance_task:
            return
        old_day = self.balance_task["day"]
        self.balance_task["day"] = self.balance_target
        self.draw_day(old_day)
        self.draw_day(self.balance_target)
        self.update_score()

    def toggle_timer(self):
        self.timer_running = not self.timer_running
        if self.timer_running:
            self.tick()
        elif self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def tick(self):
        minutes, seconds = divmod(self.remaining, 60)
        self.clock_label.config(text=f"{minutes:02}:{seconds:02}")
        if self.remaining == 0:
            self.timer_running = False
            self.timer_job = None
            messagebox.showinfo("Focus session", "Nice work! Session complete.")
            return
        self.remaining -= 1
        self.timer_job = self.root.after(1000, self.tick)

    def reset_timer(self):
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.remaining = 25 * 60
        self.clock_label.config(text="25:00")


root = tk.Tk()
app = FocusPlanner(root)
root.mainloop()
