import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json

class OllamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Model Manager")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create two frames for available and running models
        available_frame = ttk.LabelFrame(main_frame, text="Available Models", padding="5")
        available_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        running_frame = ttk.LabelFrame(main_frame, text="Running Models", padding="5")
        running_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeviews (now at row 0)
        self.available_tree = ttk.Treeview(available_frame, columns=('Name', 'Size'), show='headings')
        self.available_tree.heading('Name', text='Name')
        self.available_tree.heading('Size', text='Size')
        self.available_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.running_tree = ttk.Treeview(running_frame, columns=('Name', 'Processor'), show='headings')
        self.running_tree.heading('Name', text='Name')
        self.running_tree.heading('Processor', text='Processor')
        self.running_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbars (at row 0)
        available_scroll = ttk.Scrollbar(available_frame, orient=tk.VERTICAL, command=self.available_tree.yview)
        available_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.available_tree.configure(yscrollcommand=available_scroll.set)
        
        running_scroll = ttk.Scrollbar(running_frame, orient=tk.VERTICAL, command=self.running_tree.yview)
        running_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.running_tree.configure(yscrollcommand=running_scroll.set)
        
        # Add instruction labels below treeviews
        ttk.Label(available_frame, text="Double-click to start a model").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(running_frame, text="Double-click to stop a model").grid(row=1, column=0, sticky=tk.W)
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh", command=self.refresh_lists)
        refresh_btn.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Initial refresh
        self.refresh_lists()
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        available_frame.columnconfigure(0, weight=1)
        running_frame.columnconfigure(0, weight=1)

        # Bind double-click events
        self.available_tree.bind("<Double-1>", self.run_model)
        self.running_tree.bind("<Double-1>", self.stop_model)

    def get_available_models(self):
        try:
            result = subprocess.run(['ollama', 'ls'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    models.append((parts[0], parts[3] + ' ' + parts[4]))
            return models
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get available models: {str(e)}")
            return []

    def get_running_models(self):
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    models.append((parts[0], parts[3] + ' ' + parts[4]))
            return models
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get running models: {str(e)}")
            return []

    def refresh_lists(self):
        # Clear existing items
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        for item in self.running_tree.get_children():
            self.running_tree.delete(item)
        
        # Populate available models
        for model in self.get_available_models():
            self.available_tree.insert('', tk.END, values=model)
        
        # Populate running models
        for model in self.get_running_models():
            self.running_tree.insert('', tk.END, values=model)

    def run_model(self, event):
        item = self.available_tree.selection()[0]
        model_name = self.available_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm", f"Do you want to run model {model_name}?"):
            try:
                subprocess.Popen(['ollama', 'run', model_name])
                messagebox.showinfo("Success", f"Model {model_name} is starting")
                self.root.after(2000, self.refresh_lists)  # Refresh after 2 seconds
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run model: {str(e)}")

    def stop_model(self, event):
        item = self.running_tree.selection()[0]
        model_name = self.running_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm", f"Do you want to stop model {model_name}?"):
            try:
                subprocess.run(['ollama', 'stop', model_name])
                messagebox.showinfo("Success", f"Model {model_name} stopped")
                self.refresh_lists()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop model: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaGUI(root)
    root.mainloop()
