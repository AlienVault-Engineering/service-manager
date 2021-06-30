import logging
import os

from service_buddy_too.service import loader
from service_buddy_too.vcs.vcs import VCS


class ServiceContext(object):

    def __init__(self, filter_string, service_filter_string, service_directory, destination_directory):
        super(ServiceContext, self).__init__()
        self.destination_directory = destination_directory
        if not os.path.exists(service_directory):
            logging.warning("Service directory does not exist, not loading services or vcs - {}".format(service_directory))
        else:
            self.application_map = loader.load_service_definitions(service_directory=service_directory,
                                                                   code_directory=destination_directory,
                                                                   app_filter=filter_string,
                                                                   service_filter=service_filter_string)
            self.vcs = VCS(service_directory=service_directory)
