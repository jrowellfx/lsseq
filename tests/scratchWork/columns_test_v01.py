import shutil
import sys
import os

if sys.stdout.isatty():
    ## You're running in a real terminal
    print("terminal")

    cols, rows = os.get_terminal_size()

    print("From os.get_terminal_size()")
    print("cols:", cols)
    print("rows:", rows)
else:
    ## You're being piped or redirected
    print("pipe or redirect")

    cols, rows = os.get_terminal_size() # should fail if stdout is 'less' for example

    print("From os.get_terminal_size()")
    print("cols:", cols)
    print("rows:", rows)
