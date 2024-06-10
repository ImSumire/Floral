from typing import Callable, Mapping, Tuple
from colorama import Back, Fore, Style
import inspect
import sys
import re


MAGENTA = "\033[35m"
YELLOW = "\033[33m"
ITALIC = "\033[3m"
RESET = "\033[97m"
GRAY = "\033[90m"
DIM = "\033[2m"

regex = re.compile(r"\x1b\[[;\d]*[A-Za-z]")


class Cli:
    def __init__(self):
        self.opts: Mapping[str, Callable] = {'help': self.help}
        self.cmds: Mapping[str, Callable] = {}
        self.alts: Mapping[str, Callable] = {}

    def cmd(self, alts=None):
        def wrapper(fn):
            self.cmds[fn.__name__] = fn
            if alts:
                for alt in alts:
                    self.alts[alt] = fn.__name__

        return wrapper
    
    def opt(self, alts=None):
        def wrapper(fn):
            self.opts[fn.__name__] = fn
            if alts:
                for alt in alts:
                    self.alts[alt] = fn.__name__
        
        return wrapper
    
    @staticmethod
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

    def help(self):
        print(f"""
                ███████╗██╗      ██████╗ ██████╗  █████╗ ██╗     
                ██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗██║     
                █████╗  ██║     ██║   ██║██████╔╝███████║██║     
                ██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║██║     
                ██║     ███████╗╚██████╔╝██║  ██║██║  ██║███████╗
                ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

                              {Back.MAGENTA} floral ⬢ v1.0.0 {Style.RESET_ALL}

        """)
        print(self.frame("Usage", [f"{MAGENTA}floral {RESET}[OPTIONS] [COMMAND]"]))

        options = []
        for opt in self.opts.values():
            opts = '--' + opt.__name__
            for alt, base in self.alts.items():
                if base == opt.__name__:
                    opts += ', --' + alt
            options.append(f"{MAGENTA}{opts}  {RESET}{opt.__doc__}")
        print(self.frame("Options", options))

        commands = []
        for cmd in self.cmds.values():
            cmds = cmd.__name__
            for alt, base in self.alts.items():
                if base == cmd.__name__:
                    cmds += ', ' + alt
            commands.append(f"{MAGENTA}{cmds}  {RESET}{cmd.__doc__}")
        print(self.frame("Commands", commands))

    def __call__(self):
        argv = sys.argv
        if len(argv) == 1:
            self.help()
            return

        _, *cmd = argv

        if len(cmd) == 1:
            fn = cmd[0]
            
            if fn in ["-h", "--help", "--?"]:
                self.help()
                return

            try:
                self.cmds[fn]()
            except KeyError:
                print("Command not found")
        else:
            fn, *args = cmd
            try:
                self.cmds[fn](*args)
            except KeyError:
                print("Command not found")


cli = Cli()


@cli.cmd(alts=('r'))
def run(path: str = "main"):
    """Run the binary"""
    print("Running " + path)

@cli.cmd(alts=('c'))
def compile(path: str = "main.💐"):
    """Compile to binary"""
    print("Compiling " + path)

@cli.cmd(alts=('b'))
def bench(path: str = "main"):
    """Run as benchmark"""
    print("Benchmarking " + path)

@cli.opt(alts=('h', '?'))
def help():
    """Print help"""
    return cli.help


# -V --version
# --explain <CODE>
# --config
# --h --help --?


cli()

# parser = argparse.ArgumentParser()
# parser.add_argument("command", help="Lorem ipsum")
# args = parser.parse_args()
# print(args.command)
