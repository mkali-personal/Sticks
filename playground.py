import pygetwindow as gw
import pyautogui
import pywinauto
import time


def find_open_file_dialog():
    """Finds an active 'Open File' dialog window."""
    dialogs = [w for w in gw.getWindowsWithTitle("Open")]
    return dialogs[0] if dialogs else None


def paste_path(dialog, path):
    """Pastes a path into the dialog's filename field and presses Enter."""
    app = pywinauto.Application().connect(handle=dialog._hWnd)
    dialog_window = app.window(handle=dialog._hWnd)

    # Attempt to find the file name edit box
    try:
        edit_box = dialog_window.child_window(auto_id="1148", control_type="Edit")
        edit_box.click_input()
        edit_box.type_keys(path, with_spaces=True)
        pyautogui.press("enter")
    except Exception as e:
        print("Could not interact with the dialog directly:", e)
        # Fallback: Assume the last window was the dialog and type blindly
        pyautogui.write(path, interval=0.05)
        pyautogui.press("enter")


def main():
    path_to_paste = r"C:\Users\michaeka\Dropbox (Weizmann Institute)\Michael Kali’s files\Current Semester"
    dialog = find_open_file_dialog()

    if dialog:
        print(f"Found dialog: {dialog.title}")
        paste_path(dialog, path_to_paste)
    else:
        print("No active 'Open File' dialog found. Assuming it was last focused.")
        pyautogui.write(path_to_paste, interval=0.05)
        pyautogui.press("enter")


if __name__ == "__main__":
    time.sleep(2)  # Give user time to focus the dialog manually
    main()
