# RegistryCheckerGUI.py

from tkinter import ttk
import tkinter as tk
import winreg
import datetime
from tkcalendar import DateEntry
from RegistryKey import RegistryKey

BG_COLOR = "#D9E3F1"

class RegistryCheckerGUI:
    """GUI application to check and display last modified timestamps of registry keys."""

    def __init__(self, root):
        """Initialize the GUI with a given root window."""
        self.root = root
        self.root.title("Registry Key Timestamp Checker")
        self.selected_roots = set()  # Set to store selected registry roots
        self.checkbox_vars = {}
        self.start_date = None
        self.end_date = None
        self.create_style()
        self.create_widgets()

    def create_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Normal state configuration
        style.configure("Treeview.Heading", background="#5B62F4", foreground="white", relief=tk.FLAT)

        # Hover state configuration (change hover background color to black)
        style.map("Treeview.Heading",
                  background=[("active", "#4F55C9")],
                  foreground=[("active", "white")])

        style.configure('Flat.Treeview', relief=tk.FLAT, background="#F0F5FA", foreground="#8599C8")
        # Define scrollbar style
        style.configure("Custom.Vertical.TScrollbar",
                        background="#8599C8",
                        troughcolor=BG_COLOR,
                        gripcount=0,
                        bordercolor=BG_COLOR,
                        darkcolor=BG_COLOR,
                        lightcolor=BG_COLOR)


        # Set root background color
        self.root.configure(bg=BG_COLOR)

    def create_widgets(self):
        """Create all GUI widgets."""
        # Label above the Textbox
        textbox_label = tk.Label(self.root, text="Check for specific registry keys with path:", bg=BG_COLOR)
        textbox_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Scrollbar for key_textbox
        key_scrollbar = tk.Scrollbar(self.root)
        key_scrollbar.grid(row=1, column=1, sticky="ns")

        # Textbox to paste registry keys
        self.key_textbox = tk.Text(self.root, height=3, width=60, bg='#FFFFFF', fg='#000000', padx=5, pady=5,
                                   yscrollcommand=key_scrollbar.set)
        self.key_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        key_scrollbar.config(command=self.key_textbox.yview)

        # Label above the Checkboxes
        checkboxes_label = tk.Label(self.root, text="Or fetch registries that were modified recently:", bg=BG_COLOR)
        checkboxes_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Frame for checkboxes
        checkbox_frame = tk.Frame(self.root, bg=BG_COLOR)
        checkbox_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Create checkboxes for each registry root
        for i, (root, names) in enumerate(RegistryKey.registry_roots.items()):
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(checkbox_frame, text=names[0], variable=var, command=self.on_checkbox_toggle,
                                       bg=BG_COLOR, fg="#8599C8", selectcolor=BG_COLOR,
                                       activebackground=BG_COLOR, activeforeground="#7878BE",
                                       font=("Segoe UI", 10))
            checkbox.grid(row=i // 3, column=i % 3, padx=5, pady=0, sticky="w")
            self.checkbox_vars[root] = var

        # Calendar / Date button for selecting date range
        date_label = tk.Label(self.root, text="Select date range:", bg=BG_COLOR)
        date_label.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        today = datetime.date.today()

        # Frame for date entries
        date_frame = tk.Frame(self.root, bg=BG_COLOR)
        date_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=0, sticky="w")

        # Start date entry
        self.start_date_entry = DateEntry(date_frame, width=12, background='#4CAF50',
                                          foreground='white', borderwidth=2, maxdate=today)
        self.start_date_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry.bind("<<DateEntrySelected>>", self.update_end_date_min)

        # End date entry
        self.end_date_entry = DateEntry(date_frame, width=12, background='#4CAF50',
                                        foreground='white', borderwidth=2, maxdate=today)
        self.end_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Button to trigger checking
        check_button = tk.Button(self.root, text="Retrieve Timestamps", command=self.check_registry_keys,
                                    bg="#43CC29", fg="white", relief=tk.FLAT, height=2)
        check_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Scrollbar for result_tree
        self.result_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.result_scrollbar.grid(row=8, column=1, sticky="ns")
        self.result_scrollbar.grid_forget()

        # Treeview to display results in a table
        self.result_tree = ttk.Treeview(self.root, columns=("Index", "Key Path", "Last Modified"), show="headings",
                                        selectmode="extended", yscrollcommand=self.result_scrollbar.set)
        self.result_tree.heading("Index", text="#", anchor=tk.CENTER)
        self.result_tree.heading("Key Path", text="Key Path", anchor=tk.CENTER)
        self.result_tree.heading("Last Modified", text="Last Modified", anchor=tk.CENTER)

        # Adjust column widths
        self.result_tree.column("Index", width=10, anchor=tk.W)
        self.result_tree.column("Key Path", width=400, anchor=tk.W)
        self.result_tree.column("Last Modified", width=200, anchor=tk.W)

        # Grid setup for result treeview
        self.result_tree.grid(row=8, column=0, padx=10, pady=10, sticky="nsew")

        # Configure scrollbar command
        self.result_scrollbar.config(command=self.result_tree.yview)

        # Configure weight for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)  # Or set a weight if you want the scrollbar to also resize
        self.root.rowconfigure(8, weight=1)  # Ensure row 8 expands with resizing

        self.result_tree.columnconfigure(0, weight=1)  # Adjust column weights if needed
        self.result_tree.rowconfigure(0, weight=1)  # Adjust row weights if needed

        # Bind right-click event to show context menu
        self.result_tree.bind("<Button-3>", self.show_context_menu)

        self.result_tree.grid_forget()  # Hide the treeview initially

        # Context menu for copying
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_rows)


    def update_end_date_min(self, event):
        """Update the minimum date for the end date entry based on the selected start date."""
        start_date = self.start_date_entry.get_date()
        self.end_date_entry.config(mindate=start_date)

        # If the current end date is before the new start date, update the end date
        if self.end_date_entry.get_date() < start_date:
            self.end_date_entry.set_date(start_date)

    def check_registry_keys(self):
        """Retrieve and display last modified timestamps for the entered registry keys."""
        # Clear previous results
        self.result_tree.delete(*self.result_tree.get_children())

        # Retrieve keys based on selected roots or from textbox
        if self.selected_roots:
            registry_keys = []
            for root in self.selected_roots:
                registry_keys.extend(self.get_keys_in_root(root))
        else:
            keys_text = self.key_textbox.get("1.0", tk.END).strip()
            registry_keys = keys_text.splitlines()

        # Get selected date range
        self.start_date = self.start_date_entry.get_date()
        self.end_date = self.end_date_entry.get_date() if self.end_date_entry.get_date() else datetime.date.today()

        # Show result_tree
        self.result_tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.result_scrollbar.grid(row=8, column=1, sticky="ns")

        # Check each registry key and populate the treeview
        for index, key_path in enumerate(registry_keys, start=1):
            registry_key = RegistryKey(key_path.strip())
            try:
                success, result = registry_key.check_last_modified()
                last_modified_date = datetime.datetime.strptime(result, "%d/%m/%Y, %H:%M:%S")
                if success and self.start_date <= last_modified_date.date() <= self.end_date:
                    self.result_tree.insert("", "end", values=(index, key_path, result), tags=("success",))
                elif success:
                    continue  # Skip keys not in date range
                else:
                    self.result_tree.insert("", "end", values=(index, key_path, f"{result}"), tags=("error",))
            except RuntimeError as e:
                self.result_tree.insert("", "end", values=(index, key_path, f"{str(e)}"), tags=("error",))

        # Configure tag settings for colors
        self.result_tree.tag_configure("success", foreground="#43B581")  # Light green for success
        self.result_tree.tag_configure("error", foreground="#F04747")  # Light red for error

    def on_checkbox_toggle(self):
        """Handle checkbox state changes to ensure mutual exclusivity with text input."""
        # Update selected roots based on checkbox state
        self.selected_roots = {root for root, var in self.checkbox_vars.items() if var.get()}

        # Disable textbox if any checkbox is checked
        if self.selected_roots:
            self.key_textbox.delete("1.0", tk.END)
            self.key_textbox.config(state=tk.DISABLED)
        else:
            self.key_textbox.config(state=tk.NORMAL)

    def get_keys_in_root(self, root):
        """Retrieve all keys in a given registry root."""
        keys = []
        try:
            with winreg.OpenKey(root, "") as base_key:
                num_subkeys = winreg.QueryInfoKey(base_key)[0]
                for i in range(num_subkeys):
                    subkey_name = winreg.EnumKey(base_key, i)
                    full_path = f"{RegistryKey.registry_roots[root][0]}\\{subkey_name}"
                    keys.append(full_path)
        except OSError:
            pass
        return keys

    def show_context_menu(self, event):
        """Display context menu when right-clicking on a row in the result tree."""
        # Select the item under the mouse pointer if not already selected
        item = self.result_tree.identify_row(event.y)
        if item:
            # Check if the item is already selected, if not, select it
            if item not in self.result_tree.selection():
                self.result_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_rows(self):
        """Copy selected rows' data (index, key path, last modified) to clipboard."""
        selected_items = self.result_tree.selection()
        if selected_items:
            values_to_copy = []

            # Calculate maximum widths for index, path, and date columns
            max_widths = {
                "Index": len(str(len(selected_items))),
                "Key Path": max(len(self.result_tree.item(item, "values")[1]) for item in selected_items),
                "Last Modified": max(len(self.result_tree.item(item, "values")[2]) for item in selected_items)
            }

            # Prepare data to be copied to clipboard
            copy_content = []
            for item in selected_items:
                values = self.result_tree.item(item, "values")
                if values:
                    values_str = "\t".join(f"{str(values[i]).ljust(max_widths[col])}" for i, col in
                                           enumerate(("Index", "Key Path", "Last Modified")))
                    copy_content.append(values_str)

            # Join all lines with newline characters
            copy_text = "\n".join(copy_content)

            # Clear the clipboard contents and append the new content
            self.root.clipboard_clear()
            self.root.clipboard_append(copy_text)

    def main(self):
        """Main function to initialize the GUI application."""
        self.root.mainloop()