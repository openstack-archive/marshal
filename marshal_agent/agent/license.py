# Copyright (c) 2015 Cisco Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility class to handle license data extraction and management
"""

import sys
import json
from marshal_agent.common import config

LOG = config.LOG


class License(object):

    def __init__(self, license_file, kms_type=None):
        self.keystone_endpoint = None
        self.project_id = None
        self.project_name = None
        self.key_id = None
        self.mode = None
        self.user_id = None
        self.user_pass = None
        self.kms_type = kms_type
        self.parse_license_file(license_file)

    def parse_license_file(self, lf):
        try:
            with open(lf, 'r') as lf_h:
                l_data = (lf_h.read()).rstrip()
                try:
                    jl_data = json.loads(l_data)
                except ValueError as e:
                    LOG.debug("Unable to parse license file: %s", str(e))
                    print 'Unable to parse license file: '+str(e)
                    sys.exit(1)

                if self.kms_type == 'vault':
                    self.x_vault_token = \
                        jl_data['license']['identity']['token']
                    try:
                        self.kms_base = \
                            jl_data['license']['endpoint']['kms_base']
                    except KeyError:
                        pass
                    try:
                        self.kms_get_key_api = \
                            jl_data['license']['endpoint']['kms_get_key_api']
                    except KeyError:
                        pass
                else:
                    self.keystone_endpoint = \
                        jl_data['license']['identity']['endpoint']
                    self.project_id = jl_data['license']['project']['id']
                    self.project_name = jl_data['license']['project']['name']
                    self.key_id = jl_data['license']['key']['id']
                    self.mode = jl_data['license']['credentials']['type']
                    if self.mode == 'user':
                        self.user_id = \
                            jl_data['license']['credentials']['user']['id']
                        self.user_pass = \
                            jl_data['license']['credentials']['user']['password\
                                    ']

        except IOError:
            LOG.info("Unable to locate license file: %s", lf)
            print 'License file not found.'
            sys.exit(1)
        except KeyError as e:
            LOG.info("Unable to parse license file: %s", str(e))
            print 'Unable to parse license file.'
            sys.exit(1)
