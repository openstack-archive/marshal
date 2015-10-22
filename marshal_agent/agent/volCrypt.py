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
The volcrypt module interfaces with cryptsetup
"""

from marshal_agent.common import config

import subprocess

CONF = config.CONF
LOG = config.LOG


class VolCrypt():

    def __init__(self, dev_path, mapped_name):
        self.dev_path = dev_path
        self.mapped_name = mapped_name

    def is_luks(self, dev_path):
        """Checks if the specified device uses LUKS for encryption.
        :param device: the device to check
        :returns: true if the specified device uses LUKS; false otherwise
        """
        try:
            # check to see if the device uses LUKS: exit status is 0
            # if the device is a LUKS partition and non-zero if not
            cmd = ["cryptsetup", 'isLuks', '--verbose', dev_path]
            output = subprocess.check_output(cmd, shell=False)
            LOG.debug(output)
            return True
        except subprocess.CalledProcessError as e:
            LOG.info(("isLuks exited with (status %(exit_code)s): "),
                     {"exit_code": e.returncode})
            return False

    def open_volume(self, **kwargs):
        """Opens the LUKS partition on the volume using the provided key file
        """
        LOG.debug("opening encrypted volume %s", self.dev_path)
        try:
            cmd = ["cryptsetup", "luksOpen"]

            key_file = kwargs.get("key_file", None)
            if key_file is not None:
                cmd.extend(["--key-file", key_file])

            cmd.extend([self.dev_path])
            cmd.extend([self.mapped_name])

            output = subprocess.check_output(cmd, shell=False)
            LOG.info("Successfully opened the volume.  Opening output was: %s",
                     output)
            return 0

        except subprocess.CalledProcessError as e:
            LOG.info(("luksOpen exited with (status %(exit_code)s)"),
                     {"exit_code": e.returncode})
            return e.returncode

    def close_volume(self, **kwargs):
        """Closes the LUKS partition on the volume
        """
        LOG.debug("closing encrypted volume %s", self.dev_path)
        try:
            cmd = ["cryptsetup", "luksClose"]

            cmd.extend([self.mapped_name])

            output = subprocess.check_output(cmd, shell=False)
            LOG.info("Successfully closed the volume.  Closing output was: %s",
                     output)
            return 0

        except subprocess.CalledProcessError as e:
            LOG.info(("luksClose exited with (status %(exit_code)s): "),
                     {"exit_code": e.returncode})
            return e.returncode

    def format_volume(self, **kwargs):
        """Creates a LUKS header on the volume.
        """
        LOG.debug("formatting encrypted volume %s", self.dev_path)
        try:
            cmd = ["cryptsetup", "--batch-mode", "luksFormat"]

            cipher = kwargs.get("cipher", None)
            if cipher is not None:
                cmd.extend(["--cipher", cipher])
            key_size = kwargs.get("key_size", None)
            if key_size is not None:
                cmd.extend(["--key-size", key_size])
            key_file = kwargs.get("key_file", None)
            if key_file is not None:
                cmd.extend(["--key-file", key_file])
            cmd.extend([self.dev_path])

            output = subprocess.check_output(cmd, shell=False)
            LOG.info("Successfully formatted the volume.  Format output was: \
                      %s", output)
            return 0

        except subprocess.CalledProcessError as e:
            LOG.info(("luksFormat exited with (status %(exit_code)s): "),
                     {"exit_code": e.returncode})
            return e.returncode

    def status_volume(self, **kwargs):
        """Statuses the LUKS partition on the volume
        """
        LOG.debug("Stating encrypted volume %s", self.dev_path)
        try:
            cmd = ["cryptsetup", "-v", "status"]

            cmd.extend([self.mapped_name])

            output = subprocess.check_output(cmd, shell=False)
            LOG.info("Status output was: %s", output)

        except subprocess.CalledProcessError as e:
            LOG.info(("status exited with (status %(exit_code)s): "),
                     {"exit_code": e.returncode})
