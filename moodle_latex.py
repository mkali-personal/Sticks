import win32clipboard
win32clipboard.OpenClipboard()
latex = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
latex_url = r'<img src="http://latex.codecogs.com/gif.latex?' + latex + '" border="0"/>'
win32clipboard.EmptyClipboard()
win32clipboard.SetClipboardText(latex_url, win32clipboard.CF_TEXT)
win32clipboard.CloseClipboard()
