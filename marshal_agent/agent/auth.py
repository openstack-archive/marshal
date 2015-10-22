# Copyright (c) 2015 Cisco Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Class to handle Marshal authentication against Keystone
"""

import requests
import json
import abc
import six

from marshal_agent.i18n import _

from marshal_agent.common import config
from marshal_agent.common import exception

CONF = config.CONF
LOG = config.LOG


@six.add_metaclass(abc.ABCMeta)
class AuthBase(object):
    @abc.abstractmethod
    def get_token_wrapper(self, key_id, project_id):
        raise NotImplementedError

    def get_key_wrapper(self, key_id, project_id):
        raise NotImplementedError

    def get_key_binary(self):
        raise NotImplementedError


class Auth(AuthBase):

    def __init__(self, conf=CONF, lic=None, kms_type=None):
        self.conf = conf
        self.lic = lic
        self.kms_type = kms_type

    def get_token_wrapper(self):
        return self._get_token_from_keystone()

    def get_token(self):
        if self.kms_type == 'vault':
            token = self.lic.x_vault_token
            return token, None
        else:
            return self._get_token_from_keystone()

    def get_key_wrapper(self):
        return self._get_key_from_kms()

    def _get_token_from_keystone(self):
        """ Get token from Keystone"""
        token = None
        kms_endpoint = None

        payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "id": self.lic.user_id,
                            "password": self.lic.user_pass
                        }
                    }
                },
                "scope": {
                    "project": {
                        "id": self.lic.project_id,
                        "domain": {
                            "id": "default"
                        },
                        "name": self.lic.project_name
                    }
                }
            }
        }

        self.json_data = json.dumps(payload)
        hdrs = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        pr = requests.post(self.lic.keystone_endpoint,
                           data=json.dumps(payload), headers=hdrs)
        if pr.status_code != 201:
            log_msg = _('Unable to get identity from Keystone.  Response Code\
                         was: '+str(pr.status_code))
            client_msg = _('Marshal was unable to authenticate.')
            raise exception.MarshalHTTPException(log_msg, client_msg,
                                                 pr.status_code)
        else:
            LOG.debug("Successfully authenticated against Keystone.")
        token = pr.headers['X-Subject-Token']
        pr_j = json.loads(pr.content)
        catalog = pr_j['token']['catalog']
        for endpoint in catalog:
            if endpoint.get('type') == 'kms':
                kms_endpoint = endpoint
                break

        return token, kms_endpoint
