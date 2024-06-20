import tkinter as tk
from tkinter import ttk
import winreg
import datetime


class RegistryKey:
    """Class to represent a registry key and retrieve its last modified timestamp."""
    registry_roots = {
        winreg.HKEY_CLASSES_ROOT: ["HKEY_CLASSES_ROOT", "HKCR"],
        winreg.HKEY_CURRENT_USER: ["HKEY_CURRENT_USER", "HKCU"],
        winreg.HKEY_LOCAL_MACHINE: ["HKEY_LOCAL_MACHINE", "HKLM"],
        winreg.HKEY_USERS: ["HKEY_USERS", "HKU"],
        winreg.HKEY_CURRENT_CONFIG: ["HKEY_CURRENT_CONFIG", "HKCC"],
    }

    def __init__(self, full_key_path):
        """Initialize with the full registry key path and clean it."""
        self.full_key_path = self.clean_registry_path(full_key_path)

    def clean_registry_path(self, full_key_path):
        """Clean up the registry path to match expected format."""
        parts = full_key_path.split("\\")
        for i, part in enumerate(parts):
            if part.startswith("HKEY_"):
                return "\\".join(parts[i:])
        return full_key_path

    def windows_ticks_to_unix_seconds(self, windows_ticks):
        """Convert Windows ticks to Unix timestamp."""
        return windows_ticks / 10000000 - 11644473600

    def format_registry_date(self, last_modified_date):
        """Format datetime object to a readable string."""
        return last_modified_date.strftime("%d/%m/%Y, %H:%M:%S")

    def check_last_modified(self):
        """Retrieve the last modified timestamp of the registry key."""
        try:
            for root_value, root_names in self.registry_roots.items():
                if any(self.full_key_path.startswith(root_name) for root_name in root_names):
                    key_path = self.full_key_path
                    for root_name in root_names:
                        key_path = key_path.replace(root_name, "", 1).lstrip("\\")
                    key_root = root_value
                    break
            else:
                raise ValueError(f"Unsupported registry key root: {self.full_key_path}")

            with winreg.OpenKey(key_root, key_path) as key:
                last_modified = winreg.QueryInfoKey(key)[2]
                last_modified_date = self.windows_ticks_to_unix_seconds(last_modified)
                formatted_date = self.format_registry_date(datetime.datetime.fromtimestamp(last_modified_date))
                return True, formatted_date

        except FileNotFoundError:
            raise RuntimeError("Registry key not found.")
        except PermissionError:
            raise RuntimeError("Permission denied to access registry key.")
        except OSError as e:
            raise RuntimeError(f"OS error occurred: {e}")
        except ValueError as e:
            raise RuntimeError(str(e))


class RegistryCheckerGUI:
    """GUI application to check and display last modified timestamps of registry keys."""

    def __init__(self, root):
        """Initialize the GUI with a given root window."""
        self.root = root
        self.root.title("Registry Key Timestamp Checker")

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Scrollbar for key_textbox
        key_scrollbar = tk.Scrollbar(self.root)
        key_scrollbar.grid(row=0, column=1, sticky="ns")

        # Textbox to paste registry keys
        self.key_textbox = tk.Text(self.root, height=10, width=60, bg='#FFFFFF', fg='#000000', padx=5, pady=5,
                                   yscrollcommand=key_scrollbar.set)
        self.key_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        key_scrollbar.config(command=self.key_textbox.yview)

        # Button to trigger checking
        check_button = tk.Button(self.root, text="Retrieve Timestamps", command=self.check_registry_keys, bg='#4CAF50',
                                 fg='white', activebackground='#45a049', padx=10, pady=5)
        check_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Scrollbar for result_tree
        result_scrollbar = ttk.Scrollbar(self.root)
        result_scrollbar.grid(row=2, column=1, sticky="ns")

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
        self.result_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        result_scrollbar.config(command=self.result_tree.yview)

        # Configure weight for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.result_tree.columnconfigure(0, weight=1)
        self.result_tree.rowconfigure(0, weight=1)

        # Bind right-click event to show context menu
        self.result_tree.bind("<Button-3>", self.show_context_menu)

        # Context menu for copying
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_rows)

    def check_registry_keys(self):
        """Retrieve and display last modified timestamps for the entered registry keys."""
        # Clear previous results
        self.result_tree.delete(*self.result_tree.get_children())

        # Get registry keys from textbox
        keys_text = self.key_textbox.get("1.0", tk.END).strip()
        registry_keys = keys_text.splitlines()

        # Check each registry key and populate the treeview
        for index, key_path in enumerate(registry_keys, start=1):
            registry_key = RegistryKey(key_path.strip())
            try:
                success, result = registry_key.check_last_modified()
                if success:
                    self.result_tree.insert("", "end", values=(index, key_path, result), tags=("success",))
                else:
                    self.result_tree.insert("", "end", values=(index, key_path, f"{result}"), tags=("error",))
            except RuntimeError as e:
                self.result_tree.insert("", "end", values=(index, key_path, f"{str(e)}"), tags=("error",))

        # Configure tag settings for colors
        self.result_tree.tag_configure("success", foreground="#43B581")  # Light green for success
        self.result_tree.tag_configure("error", foreground="#F04747")  # Light red for error

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


if __name__ == "__main__":
    root = tk.Tk()
    app = RegistryCheckerGUI(root)
    app.main()
