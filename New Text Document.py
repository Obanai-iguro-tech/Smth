import tkinter as tk
from tkinter import messagebox


class QuickApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickApp")
        self.root.geometry("580x540")
        self.root.configure(bg="#f3f6fb")
        self.root.resizable(False, False)

        self.items = []
        self.colors = {
            "navy": "#17324d",
            "blue": "#2878d0",
            "red": "#d9534f",
            "gray": "#64748b",
            "light": "#f3f6fb",
            "white": "#ffffff",
        }
        self.make_ui()

    def make_ui(self):
        header = tk.Frame(self.root, bg=self.colors["navy"], height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="QuickApp", bg=self.colors["navy"],
            fg="white", font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=28, pady=(18, 2))
        tk.Label(
            header, text="A simple place to manage your records",
            bg=self.colors["navy"], fg="#c8d8e8", font=("Arial", 10)
        ).pack(anchor="w", padx=30)

        body = tk.Frame(self.root, bg=self.colors["light"])
        body.pack(fill="both", expand=True, padx=24, pady=18)

        form = tk.Frame(body, bg=self.colors["white"], padx=18, pady=14)
        form.pack(fill="x")
        tk.Label(
            form, text="ADD A RECORD", bg="white", fg=self.colors["navy"],
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        tk.Label(form, text="Name", bg="white", fg=self.colors["gray"]
        ).grid(row=1, column=0, sticky="w")
        self.name_box = tk.Entry(form, width=38, relief="solid", bd=1)
        self.name_box.grid(row=1, column=1, padx=8, pady=5, ipady=5)

        tk.Label(form, text="Details", bg="white", fg=self.colors["gray"]
        ).grid(row=2, column=0, sticky="w")
        self.detail_box = tk.Entry(form, width=38, relief="solid", bd=1)
        self.detail_box.grid(row=2, column=1, padx=8, pady=5, ipady=5)

        buttons = tk.Frame(body, bg=self.colors["light"])
        buttons.pack(fill="x", pady=12)

        self.make_button(buttons, "Add record", self.add_item,
                         self.colors["blue"]).pack(side="left", padx=(0, 7))
        self.make_button(buttons, "Delete selected", self.delete_item,
                         self.colors["red"]).pack(side="left", padx=7)
        self.make_button(buttons, "Clear", self.clear_form,
                         self.colors["gray"]).pack(side="left", padx=7)

        list_card = tk.Frame(body, bg=self.colors["white"], padx=14, pady=12)
        list_card.pack(fill="both", expand=True)
        tk.Label(
            list_card, text="YOUR RECORDS", bg="white",
            fg=self.colors["navy"], font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.list_box = tk.Listbox(
            list_card, height=10, font=("Arial", 11),
            bg="#fbfdff", fg=self.colors["navy"],
            selectbackground=self.colors["blue"], relief="solid", bd=1,
            highlightthickness=0, activestyle="none"
        )
        self.list_box.pack(fill="both", expand=True)

        self.status = tk.Label(
            body, text="0 items", bg=self.colors["light"],
            fg=self.colors["gray"], font=("Arial", 9)
        )
        self.status.pack(anchor="e", pady=(7, 0))

    def make_button(self, parent, label, action, color):
        return tk.Button(
            parent, text=label, command=action, bg=color, fg="white",
            activebackground=color, activeforeground="white",
            relief="flat", padx=12, pady=7, cursor="hand2",
            font=("Arial", 9, "bold")
        )

    def add_item(self):
        name = self.name_box.get().strip()
        detail = self.detail_box.get().strip()

        if not name:
            messagebox.showwarning("Missing name", "Enter a name first.")
            return

        item = {"name": name, "detail": detail}
        self.process_item(item)
        self.items.append(item)
        self.refresh_list()
        self.clear_form()

    def process_item(self, item):
        #item["detail"] = item["detail"].upper()
        pass

    def delete_item(self):
        choice = self.list_box.curselection()
        if not choice:
            messagebox.showinfo("Select an item", "Choose an item to delete.")
            return

        self.items.pop(choice[0])
        self.refresh_list()

    def refresh_list(self):
        self.list_box.delete(0, tk.END)
        for item in self.items:
            line = item["name"]
            if item["detail"]:
                line += " - " + item["detail"]
            self.list_box.insert(tk.END, line)

        count = len(self.items)
        self.status.config(text=f"{count} items")

    def clear_form(self):
        self.name_box.delete(0, tk.END)
        self.detail_box.delete(0, tk.END)
        self.name_box.focus()


root = tk.Tk()
app = QuickApp(root)
root.mainloop()
