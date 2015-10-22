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
Test class dedicated to testing the KeyRunner class in isolation / with mocks
"""

import unittest
from marshal_agent.common.exception import MarshalHTTPException
import responses

# Stash the command-line args so the oslo config doesn't hoover
# the unittest args
import sys
tempArgs = []
for x in sys.argv:
    tempArgs.append(x)
del sys.argv[1:]
__builtins__['TESTING_MARSHAL'] = True
from marshal_agent.agent.keyRunner import KeyRunner
for x in tempArgs:
    sys.argv.append(x)


class TestKeyRunner(unittest.TestCase):

    def __init__(self,  *args, **kwargs):
        super(TestKeyRunner, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TestKeyRunner, self).setUp()

    """
    Mocked / Isolation Tests
    """
    """
    Testing 200 with key received
    """
    @responses.activate
    def test_success_with_mocking(self):
        keyRunner = KeyRunner()
        conf = keyRunner.conf
        KM_OPT_GRP_NAME = keyRunner.config.KM_OPT_GRP_NAME
        conf_opts = getattr(conf, KM_OPT_GRP_NAME)
        kms_base = conf_opts.kms_base
        kms_get_key_api = conf_opts.kms_get_key_api
        kms_key_id = conf_opts.kms_key_id
        URL = kms_base+kms_get_key_api+kms_key_id
        responses.add(responses.GET, URL,
                      status=200,
                      body='aVeryVerySecretKey',
                      content_type="application/json")
        response = keyRunner.get_key_binary()
        self.assertNotEqual(response, None,
                            "TestKeyRunner test_success_with_mocking: Failed!")
        if response is not None:
            assert response == 'aVeryVerySecretKey'

    """
    Testing 200 with no key received
    """
    @responses.activate
    def test_partial_success_with_mocking(self):
        keyRunner = KeyRunner()
        conf = keyRunner.conf
        KM_OPT_GRP_NAME = keyRunner.config.KM_OPT_GRP_NAME
        conf_opts = getattr(conf, KM_OPT_GRP_NAME)
        kms_base = conf_opts.kms_base
        kms_get_key_api = conf_opts.kms_get_key_api
        kms_key_id = conf_opts.kms_key_id
        URL = kms_base+kms_get_key_api+kms_key_id
        responses.add(responses.GET, URL,
                      status=200,
                      body=None,
                      content_type="application/json")
        response = keyRunner.get_key_binary()
        self.assertEqual(response, None, "TestKeyRunner \
                        test_partial_success_with_mocking:  Failed!")
    """
    Testing 403
    """
    @responses.activate
    def test_successful_failure_code_403_with_mocking(self):
        keyRunner = KeyRunner()
        conf = keyRunner.conf
        KM_OPT_GRP_NAME = keyRunner.config.KM_OPT_GRP_NAME
        conf_opts = getattr(conf, KM_OPT_GRP_NAME)
        kms_base = conf_opts.kms_base
        kms_get_key_api = conf_opts.kms_get_key_api
        kms_key_id = conf_opts.kms_key_id
        URL = kms_base+kms_get_key_api+kms_key_id
        responses.add(responses.GET, URL,
                      status=403,
                      body='aVeryVerySecretKey',
                      content_type="application/json")
        with self.assertRaises(MarshalHTTPException) as cm:
            keyRunner.get_key_binary()
        self.assertEqual(cm.exception.status_code, 403, "TestKeyRunner\
                         test_successful_failure_code_403_with_mocking:\
                         Failed! Response Code="+str(cm.exception.status_code))

if __name__ == '__main__':
    unittest.main()
