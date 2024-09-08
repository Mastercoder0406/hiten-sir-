import tkinter as tk
import csv
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

class ResumeScreeningWindow:
    def __init__(self, master):
        self.master = master
        master.title("Resume Screening")
        master.geometry("800x600")
        master.configure(bg="#f4f4f9")

        # Track current view: 'categories' or 'resumes'
        self.current_view = 'categories'

        # Create frames
        self.left_frame = tk.Frame(master, width=200, height=600, bg="#2d2d2d")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.center_frame = tk.Frame(master, width=600, height=600, bg="#ffffff")
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(master, width=800, height=50, bg="#2d2d2d")
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # Create widgets
        self.resume_listbox = tk.Listbox(self.left_frame, width=30, height=30, bg="#f0f0f0", font=("Arial", 12), bd=0, selectmode=tk.SINGLE)
        self.resume_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.resume_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        self.resume_label = tk.Label(self.center_frame, text="Resume Screening", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333")
        self.resume_label.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.target_resume_text = tk.Text(self.center_frame, width=60, height=25, wrap=tk.WORD, font=("Arial", 12), bg="#ffffff", bd=1, relief=tk.SUNKEN)
        self.target_resume_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.search_frame = tk.Frame(self.top_frame, bg="#2d2d2d")
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.search_entry = tk.Entry(self.search_frame, width=50, font=("Arial", 12), bd=0, relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, padx=10)

        self.search_button = tk.Button(self.search_frame, text="Search", font=("Arial", 12, "bold"), command=self.search_resumes, bg="#007bff", fg="#ffffff", bd=0, relief=tk.FLAT)
        self.search_button.pack(side=tk.LEFT, padx=10)

        self.pie_chart_frame = tk.Frame(self.center_frame, bg="#ffffff")
        self.pie_chart_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.back_button = tk.Button(self.top_frame, text="Back", font=("Arial", 12, "bold"), command=self.go_back, bg="#007bff", fg="#ffffff", bd=0, relief=tk.FLAT)
        self.back_button.pack(side=tk.RIGHT, padx=10)

        self.show_category_distribution()

        # Load resumes from CSV
        self.resume_dict = self.load_resumes_from_csv('resume_dataset.csv')
        self.update_category_listbox()

        # Set default text in search entry
        self.search_entry.insert(tk.END, "Search resumes...")

        # Bind Enter key to the search function
        self.master.bind('<Return>', self.search_resumes_event)

    def load_resumes_from_csv(self, file_path):
        resume_dict = {}
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header if there is one
                for row in reader:
                    if row:  # Check if the row is not empty
                        resume_name = row[0]
                        resume_text = '\n'.join(row[1:])
                        category = row[2] if len(row) > 2 else 'Uncategorized'
                        if category not in resume_dict:
                            resume_dict[category] = []
                        resume_dict[category].append((resume_name, resume_text))
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return resume_dict

    def update_category_listbox(self):
        self.current_view = 'categories'
        self.resume_listbox.delete(0, tk.END)
        for category in self.resume_dict:
            self.resume_listbox.insert(tk.END, category)

    def update_resume_listbox(self, selected_category):
        self.current_view = 'resumes'
        self.resume_listbox.delete(0, tk.END)
        for i, (resume_name, _) in enumerate(self.resume_dict.get(selected_category, []), start=1):
            self.resume_listbox.insert(tk.END, f"{i}. {resume_name}")

    def on_listbox_select(self, event):
        if self.current_view == 'categories':
            self.display_category_resumes(event)
        elif self.current_view == 'resumes':
            self.display_selected_resume(event)

    def display_category_resumes(self, event):
        selected_index = self.resume_listbox.curselection()
        if not selected_index:
            return
        selected_category = self.resume_listbox.get(selected_index[0])
        self.update_resume_listbox(selected_category)

    def search_resumes(self):
        # Get search keyword
        keyword = self.search_entry.get().lower()

        # Filter resumes based on keyword
        filtered_resumes = []
        for category, resumes in self.resume_dict.items():
            for resume_name, resume_text in resumes:
                if keyword in resume_name.lower() or keyword in resume_text.lower():
                    filtered_resumes.append((resume_name, resume_text, category))

        # Clear and update resume listbox
        self.current_view = 'resumes'
        self.resume_listbox.delete(0, tk.END)
        for resume_name, _, category in filtered_resumes:
            self.resume_listbox.insert(tk.END, f"{resume_name} ({category})")

        # Update the text area with the selected resume
        self.target_resume_text.delete(1.0, tk.END)
        if filtered_resumes:
            self.target_resume_text.insert(tk.END, filtered_resumes[0][1])

        # Update the pie chart
        self.update_category_distribution()

    def search_resumes_event(self, event):
        self.search_resumes()

    def show_category_distribution(self):
        # Create a new figure and axis
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Create the pie chart
        resumeDataSet = pd.read_csv('resume_dataset.csv')
        targetCounts = resumeDataSet['Category'].value_counts()
        targetLabels = resumeDataSet['Category'].unique()
        cmap = plt.get_cmap('coolwarm')
        colors = [cmap(i) for i in np.linspace(0, 1, len(targetLabels))]
        ax.pie(targetCounts, labels=targetLabels, autopct='%1.1f%%', shadow=True, colors=colors)
        ax.set_title('CATEGORY DISTRIBUTION')

        # Create a Tkinter canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, anchor=tk.CENTER)

    def update_category_distribution(self):
        # Clear the pie chart frame
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()

        # Show the new pie chart
        self.show_category_distribution()

    def display_selected_resume(self, event):
        selected_index = self.resume_listbox.curselection()
        if not selected_index:
            return
        
        selected_text = self.resume_listbox.get(selected_index[0])

        # Determine if the text includes category information
        if ' (' in selected_text:
            # Extract resume name and category
            selected_resume_name, selected_category = selected_text.rsplit(' (', 1)
            selected_category = selected_category.rstrip(')')  # Remove trailing ')'
        else:
            # No category information, assume it's just the resume name
            selected_resume_name = selected_text
            selected_category = None

        # Find and display the selected resume
        if selected_category:
            resumes = self.resume_dict.get(selected_category, [])
            for resume_name, resume_text in resumes:
                if resume_name == selected_resume_name:
                    self.target_resume_text.delete(1.0, tk.END)
                    self.target_resume_text.insert(tk.END, resume_text)
                    return
        else:
            # Handle case where there is no category (e.g., when searching)
            for category, resumes in self.resume_dict.items():
                for resume_name, resume_text in resumes:
                    if resume_name == selected_resume_name:
                        self.target_resume_text.delete(1.0, tk.END)
                        self.target_resume_text.insert(tk.END, resume_text)
                        return

    def go_back(self):
        # Reset the listbox to show categories
        self.update_category_listbox()

        # Clear the text area
        self.target_resume_text.delete(1.0, tk.END)
        self.target_resume_text.insert(tk.END, "Select a category to view resumes.")

root = tk.Tk()
my_window = ResumeScreeningWindow(root)
root.mainloop()

            # No category information
