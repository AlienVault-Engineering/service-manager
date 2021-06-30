import os

from service_buddy_too.ci.build_creator import FileBasedBuildCreator
from service_buddy_too.service.service import Service
from service_buddy_too.util.command_util import invoke_process


class TravisBuildCreator(FileBasedBuildCreator):

    def options(self):
        return {}

    def init(self,  default_config: dict, build_templates: dict, template_directory: str,
             user: str = None, password: str = None):
        super(TravisBuildCreator, self).init( default_config, build_templates, template_directory)
        self.use_org = default_config.get("use-travis-open-source", True)
        self.gh_token = default_config.get('github-token', os.environ.get('GITHUB_TOKEN', ''))
        self.pypi_user = default_config.get('pypi-user', os.environ.get('PYPI_USER'))
        self.pypi_pass = default_config.get('pypi-pass', os.environ.get('PYPI_PASS'))
        self.default_args = ['--no-interactive']
        if self._invoke_travis(['--help'], append_org=False) != 0:
            raise Exception("Travis CLI must be installed to use travis build creator.  "
                            "See https://github.com/travis-ci/travis.rb#installation")
        if self._invoke_travis(['login', '--github-token', self.gh_token]) != 0:
            raise Exception("Unable to authenticate Travis CLI. Please verify github token is configured properly.")

    def _build_exists_action(self, service_dir: str, build_template: dict, service_definition: Service):
        self._invoke_travis(['enable'], exec_dir=service_dir)

    def _get_build_file(self, service_dir):
        return os.path.join(service_dir, ".travis.yml")

    @classmethod
    def get_type(cls):
        return "travis"

    def _create_script_build(self, service_dir: str, build_configuration: dict, service_definition: Service):
        language_ = build_configuration.get('language', 'python')
        args = [
            'init',
            language_
        ]
        if language_ == 'python':
            args.append('--python')
            args.append('2.7')

        install_script = build_configuration.get('install', None)
        if install_script:
            args.append('--install')
            self._append_rendered_arguments(args, install_script, service_definition)

        script = build_configuration.get('script', None)
        if script:
            args.append('--script')
            self._append_rendered_arguments(args, script, service_definition)

        self._invoke_travis(args, exec_dir=service_dir)
        use_pypi = build_configuration.get('pypi-deploy', False)
        if use_pypi:
            self._write_deploy_stanza(service_dir)
            self._invoke_travis(['encrypt', self.pypi_pass, '--add', 'deploy.password'], exec_dir=service_dir)


    @staticmethod
    def _append_rendered_arguments(args, install_script, service_definition):
        if isinstance(install_script, str):
            install_script = [install_script]
        for script in install_script:
            if "${" in script:
                # Assume is there is bash style escape we don't python escape.  sucks but the extent of my attention
                args.append("\"{}\"".format(script))
            else:
                args.append("\"{}\"".format(script.format(**service_definition)))

    def _write_deploy_stanza(self, service_dir):
        with open(self._get_build_file(service_dir), 'a') as build_file:
            build_file.writelines([
                '\n'
                'deploy\n',
                '\tprovider: pypi\n',
                '\tuser: {}\n'.format(self.pypi_user),
                '\tdistributions: sdist bdist_wheel\n',
                '\tserver: https://upload.pypi.org/legacy\n'
            ])

    def _invoke_travis(self, args, exec_dir=None, append_org=True):
        base_args = ['travis']
        base_args.extend(args)
        base_args.extend(self.default_args)
        if append_org: base_args.append('--org' if self.use_org else '--pro')
        if exec_dir:
            return invoke_process(args=base_args, exec_dir=exec_dir)
        else:
            return invoke_process(args=base_args)
