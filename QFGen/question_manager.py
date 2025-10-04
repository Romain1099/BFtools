import json
import customtkinter as ctk
from tkinter import messagebox, filedialog, Text
import random

class Question:
    def __init__(self, title, func_name, params, func_code, conditions):
        self.title = title
        self.func_name = func_name
        self.params = params
        self.func_code = func_code
        self.conditions = conditions

    def to_dict(self):
        return {
            "title": self.title,
            "func_name": self.func_name,
            "params": self.params,
            "func_code": self.func_code,
            "conditions": self.conditions
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("title", ""),
            data.get("func_name", ""),
            data.get("params", {}),
            data.get("func_code", ""),
            data.get("conditions", "")
        )

class QuestionManager:
    def __init__(self, json_file='question_manager_database.json'):
        self.json_file = json_file
        self.questions = self.load_questions()

    def load_questions(self):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                return [Question.from_dict(q) for q in data]
        except FileNotFoundError:
            return []

    def save_questions(self):
        with open(self.json_file, 'w') as f:
            json.dump([q.to_dict() for q in self.questions], f, indent=4)

    def add_question(self, question):
        self.questions.append(question)
        self.save_questions()

    def update_question(self, index, question):
        self.questions[index] = question
        self.save_questions()

class QuestionUI:
    def __init__(self, root, manager):
        self.manager = manager
        self.root = root
        self.root.title("Question Manager")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        self.title_entry = ctk.CTkEntry(self.frame)
        self.func_name_var = ctk.StringVar()

        ctk.CTkLabel(self.frame, text="Title:").grid(row=0, column=0, sticky="e")
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.frame, text="Function Name:").grid(row=1, column=0, sticky="e")
        self.func_name_combobox = ctk.CTkComboBox(self.frame, values=["addition", "multiplication", "celsius_to_fahrenheit"], variable=self.func_name_var)
        self.func_name_combobox.grid(row=1, column=1, padx=10, pady=5)

        self.params_frame = ctk.CTkFrame(self.frame)
        self.params_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        ctk.CTkLabel(self.params_frame, text="Params:").grid(row=0, column=0, sticky="w")
        self.params_vars = {}
        self.create_param_entries(self.params_frame, {}, 1, self.params_vars)

        self.conditions_frame = ctk.CTkFrame(self.frame)
        self.conditions_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        ctk.CTkLabel(self.conditions_frame, text="Conditions:").grid(row=0, column=0, sticky="w")
        self.conditions_vars = {}
        self.create_dict_entries(self.conditions_frame, {}, 1, self.conditions_vars)

        self.func_code_textbox = Text(self.frame, height=5, width=40)
        self.func_code_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.add_btn = ctk.CTkButton(self.frame, text="Add/Update Question", command=self.add_update_question)
        self.add_btn.grid(row=5, columnspan=2, pady=10)

        self.questions_listbox = ctk.CTkTextbox(self.frame, height=10)
        self.questions_listbox.grid(row=6, columnspan=2, sticky="ew", padx=10, pady=10)
        self.questions_listbox.bind('<ButtonRelease-1>', self.load_selected_question)

        self.refresh_questions_listbox()

    def refresh_questions_listbox(self):
        self.questions_listbox.delete("1.0", ctk.END)
        for q in self.manager.questions:
            self.questions_listbox.insert(ctk.END, q.title + "\n")

    def create_param_entries(self, parent_frame, params, start_row, vars_dict):
        """Recursively create entry widgets for parameter items."""
        row = start_row
        for key, value in params.items():
            frame = ctk.CTkFrame(parent_frame)
            frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            param_name=f"{key}:"
            ctk.CTkEntry(frame,textvariable=param_name, bg_color="blue", corner_radius=5).grid(row=0, column=0, sticky="w")
            

            if "default_value" in value:
                var = ctk.StringVar(value=str(value["default_value"]))
                entry = ctk.CTkEntry(frame, textvariable=var)
                entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
                vars_dict[key] = {"var": var, "entry": entry, "type": value["type"]}
            if "random_condition" in value:
                random_btn = ctk.CTkButton(frame, text="Randomize", command=lambda k=key: self.randomize_param(k))
                random_btn.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
            row += 1

    def create_dict_entries(self, parent_frame, dictionary, start_row, vars_dict):
        """Recursively create entry widgets for dictionary items."""
        row = start_row
        for key, value in dictionary.items():
            if isinstance(value, dict):
                frame = ctk.CTkFrame(parent_frame)
                frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                ctk.CTkLabel(frame, text=f"{key}:").grid(row=0, column=0, sticky="w")
                vars_dict[key] = {}
                self.create_dict_entries(frame, value, 1, vars_dict[key])
            else:
                ctk.CTkLabel(parent_frame, text=f"{key}:").grid(row=row, column=0, sticky="e")
                var = ctk.StringVar(value=str(value))
                ctk.CTkEntry(parent_frame, textvariable=var).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                vars_dict[key] = var
            row += 1

    def randomize_param(self, key):
        param = self.params_vars.get(key)
        if param and "entry" in param:
            type_ = param["type"]
            if type_ == "int":
                value = eval(param["entry"].get())
                param["var"].set(value)
            elif type_ == "str":
                # Example handling for string type
                param["var"].set(param["entry"].get())
            # Handle other types as needed

    def load_selected_question(self, event):
        selected_text = self.questions_listbox.get("1.0", ctk.END).strip().split('\n')
        index = self.questions_listbox.index("@%s,%s" % (event.x, event.y)).split('.')[0]
        if not selected_text or int(index) > len(selected_text) or int(index) <= 0:
            return
        selected_title = selected_text[int(index) - 1]

        for i, question in enumerate(self.manager.questions):
            if question.title == selected_title:
                self.title_entry.delete(0, ctk.END)
                self.title_entry.insert(0, question.title)
                self.func_name_var.set(question.func_name)
                self.params_vars.clear()
                self.conditions_vars.clear()
                for widget in self.params_frame.winfo_children():
                    widget.destroy()
                for widget in self.conditions_frame.winfo_children():
                    widget.destroy()
                self.create_param_entries(self.params_frame, question.params, 1, self.params_vars)
                self.create_dict_entries(self.conditions_frame, question.conditions, 1, self.conditions_vars)
                self.func_code_textbox.delete("1.0", ctk.END)
                self.func_code_textbox.insert("1.0", question.func_code)
                break

    def add_update_question(self):
        title = self.title_entry.get()
        func_name = self.func_name_var.get()
        params = self.extract_param_entries(self.params_vars)
        conditions = self.extract_dict_entries(self.conditions_vars)
        func_code = self.func_code_textbox.get("1.0", ctk.END).strip()

        question = Question(title, func_name, params, func_code, conditions)

        if self.questions_listbox.get("1.0", ctk.END).strip():
            selected_text = self.questions_listbox.get("1.0", ctk.END).strip().split('\n')
            if title in selected_text:
                index = selected_text.index(title)
                self.manager.update_question(index, question)
            else:
                self.manager.add_question(question)
        else:
            self.manager.add_question(question)

        self.refresh_questions_listbox()
        self.clear_entries()

    def extract_param_entries(self, vars_dict):
        """Recursively extract values from parameter entry widgets to form a dictionary."""
        result = {}
        for key, value in vars_dict.items():
            if "entry" in value:
                result[key] = {
                    "type": value["type"],
                    "default_value": value["var"].get()
                }
                if "random_condition" in value:
                    result[key]["random_condition"] = value["random_condition"]
        return result

    def extract_dict_entries(self, vars_dict):
        """Recursively extract values from entry widgets to form a dictionary."""
        result = {}
        for key, value in vars_dict.items():
            if isinstance(value, dict):
                result[key] = self.extract_dict_entries(value)
            else:
                result[key] = value.get()
        return result

    def clear_entries(self):
        self.title_entry.delete(0, ctk.END)
        self.func_name_var.set("")
        self.params_vars.clear()
        self.conditions_vars.clear()
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        for widget in self.conditions_frame.winfo_children():
            widget.destroy()
        self.func_code_textbox.delete("1.0", ctk.END)

if __name__ == "__main__":
    root = ctk.CTk()
    manager = QuestionManager()
    app = QuestionUI(root, manager)
    root.mainloop()
