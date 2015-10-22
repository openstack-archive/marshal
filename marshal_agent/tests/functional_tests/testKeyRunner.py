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
Test class dedicated to testing the KeyRunner class end-to-end
"""

import unittest
from unittest import TestCase
from marshal_agent.agent.keyRunner import KeyRunner
# from marshal_agent.common import config
from oslo_log import log as logging

# CONF = config.CONF
# LOG = config.LOG
LOG = logging.getLogger(__name__)


class TestKeyRunner(TestCase):

    """
    Functionality Test
    """
    def test_success_without_mocking(self):
        LOG.info("TestKeyRunner test_success_without_mocking: initializing...")
        keyRunner = KeyRunner()
        response = keyRunner.get_key_binary()
        self.assertNotEqual(response, None, "TestKeyRunner test_success_without\
                            _mocking:  Failed!")
        if response is not None:
            LOG.info("TestKeyRunner test_success_without_mocking: Key Retrieved\
                        !")
            print "binary key is: " + response
            with open('key.bin', 'wb') as fh:
                fh.write(response)
        LOG.info("TestKeyRunner test_success_without_mocking: finalizing...")

if __name__ == '__main__':
    unittest.main()
