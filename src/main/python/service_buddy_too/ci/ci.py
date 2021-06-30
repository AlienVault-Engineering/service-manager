import json
import logging
import os
from typing import Dict, Any

from service_buddy_too.ci.bamboo_build_creator import BambooBuildCreator
from service_buddy_too.ci.bitbucket_pipeline_build_creator import BitBucketPipelineBuildCreator
from service_buddy_too.ci.travis_build_creator import TravisBuildCreator
from service_buddy_too.service.service import Service
from jsonschema import validate

build_system_map: Dict[str, Any] = {
    BambooBuildCreator.get_type(): BambooBuildCreator(),
    BitBucketPipelineBuildCreator.get_type(): BitBucketPipelineBuildCreator(),
    TravisBuildCreator.get_type(): TravisBuildCreator()}
build_systems = [key for key in build_system_map.keys()]


class BuildCreatorManager(object):
    schema = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "enum": ["travis",
                                                "bamboo",
                                                "bitbucket"]},
            "pypi_user": {"type": "string"},
            "build-creation-is-idempotent": {"type": "boolean"},
            "bamboo-url": {"type": "string"},
            "use-travis-open-source": {"type": "boolean"},
            "build-templates": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"}
                    },
                    "required": ["type"]
                },
            },
            "build-configuration": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "language": {"type": "string"},
                        "install": {"type": "string"},
                        "script": {"type": "string"},
                        "pypi-deploy": {"type": "boolean"},
                        "location": {"type": "string"}
                    }
                },
            }
        },
        "required": ["provider"]

    }

    def __init__(self, template_directory):
        super(BuildCreatorManager, self).__init__()
        default_path = os.path.join(template_directory, "build-config.json")
        if os.path.exists(default_path):
            with open(default_path) as fp:
                defaults = json.load(fp)
                validate(defaults, schema=self.schema)
                self.default_provider = defaults.get('provider', None)
                self.build_templates = defaults.get('build-templates', {})
                self.user = defaults.get('user', os.environ.get('BUILD_SYSTEM_USER'))
                self.password = defaults.get('password', os.environ.get('BUILD_SYSTEM_PASSWORD'))
                self.always_recreate_builds = defaults.get('build-creation-is-idempotent', True)
                self.default_config = defaults
        else:
            logging.warning("Could not local 'build-config.json' in code template directory")
            self.default_provider = "bamboo"
        if self.default_provider not in build_system_map:
            raise Exception("Requested provider is not configured {}".format(self.default_provider))
        else:
            creator = self._get_default_build_creator()
            creator.init(
                default_config=self.default_config,
                build_templates=self.build_templates,
                template_directory=template_directory,
                user=self.user, password=self.password
            )

    def _get_default_build_creator(self):
        return build_system_map[self.default_provider]

    def create_project(self, service_definition: Service, force_build_creation: bool = False):
        do_create = not service_definition.repo_exists() or self.always_recreate_builds or force_build_creation
        logging.info(
            '[create project] repo exists: %r, always_recreate: %r, force create: %r do_create: %r',
            service_definition.repo_exists(), self.always_recreate_builds, force_build_creation, do_create
        )
        if do_create:
            return self._get_default_build_creator().create_project(
                service_definition=service_definition
            )
