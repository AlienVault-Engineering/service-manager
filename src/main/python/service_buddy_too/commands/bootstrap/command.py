import click
from click import Choice

from service_buddy_too.ci import ci
from service_buddy_too.codegenerator.code_creator import CodeCreator
from service_buddy_too.commandline import cli
from service_buddy_too.service.application import Application
from service_buddy_too.service.service import Service
from service_buddy_too.vcs import vcs


@cli.command(name='bootstrap', short_help="Create a repository containing the initial definition for a micro-service "
                                          "stack managed by service-buddy.")
@click.option("--application", envvar='APPLICATION', required=True,
              help='Application name for new micro-service stack.  Brevity suggested.')
@click.pass_obj
def bootstrap(service_ctx, application):
    cc = CodeCreator("")
    directory = service_ctx.destination_directory
    if directory == "./code":  # override default for this usecase
        directory = "./"
    service_def = Service(app=application, role="master", definition={},
                          app_reference=Application("master", code_directory=directory))
    service_def.set_service_type("service-buddy-master")

    config = {}
    vcs_provider = click.prompt('Please select your source code repository', type=Choice(vcs.vcs_providers))
    config['vcs-provider'] = vcs_provider
    vcs_options = vcs.options
    for key, value in vcs_options.items():
        config['vcs_{}'.format(key)] = click.prompt("VCS: {} ({})".format(value, key))
    ci_provider = click.prompt('Please select your build system - ', type=Choice(ci.build_systems))
    config['build-system-provider'] = ci_provider
    ci_options = ci.build_system_map[ci_provider].options()
    for key, value in ci_options.items():
        config['build-system-{}'.format(key)] = click.prompt("Build System: {} ({})".format(value, key))
    cc.create_project(service_definition=service_def, destination_directory=directory, extra_config=config)
