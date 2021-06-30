import logging

from service_buddy_too.ci.ci import BuildCreatorManager
from service_buddy_too.codegenerator.code_creator import CodeCreator
from service_buddy_too.service.loader import safe_mkdir, walk_service_map
from service_buddy_too.service.service import Service
from service_buddy_too.util.pretty_printer import pretty_print_service


class Initializer(object):
    def __init__(self, vcs, destination_directory, code_template_directory,
                 skip_code_creation=False,
                 skip_build_creation=False,
                 skip_git_creation=False,
                 force_build_creation=False,
                 ):
        super(Initializer, self).__init__()
        self.skip_code_creation = skip_code_creation
        self.force_build_creation = force_build_creation
        self.skip_build_creation = skip_build_creation
        self.skip_git_creation = skip_git_creation
        self.code_generator = CodeCreator(code_template_directory=code_template_directory)
        self.build_creator = BuildCreatorManager(template_directory=code_template_directory)
        safe_mkdir(directory=destination_directory)
        self.destination_directory = destination_directory
        self.vcs = vcs

    def init_app(self, app):
        pass

    def init_service(self, definition: Service):
        app_destination_dir = definition.get_parent_dir()
        if not definition.repo_exists():
            logging.info("Creating Service - %r", definition.get_fully_qualified_service_name())
            if self.skip_code_creation:
                logging.info("Skipping code creation")
            else:
                logging.info("Running code creation")
                self.code_generator.create_project(definition, app_destination_dir)

            if self.skip_git_creation:
                logging.info("Skipping git creation")
            else:
                logging.info("Running git creation")
                self.vcs.create_project(definition, app_destination_dir)
        else:
            logging.info("Service exists - {}".format(definition.get_fully_qualified_service_name()))

        if self.skip_build_creation:
            logging.info("Skipping build creation")
        else:
            logging.info("Running build creation")
            self.build_creator.create_project(definition,  force_build_creation=self.force_build_creation)

        pretty_print_service(definition)
        logging.info("Done creating Service - %r", definition.get_fully_qualified_service_name())

    def initialize_services(self, application_map):
        walk_service_map(application_map=application_map, application_callback=self.init_app,
                         service_callback=self.init_service)
