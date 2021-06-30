import json
import logging
import os
from copy import deepcopy
from typing import Dict

from service_buddy_too.codegenerator.cookie_cutter_creator import CookeCutterProjectCreator
from service_buddy_too.service.service import Service
from service_buddy_too.service.service_template_generator import ServiceTemplateGenerator


class CodeCreator(object):
    code_creators: Dict[str, CookeCutterProjectCreator]

    def __init__(self, code_template_directory):
        super(CodeCreator, self).__init__()
        default_path = os.path.join(code_template_directory, "code-template-config.json")
        infra_buddy_default_path = os.path.join(code_template_directory, "infra-buddy-defaults.json")
        if os.path.exists(infra_buddy_default_path):
            self.ib_defaults = infra_buddy_default_path
        else:
            self.ib_defaults = None
        if os.path.exists(default_path):
            with open(default_path) as fp:
                defaults = json.load(fp)
                self.default_provider = defaults.get('provider', None)
                self.remote_template_locations = defaults.get('service-template-definition-locations', None)
                self.extended_templates = defaults.get('code-template-definitions', {})
        else:
            logging.info("Could not locate 'code-template-config.json' in code template directory")
            self.default_provider = "cookiecutter"
            self.extended_templates = {}
        built_in = self._load_service_templates(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'builtin-code-templates.json'))
        built_in.update(self.extended_templates)
        self.templates = self._resolve_alias(built_in)
        self.service_template_generator = ServiceTemplateGenerator()
        self.code_creators = {
            CookeCutterProjectCreator.get_type(): CookeCutterProjectCreator(template_dir=code_template_directory,
                                                                            templates=self.templates)}
        if self.default_provider not in self.code_creators:
            raise Exception("Requested provider is not configured {}".format(self.default_provider))

    def _resolve_alias(self, templates):
        ret = {}
        for key, value in templates.items():
            if value['type'] == 'alias':
                ret[key] = deepcopy(templates[value['lookup']])
                value.pop('type')
                value.pop('lookup')
                ret[key].update(value)
            else:
                ret[key] = value
        return ret

    def _load_service_templates(self, builtIn: str) -> dict:
        with open(builtIn) as builtin:
            return json.load(builtin)

    def get_default_code_creator(self):
        return self.code_creators[self.default_provider]

    def create_project(self, service_definition: Service, destination_directory: str,
                       extra_config: dict = None) -> None:
        project = self.get_default_code_creator().create_project(service_definition=service_definition,
                                                                 destination_directory=destination_directory,
                                                                 extra_config=extra_config)
        service_type_ = self.templates[service_definition.get_service_type()]
        create_service_def = service_type_.get('generate-service-definition', True)
        if create_service_def:
            self.service_template_generator.create_project(service_definition,
                                                           service_type=service_type_.get('service-definition',
                                                                                          None),
                                                           defaults=service_type_.get('service-defaults',None),
                                                           ib_defaults=self.ib_defaults,
                                                           remote_template_locations=self.remote_template_locations)
        return project
