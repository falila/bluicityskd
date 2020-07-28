
import click


CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower(),ignore_unknown_options=True)

@click.group(context_settings={'help_option_names': ['-h', '--help']},chain=True)
@click.version_option(version='0.1.0')
@click.pass_context
def blu_cli(ctx):
    ctx.ensure_object(dict)

@blu_cli.command(help="reports and services status managment command", context_settings=CONTEXT_SETTINGS)
@click.option('--r', is_flag=True, help='Print the report')
@click.pass_context
def sync(ctx, r):
    """sync notifications suntech cloud vs bluicity"""
    pass


if __name__ == '__main__':
    blu_cli(obj={})