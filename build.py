from pybuilder.core import init, use_plugin

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("exec")
use_plugin("python.unittest")
use_plugin("python.pylint")
use_plugin("copy_resources")
use_plugin("python.pycharm")

name = "service-buddy-too"
default_task = "publish"


@init
def initialize(project):
    build_number = project.get_property("build_number")
    if build_number is not None and "" != build_number:
        project.version = build_number
    else:
        project.version = "0.0.999"
    # Project Manifest
    project.summary = "CLI for managing micro-services"
    project.home_page = "https://github.com/rspitler/service-buddy"
    project.description = "CLI for managing micro-services"
    project.author = "rspitler"
    project.license = "Apache 2.0"
    project.url = "https://github.com/rspitler/service-buddy"
    project.depends_on_requirements("requirements.txt")
    # Build and test settings
    project.set_property("run_unit_tests_propagate_stdout", True)
    project.set_property("run_unit_tests_propagate_stderr", True)
    project.include_file('service_buddy_too', "codegenerator/builtin-code-templates.json")
    project.set_property("distutils_upload_repository", "pypi")
