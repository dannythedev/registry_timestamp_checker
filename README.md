# Registry Key Timestamp Checker

This application allows you to check and display the last modified timestamps of Windows registry keys.

## Features
- **Input**: Paste or enter multiple registry key paths.
- **Output**: Displays the last modified timestamps for each key in a table.

Or, alternatively:

- **Checkbox Selection**: Fetch registry keys from selected root categories.
- **Calendar Selection**: Choose a range of dates to retrieve keys modified within that period.
- **Output**: Displays the modified registries and timestamps for each key in the selected checkbox categories and date range.


## Requirements
- Python 3.x
- tkinter (included in standard library)
- winreg (included in standard library)
- tkcalendar (as per ```python requirements.txt```)

## Usage
1. **Clone the repository** or download the `main.py` file.
2. **Run the application** using Python:
```python main.py```
3. **Paste**, manually enter or select specific checkboxes and date range of the registry keys into the text box.
4. Click on **Retrieve Timestamps** to fetch and display the last modified timestamps.
5. **Right-click** on any row in the results table to copy the selected rows to the clipboard.

## Example

Should they exist, then:
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer
HKEY_CLASSES_ROOT\.exe
```
Will give out:

| # | Key Path                                                         | Last Modified         |
|---|------------------------------------------------------------------|-----------------------|
| 1 | HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion     | 20/02/2024, 15:45:30  |
| 2 | HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer | 20/02/2024, 10:30:15  |
| 3 | HKEY_CLASSES_ROOT\.exe                                           | 20/02/2024, 12:20:00  |


## Notes
- Ensure you have the necessary permissions to access the registry keys.

## Author
- Created by dannythedev.
