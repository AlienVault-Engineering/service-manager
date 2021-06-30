import click

from service_buddy_too.commandline import cli
from service_buddy_too.util.pretty_printer import pretty_print_services


@cli.command(name='list', short_help="Print definitions for services.")
@click.option('--validate-repository', envvar='VALIDATE',  is_flag=True,
              help='Validate existence of repository in VCS.')
@click.pass_obj
def git_exec(service_ctx, validate_repository):
    application_map = service_ctx.application_map
    if validate_repository:
        service_ctx.vcs.validate_repositories(application_map)
    pretty_print_services(application_map)