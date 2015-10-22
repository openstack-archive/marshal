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
Class to handle KMS key retrieval
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
class KeyAgentBase(object):
    @abc.abstractmethod
    def get_key_wrapper(self, key_id, project_id):
        raise NotImplementedError

    def get_key_binary(self):
        raise NotImplementedError


class KeyRunner(KeyAgentBase):

    def __init__(self, lic=None, token=None, endpoint=None, conf=CONF,
                 key_id=None, project_id=None):

        '''
        if conf is not None:
            CONF = conf;
        else:
            CONF = config.CONF
        LOG = config.LOG
        self.LOG = LOG
        # LOG = CONF.LOG
        # self.conf = conf
        # self.conf = conf
        #CONF = conf.CONF
        '''
        self.config = config
        self.conf = CONF
        KM_OPT_GRP_NAME = config.KM_OPT_GRP_NAME
        conf_opts = getattr(CONF, KM_OPT_GRP_NAME)
        self.kms_type = conf_opts.kms_type.lower()

        if self.kms_type is None or self.kms_type == 'barbican':
            # For Barbican, we normally get endpoint from Keystone, but this
            #   allows bypass of keystone for testing Barbican interface:
            if lic is None:
                if key_id is None or project_id is None:
                    self.key_id = conf_opts.kms_key_id
                    self.project_id = conf_opts.kms_project_id
                else:
                    self.key_id = key_id
                    self.project_id = project_id
            else:
                self.project_id = lic.project_id
                self.key_id = lic.key_id
            if endpoint is None:
                # Allows manually configured Barbican or other KMS:
                self.kms_endpoint = conf_opts.kms_base+conf_opts.\
                    kms_get_key_api
                LOG.debug('Using Barbican endpoint from CONF')
            else:
                self.kms_endpoint = endpoint.get('endpoints')[0].\
                    get('url')+'/secrets/'
                LOG.debug('Using Barbican endpoint from Keystone')
        elif self.kms_type == 'vault':
            # For vault we want to be able to provide kms endpoint details in
            # license file or conf file or, some mixture of the two.
            #  Give license file the priority
            try:
                self.kms_base = lic.kms_base
            except AttributeError:
                if conf_opts.kms_base is not None:
                    self.kms_base = conf_opts.kms_base
            try:
                self.kms_get_key_api = lic.kms_get_key_api
            except AttributeError:
                if conf_opts.kms_get_key_api is not None:
                    self.kms_get_key_api = conf_opts.kms_get_key_api
            try:
                self.kms_endpoint = self.kms_base+self.kms_get_key_api
            except AttributeError:
                raise exception.MissingKMSConfigurationError

        self.lic = lic
        self.token = token

    def get_key_wrapper(self, key_id, project_id):
        return self._get_key_from_kms(key_id, project_id)

    def get_key_binary(self):
        return self._get_key_from_kms(accept='application/octet-stream')

    def _get_key_from_kms(self, accept=None):
        if self.kms_type is None or self.kms_type == 'barbican':
            if accept:
                headers = {
                    'Accept': accept,
                    'X-Project-Id': self.project_id
                }
            else:
                headers = {
                    'Accept': 'application/json',
                    'X-Project-Id': self.project_id
                }

            if self.token is not None:
                headers['X-Auth-Token'] = self.token
            key_manager_url = self.kms_endpoint+format(self.key_id)
        elif self.kms_type == 'vault':
            if self.token is not None:
                headers = {
                    'Accept': 'application/json'
                }
                headers['X-Vault-Token'] = self.token
            key_manager_url = self.kms_endpoint

        LOG.debug('Calling KMS API at: %s', key_manager_url)

        content = None

        r = requests.get(key_manager_url, headers=headers)
        if r.status_code != 200:
            log_msg = _('Unable to get key from KMS.  Response Code was: ' +
                        str(r.status_code))
            client_msg = _('Unable to get key from KMS')
            raise exception.MarshalHTTPException(log_msg, client_msg,
                                                 r.status_code)
        elif r.content is None or r.content == '' or r.content == 'None':
            LOG.info('KMS returned a blank key!')
        else:
            LOG.info('Successfully retrieved key from KMS.')
            content = r.content
        if self.kms_type is None or self.kms_type == 'barbican':
            key = content
        elif self.kms_type == 'vault':
            try:
                gr_j = json.loads(content)
                key = gr_j['data']['value']
            except (ValueError, KeyError, TypeError):
                msg = _('Unable to parse JSON response from Key Manager')
                raise exception.PayloadDecodingError(msg)

        return key
