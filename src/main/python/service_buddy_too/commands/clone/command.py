import click

from service_buddy_too.commandline import cli


@cli.command(name='clone',short_help="Clone all of the existing service definition repos onto the local file system")
@click.pass_obj
def git_clone(service_ctx):
    service_ctx.vcs.validate_repositories(service_ctx.application_map)
    service_ctx.vcs.clone_service(service_ctx.application_map)
