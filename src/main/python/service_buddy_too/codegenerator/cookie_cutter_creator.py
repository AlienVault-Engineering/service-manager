import logging
import os

from cookiecutter.main import cookiecutter

from service_buddy_too.service.service import Service
from service_buddy_too.util import command_util


def _make_cookie_safe(service_definition):
    ret = {}
    for key, valey in service_definition.items():
        ret[key.replace('-', "_")] = valey
    return ret


class CookeCutterProjectCreator(object):
    def __init__(self, template_dir, templates):
        super(CookeCutterProjectCreator, self).__init__()
        self.template_dir = template_dir
        self.templates =templates

    def create_project(self, service_definition:Service,destination_directory:str, extra_config=None):
        template = self._lookup_service_template(service_definition.get_service_type())
        if template['type'] == 'file':
            location = os.path.abspath(os.path.join(self.template_dir, template['location']))
        else:
            location = template['location']
        extra_context = _make_cookie_safe(service_definition)
        if extra_config:
            extra_context.update(_make_cookie_safe(extra_config))
        # allow for extra content to be specified in template
        extra_context.update(_make_cookie_safe(template))
        # allow user to specify the directory in the github repo
        directory= template.get('directory', None)
        if command_util.dry_run_global:
            logging.error("Creating project from template {} ".format(location))
        else:
            return cookiecutter(location,
                                no_input=True,
                                extra_context=extra_context,
                                output_dir=destination_directory,
                                directory=directory)

    def _lookup_service_template(self, service_type):
        if service_type not in self.templates:
            raise Exception("Unknown code template - {}".format(service_type))
        return self.templates[service_type]

    @classmethod
    def get_type(cls):
        return "cookiecutter"

