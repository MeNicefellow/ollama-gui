import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import pystray
from PIL import Image
import sys

# Only import Windows-specific modules if on Windows
if sys.platform.startswith('win'):
    import win32gui
    import win32con

class OllamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Model Manager")
        
        # Add window state tracking
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # Create system tray icon
        self.create_tray_icon()
        
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
        
        self.running_tree = ttk.Treeview(running_frame, columns=('Name', 'Size', 'Processor'), show='headings')
        self.running_tree.heading('Name', text='Name')
        self.running_tree.heading('Size', text='Size')
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
                    name = parts[0]
                    size = parts[2] + ' ' + parts[3]
                    models.append((name, size))
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
                    name = parts[0]
                    size = parts[2] + ' ' + parts[3]
                    processor = parts[4] + ' ' + parts[5]
                    models.append((name, size, processor))
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

    # Add new methods for tray icon functionality
    def create_tray_icon(self):
        # Create a white background image
        icon_size = 64
        icon_image = Image.new('RGB', (icon_size, icon_size), color='white')
        
        # Create a circular 'O'
        from PIL import ImageDraw
        draw = ImageDraw.Draw(icon_image)
        padding = 4
        draw.ellipse([padding, padding, icon_size-padding, icon_size-padding], 
                     outline='black', width=3, fill=None)
        
        menu = (
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.quit_application)
        )
        self.icon = pystray.Icon("Ollama Manager", icon_image, "Ollama Manager", menu)
        
        def setup(icon):
            icon.visible = True
            icon.on_click = self.show_window  # This will handle left clicks
            
        self.icon.run_detached(setup=setup)

    def show_window(self, icon=None, item=None):
        self.icon.stop()
        self.root.after(0, self._show_window)
        self.create_tray_icon()

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def quit_application(self, icon=None, item=None):
        self.icon.stop()
        self.root.quit()

if __name__ == "__main__":
    # Hide console window only on Windows
    if sys.platform.startswith('win'):
        console_window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(console_window, win32con.SW_HIDE)
    
    root = tk.Tk()
    app = OllamaGUI(root)
    root.mainloop()
