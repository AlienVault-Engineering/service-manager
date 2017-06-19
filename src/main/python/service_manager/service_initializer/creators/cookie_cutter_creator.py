import json
import os

import logging
from cookiecutter.main import cookiecutter


def _make_cookie_safe(service_definition):
    ret = {}
    for key,valey in service_definition.iteritems():
        ret[key.replace('-',"_")] = valey
    return ret


class CookeCutterProjectCreator(object):
    def __init__(self, template_file,dry_run):
        super(CookeCutterProjectCreator, self).__init__()
        self.dry_run = dry_run
        self.service_def = {}
        self._load_service_templates(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'builtin_service_templates.json'))
        if template_file:
            self.template_dir = os.path.dirname(os.path.abspath(template_file))
            self._load_service_templates(template_file)

    def _load_service_templates(self, builtIn):
        with open(builtIn) as builtin:
            self.service_def.update(json.load(builtin))

    def create_project(self, service_definition, service_dir):
        template = self.lookup_service_template(service_definition['service-type'])
        if template['type'] == 'file':
            location = os.path.abspath(os.path.join(self.template_dir,template['location']))
        else:
            location = template['location']
        if self.dry_run:
            logging.error("Creating project from template {} ".format(location))
        else:
            return cookiecutter(location,
                     no_input=True,
                     extra_context=_make_cookie_safe(service_definition),
                     output_dir=service_dir)

    def lookup_service_template(self, service_type):
        if service_type not in self.service_def:
            raise Exception("Unknown service type - {}".format(service_type))
        return self.service_def[service_type]