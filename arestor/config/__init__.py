# Copyright 2016 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from oslo_config import cfg
from oslo_log import log as logging

from arestor.config import factory
from arestor import version

CONFIG = cfg.ConfigOpts()

logging.register_options(CONFIG)
for option_class in factory.get_options():
    option_class(CONFIG).register()

_DEFAULT_CONFIG_FILES = [
    config_file for config_file in ("/etc/arestor/arestor.conf",
                                    "etc/arestor/arestor.conf", "arestor.conf")
    if os.path.isfile(config_file)
]

if _DEFAULT_CONFIG_FILES:
    CONFIG([], project='arestor', version=version.get_version(),
           default_config_files=_DEFAULT_CONFIG_FILES)
