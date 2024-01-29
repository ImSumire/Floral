import click
from colorama import Fore, Style  # , Back


HEADER = Fore.GREEN + Style.BRIGHT


class CustomHelpGroup(click.Group):
    def format_help(self, ctx, formatter):
        click.echo(f"Welcome, here's the Floral compiler !\n")
        super().format_help(ctx, formatter)

    def format_options(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Writes all the options into the formatter if they exist."""
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            with formatter.section(f"{HEADER}Options"):
                formatter.write(Style.RESET_ALL)
                formatter.write_dl(opts)

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))

            if rows:
                with formatter.section(f"{HEADER}Commands"):
                    formatter.write(Style.RESET_ALL)
                    formatter.write_dl(rows)


@click.group(cls=CustomHelpGroup)
def cli():
    pass


@cli.command()
def clean():
    """Remove the binaries files"""
    click.echo(f"{Fore.BLACK}Not implemented yeet{Fore.RESET}")


@cli.command()
@click.argument("path", type=str, default="main.💐")
def compile(path: str):
    """Compile to binary"""
    click.echo(f"{Fore.MAGENTA}Compiling {Fore.RESET}{path}")


@cli.command()
def new():
    """Create a new project"""
    click.echo(f"{Fore.BLACK}Not implemented yeet{Fore.RESET}")


@cli.command()
@click.argument("path", type=str, default="main.💐")
def run(path: str):
    """Run the binary"""
    click.echo(f"{Fore.MAGENTA}Running {Fore.RESET}{path}")


@cli.command()
def bench():
    """Run as benchmark"""
    click.echo(f"{Fore.BLACK}Not implemented yeet{Fore.RESET}")


if __name__ == "__main__":
    cli()
