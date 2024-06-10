import os
import re
from colorama import Back, Fore, Style


MAGENTA = "\033[35m"
YELLOW = "\033[33m"
ITALIC = "\033[3m"
RESET = "\033[97m"
GRAY = "\033[90m"
DIM = "\033[2m"

regex = re.compile(r"\x1b\[[;\d]*[A-Za-z]")
width, _ = os.get_terminal_size()

def frame(title, content, w=None):
    lenghtes = list(map(lambda x: len(regex.sub("", x)), content))
    if w is None:
        w = max(lenghtes)

    # Header (title)
    result = f"{GRAY}┌─ {title} {GRAY}{'─' * (w - len(title) - 1)}┐\n"
    # Content
    for i, p in enumerate(content):
        l = w - lenghtes[i]
        result += f"│ {RESET}{p} {GRAY}{' ' * l}│\n"
    # Footer
    result += f"└{'─' * (w + 2)}┘{RESET}"

    return result

print(f"""
                ███████╗██╗      ██████╗ ██████╗  █████╗ ██╗     
                ██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗██║     
                █████╗  ██║     ██║   ██║██████╔╝███████║██║     
                ██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║██║     
                ██║     ███████╗╚██████╔╝██║  ██║██║  ██║███████╗
                ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

                              {Back.MAGENTA} floral ⬢ v1.0.0 {Style.RESET_ALL}

""")
print(frame("Usage", [f"{MAGENTA}floral {RESET}[OPTIONS] [COMMAND]"]))
print(frame("Options", [
    f"{MAGENTA}-V, --version       {RESET}Print version info and exit",
    f"{MAGENTA}    --explain       {RESET}Provide a detailed explanation of a floral error message",
    f"{MAGENTA}-h, --help          {RESET}Print help",
]))
print(frame("Commands", [
    f"{MAGENTA}new                 {RESET}Create a new project",
    f"{MAGENTA}clean               {RESET}Remove the binaries files",
    f"{MAGENTA}run, r              {RESET}Run the binary",
    f"{MAGENTA}bench, b            {RESET}Run as benchmark",
]))
print(f"{ITALIC + GRAY}See `floral help <command>` for more information on a specific command{RESET}")
