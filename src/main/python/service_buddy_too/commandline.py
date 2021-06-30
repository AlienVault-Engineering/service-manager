import click

from service_buddy_too.context.service_context import ServiceContext
from service_buddy_too.util import command_util
from service_buddy_too.util.log_handler import configure_logging


@click.group()
@click.option("--application-filter", envvar='FILTER', help='Constrain command to operate on applications'
                                                            ' that match the passed filter')
@click.option("--service-filter", envvar='SERVICE_FILTER',default=".*", help='Constrain command to operate on services'
                                                            ' that match the passed filter')
@click.option("--service-directory", envvar='SERVICE_DIRECTORY', type=click.Path(),
              default="./services",
              help='Directory containing service definitions in <app>/service.json format.  Default is \'./services\'')
@click.option('--destination-directory',
              envvar='DESTINATION',
              type=click.Path(),
              default="./code",
              help='The directory where the repositories for each service should be created or currently exist.')
@click.option("--verbose", is_flag=True, help='Print verbose status messages')
@click.option("--dry-run", is_flag=True, help='Preview effect of action')
@click.pass_context
def cli(ctx, application_filter, service_filter, service_directory, destination_directory, verbose, dry_run):
    """
    CLI for managing the repositories and build pipeline in a micro-service architecture..
    """
    configure_logging(verbose)
    command_util.dry_run_global = dry_run
    ctx.obj = ServiceContext(
        filter_string=application_filter,
        service_filter_string=service_filter,
        service_directory=service_directory,
        destination_directory=destination_directory
    )


# noinspection PyUnresolvedReferences
from service_buddy_too.commands.clone import command
# noinspection PyUnresolvedReferences
from service_buddy_too.commands.git import command
# noinspection PyUnresolvedReferences
from service_buddy_too.commands.initialize import command
# noinspection PyUnresolvedReferences
from service_buddy_too.commands.list import command
# noinspection PyUnresolvedReferences
from service_buddy_too.commands.bootstrap import command

