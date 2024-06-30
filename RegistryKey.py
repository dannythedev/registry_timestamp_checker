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

    @classmethod
    def list_subkeys(cls, root, key):
        """List all subkeys of a given registry key."""
        subkeys = []
        try:
            with winreg.OpenKey(root, key) as open_key:
                i = 0
                while True:
                    subkey = winreg.EnumKey(open_key, i)
                    subkeys.append(f"{cls.registry_roots[root][0]}\\{key}\\{subkey}")
                    i += 1
        except OSError:
            pass
        return subkeys