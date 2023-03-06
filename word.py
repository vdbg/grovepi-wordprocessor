
#!/usr/bin/python3

from datetime import datetime
# See https://github.com/DexterInd/GrovePi/blob/master/Software/Python/grove_rgb_lcd/grove_rgb_lcd.py
from grove_rgb_lcd import *
from pathlib import Path
import logging
import os
import platform
import sys
import termios
import time
# see comments in requirements.txt
import tomli as tomllib
import tty

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


def get_config():
    CONFIG_FILE = "config.toml"
    try:
        with open(Path(__file__).with_name(CONFIG_FILE), "rb") as config_file:
            config = tomllib.load(config_file)

            if not config:
                raise ValueError(f"Invalid {CONFIG_FILE}. See template.{CONFIG_FILE}.")

            for name in {"lcd", "files", "main"}:
                if name not in config:
                    raise ValueError(f"Invalid {CONFIG_FILE}: missing section {name}.")

            return config
    except FileNotFoundError as e:
        logging.error(f"Missing {e.filename}.")
        exit(2)


class Processor:
    def __init__(self, config: dict) -> None:
        self.hello_line: str = config["lcd"]["hello_line"]
        self.line_len: int = config["lcd"]["line_len"]
        self.delay_msg_seconds: int = config["lcd"]["delay_msg_seconds"]
        self.save_dir: str = config["files"]["save_dir"]
        self.stdin_fd = sys.stdin.fileno()
        self.old_tty_settings = termios.tcgetattr(self.stdin_fd)

    def set_text_with_refresh(self, msg: str) -> None:
        logging.debug(f"Sending text with refresh: {msg}")
        setText(msg)

    def set_text_no_refresh(self, msg: str) -> None:
        logging.debug(f"Sending text without refresh: {msg}")
        setText_norefresh(msg)

    def set_default_color(self) -> None:
        setRGB(0, 128, 64)

    def set_error_color(self) -> None:
        setRGB(255, 0, 0)  # RED

    def message_and_pause(self, message: str) -> None:
        self.set_text_with_refresh(message)
        time.sleep(self.delay_msg_seconds)
        self.set_default_color()

    def printException(self, prefix: str, e: Exception) -> None:
        logging.exception(str, e)
        self.set_error_color()
        self.message_and_pause(f"{prefix}\n{str(e)}")

    def saveToFile(self, line: str) -> None:
        try:
            filename = datetime.today().strftime('%Y-%m-%d')
            file_path = os.path.join(self.save_dir, filename+".txt")
            file = open(file_path, "a")  # append mode
            file.write(line)
            file.write("\n")
            file.close()
        except Exception as e:
            self.printException("SAVE FAILED", e)

    def main(self) -> None:
        try:
            # this sets tty in raw mode, allowing for directly handling keyboard input w/o buffering
            tty.setcbreak(sys.stdin.fileno())

            previous_line: str = self.hello_line
            current_line: str = ""

            self.set_default_color()
            self.set_text_with_refresh(previous_line)

            while True:
                c = ord(sys.stdin.read(1))
                c = chr(c)
                if c == '\n':
                    previous_line = current_line[:self.line_len]  # only print the first Line-len chars
                    self.saveToFile(current_line)
                    current_line = ""
                    self.set_text_with_refresh(previous_line)
                    continue
                current_line = current_line + c
                display_line: str = current_line  # we may not be able to display the entire current line
                if len(display_line) > self.line_len:
                    display_line = display_line[-self.line_len:]  # grad the last line_len chars (make it scroll right)
                    self.set_text_with_refresh(previous_line + "\n" + display_line)
                else:
                    self.set_text_no_refresh(previous_line + "\n" + display_line)

        except KeyboardInterrupt:
            print("Exiting due to Ctrl-C ...")
        except Exception as e:
            self.printException("ERROR", e)
            logging.exception(e)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_tty_settings)
            setRGB(0, 255, 0)
            self.message_and_pause("DONE!!")
            setRGB(0, 0, 0)


SUPPORTED_PYTHON_MAJOR = 3
SUPPORTED_PYTHON_MINOR = 7

if sys.version_info < (SUPPORTED_PYTHON_MAJOR, SUPPORTED_PYTHON_MINOR):
    raise Exception(f"Python version {SUPPORTED_PYTHON_MAJOR}.{SUPPORTED_PYTHON_MINOR} or later required. Current version: {platform.python_version()}.")


try:
    config = get_config()

    logging.getLogger().setLevel(logging.getLevelName(config["main"]["log_verbosity"]))
    logging.info("Writing typed text to LCD screen ...")

    processor = Processor(config)
    processor.main()

except Exception as e:
    logging.exception(e)
