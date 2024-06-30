from tkinter import ttk
import tkinter as tk
import winreg
import datetime

from RegistryKey import RegistryKey


class RegistryCheckerGUI:
    """GUI application to check and display last modified timestamps of registry keys."""

    def __init__(self, root):
        """Initialize the GUI with a given root window."""
        self.root = root
        self.root.title("Registry Key Timestamp Checker")
        self.selected_roots = set()  # Set to store selected registry roots
        self.checkbox_vars = {}

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Label above the Textbox
        textbox_label = tk.Label(self.root, text="Check for specific registry keys with path:")
        textbox_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Scrollbar for key_textbox
        key_scrollbar = tk.Scrollbar(self.root)
        key_scrollbar.grid(row=1, column=1, sticky="ns")

        # Textbox to paste registry keys
        self.key_textbox = tk.Text(self.root, height=10, width=60, bg='#FFFFFF', fg='#000000', padx=5, pady=5,
                                   yscrollcommand=key_scrollbar.set)
        self.key_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        key_scrollbar.config(command=self.key_textbox.yview)

        # Label above the Checkboxes
        checkboxes_label = tk.Label(self.root, text="Or fetch registries that were modified recently:")
        checkboxes_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Frame for checkboxes
        checkbox_frame = ttk.Frame(self.root)
        checkbox_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Create checkboxes for each registry root
        for i, (root, names) in enumerate(RegistryKey.registry_roots.items()):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(checkbox_frame, text=names[0], variable=var, command=self.on_checkbox_toggle)
            checkbox.grid(row=i // 2, column=i % 2, padx=5, pady=0, sticky="w")
            self.checkbox_vars[root] = var

        # Button to trigger checking
        check_button = tk.Button(self.root, text="Retrieve Timestamps", command=self.check_registry_keys, bg='#4CAF50',
                                 fg='white', activebackground='#45a049', padx=10, pady=5)
        check_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Scrollbar for result_tree
        result_scrollbar = ttk.Scrollbar(self.root)
        result_scrollbar.grid(row=5, column=1, sticky="ns")

        # Treeview to display results in a table
        self.result_tree = ttk.Treeview(self.root, columns=("Index", "Key Path", "Last Modified"), show="headings",
                                        selectmode="extended", yscrollcommand=result_scrollbar.set)
        self.result_tree.heading("Index", text="#", anchor=tk.CENTER)
        self.result_tree.heading("Key Path", text="Key Path", anchor=tk.CENTER)
        self.result_tree.heading("Last Modified", text="Last Modified", anchor=tk.CENTER)

        # Adjust column widths
        self.result_tree.column("Index", width=10, anchor=tk.W)
        self.result_tree.column("Key Path", width=400, anchor=tk.W)
        self.result_tree.column("Last Modified", width=200, anchor=tk.W)

        # Grid setup for result treeview
        self.result_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        result_scrollbar.config(command=self.result_tree.yview)

        # Configure weight for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)
        self.result_tree.columnconfigure(0, weight=1)
        self.result_tree.rowconfigure(0, weight=1)

        # Bind right-click event to show context menu
        self.result_tree.bind("<Button-3>", self.show_context_menu)

        # Context menu for copying
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_rows)

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

        # Check each registry key and populate the treeview
        one_week_ago = datetime.datetime.now() - datetime.timedelta(weeks=1)
        for index, key_path in enumerate(registry_keys, start=1):
            registry_key = RegistryKey(key_path.strip())
            try:
                success, result = registry_key.check_last_modified()
                last_modified_date = datetime.datetime.strptime(result, "%d/%m/%Y, %H:%M:%S")
                if success and last_modified_date >= one_week_ago:
                    self.result_tree.insert("", "end", values=(index, key_path, result), tags=("success",))
                elif success:
                    continue  # Skip keys modified before one week
                else:
                    self.result_tree.insert("", "end", values=(index, key_path, f"{result}"), tags=("error",))
            except RuntimeError as e:
                self.result_tree.insert("", "end", values=(index, key_path, f"{str(e)}"), tags=("error",))

        # Configure tag settings for colors
        self.result_tree.tag_configure("success", foreground="#43B581")  # Light green for success
        self.result_tree.tag_configure("error", foreground="#F04747")  # Light red for error

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