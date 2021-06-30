import os


class Application(dict):
    def __init__(self, application,code_directory):
        super(Application, self).__init__()
        self.code_directory = code_directory
        self.application = application

    def add_service(self, role, service):
        self[role] = service

    def get_app_code_directory(self):
        return os.path.join(self.code_directory, self.application)


