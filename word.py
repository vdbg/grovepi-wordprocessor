
import sys
import tty
import termios
from grove_rgb_lcd import *
from datetime import datetime
import time
import os

# TODO: move these to config
hello_line = "Ctrl-C=Exit"
line_len = 16
save_dir = "/mnt/share/files"
delay_msg_seconds = 4


def set_default_color() -> None:
    setRGB(0, 128, 64)


def message_and_pause(message: str) -> None:
    setText(message)
    time.sleep(delay_msg_seconds)
    set_default_color()


def printException(prefix: str, e: Exception) -> None:
    setRGB(255, 0, 0)  # RED
    message_and_pause(f"{prefix}\n{str(e)}")


def saveToFile(line: str) -> None:
    try:
        filename = datetime.today().strftime('%Y-%m-%d')
        file_path = os.path.join(save_dir, filename+".txt")
        file = open(file_path, "a")  # append mode
        file.write(line)
        file.write("\n")
        file.close()
    except Exception as e:
        printException("SAVE FAILED", e)


set_default_color()
print(hello_line)
print("Writing typed text to LCD screen ...")

previous_line = hello_line
setText(previous_line)

fd = sys.stdin.fileno()
old_tty_settings = termios.tcgetattr(fd)

last_line = ""
try:
    tty.setcbreak(sys.stdin.fileno())

    while True:
        c = ord(sys.stdin.read(1))
        c = chr(c)
        # sys.stdout.write(c)
        if c == '\n':
            previous_line = last_line[:line_len]  # only print the first Line-len chars
            saveToFile(last_line)
            last_line = ""
            setText(previous_line)
            continue
        last_line = last_line + c
        display_line = last_line
        if len(display_line) > line_len:
            display_line = display_line[-line_len:]  # grad the last line_len chars (make it scroll right)
        setText(previous_line + "\n" + display_line)

except KeyboardInterrupt:
    print("Exiting due to Ctrl-C ...")
except Exception as e:
    printException("ERROR", e)

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty_settings)
    setRGB(0, 255, 0)
    message_and_pause("DONE!!")
