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
 The Marshal module is intended to facilitate flexible volume encryption with
 dynamic key management
"""

import os
import sys
import errno
import tempfile
from stat import S_ISBLK
from marshal_agent.agent.keyRunner import KeyRunner
from marshal_agent.agent.license import License
from marshal_agent.agent.auth import Auth
from marshal_agent.agent.volCrypt import VolCrypt
from marshal_agent.common import config
from marshal_agent.common.exception import MarshalHTTPException
from marshal_agent.common.exception import PayloadDecodingError
from marshal_agent.common.exception import MissingKMSConfigurationError

CONF = config.CONF
LOG = config.LOG


def check_block_device(device):
    try:
        mode = os.stat(device).st_mode
    except OSError as e:
        print 'The specified device is invalid.'
        if e[0] == errno.ENOENT:
            LOG.info('Device %s was specified, but the file could not be found.\
                     ', device)
        sys.exit(1)

    if not S_ISBLK(mode):
        print 'The specified device is invalid.'
        LOG.info('Device was specified, but the file is not a valid block devic\
                  e file.')
        sys.exit(1)


def check_if_luks(vc, device, managed_name):
    LOG.debug('Performing isLuks check.')
    if device is None:
        print 'Please provide the device path.'
        LOG.info('isLuks check cancelled.  No device specified.')
        sys.exit(1)

    check_block_device(device)

    response = vc.is_luks(device)
    if response:
        print '{} is a LUKS device.'.format(device)
        return True
    else:
        print 'Could not establish {} as a valid LUKS device.'.format(device)
        return False


def missing_managed_name():
    LOG.info("Managed name is a required parameter for this operation.")
    print 'Please provide the managed name.'
    sys.exit(1)


def agent_main():
    LOG.info('Starting Marshal...')
    KM_OPT_GRP_NAME = config.KM_OPT_GRP_NAME
    km_conf_opts = getattr(CONF, KM_OPT_GRP_NAME)
    kms_type = km_conf_opts.kms_type.lower()
    VOL_CRYPT_GRP_NAME = config.VOL_CRYPT_GRP_NAME
    vc_conf_opts = getattr(CONF, VOL_CRYPT_GRP_NAME)
    action = vc_conf_opts.action
    device = vc_conf_opts.dev
    managed_name = vc_conf_opts.mn
    license_file = vc_conf_opts.lf
    key_size = str(vc_conf_opts.ks)
    cipher = vc_conf_opts.ci

    LOG.info('KMS type: %s', kms_type)
    lic = License(license_file, kms_type)
    vc = VolCrypt(device, managed_name)

    action = action.lower()
    LOG.info('%s action requested.', action)
    if action == 'unset':
        action = 'close'
    if action == 'isluks':
        check_if_luks(vc, device, managed_name)
        sys.exit(1)

    elif action == 'open' or action == 'format' or action == 'set':
        setNeedsFormat = False
        if not check_if_luks(vc, device, managed_name):
            if action == 'open':
                # For debugging, comment this exit and uncomment the pass
                sys.exit(1)
                # pass
            elif action == 'set':
                setNeedsFormat = True

        auth = Auth(CONF, lic, kms_type)
        try:
            token, kms_endpoint = auth.get_token()
        except MarshalHTTPException:
            print 'Authentication failed.'
            LOG.info('Unable to authenticate against Keystone.')
            sys.exit(1)

        try:
            key_runner = KeyRunner(lic, token, kms_endpoint)
        except MissingKMSConfigurationError as e:
            LOG.info(e.message)
            print e.message
            sys.exit(1)
        try:
            print 'Attempting to fetch key from KMS...'
            binary_key = key_runner.get_key_binary()
            print 'Key successfully retrieved from KMS...'
        except PayloadDecodingError:
            LOG.info('Unable to parse KMS response.')
            print 'Unable to parse KMS response.'
            sys.exit(1)
        except MarshalHTTPException as e:
            LOG.info('Error requesting key from from KMS: %s', e.status_code)
            print 'Unable to access KMS.'
            sys.exit(1)

        tmpdir = tempfile.mkdtemp()
        key_file_name = 'key.bin'

        # Ensure the file is read/write by the creator only
        saved_umask = os.umask(0077)

        path = os.path.join(tmpdir, key_file_name)
        try:
            with open(path, "wb") as tmp:
                tmp.write(binary_key)
            if action == 'open':
                if managed_name is None:
                    missing_managed_name()
                result = vc.open_volume(key_file=path)
                if result == 0:
                    print 'The volume was successfully opened.'
            elif action == 'format':
                result = vc.format_volume(cipher=cipher, key_size=key_size,
                                          key_file=path)
                if result == 0:
                    print 'The volume was successfully formatted.'
            elif action == 'set':
                if setNeedsFormat:
                    result = vc.format_volume(cipher=cipher, key_size=key_size,
                                              key_file=path)
                    if result == 0:
                        print 'The volume was successfully formatted.'
                if managed_name is None:
                    missing_managed_name()
                result = vc.open_volume(key_file=path)
                if result == 0:
                    print 'The volume was successfully opened.'
                elif result == 2:
                    LOG.info("Open failed on set. Attempting format...")
                    result = vc.format_volume(cipher=cipher, key_size=key_size,
                                              key_file=path)
                    if result == 0:
                        print 'The volume was successfully formatted.'
                    result = vc.open_volume(key_file=path)
                    if result == 0:
                        print 'The volume was successfully opened.'

        except IOError as e:
            print 'IOError'
        else:
            pass
        finally:
            os.remove(path)
            os.umask(saved_umask)
            os.rmdir(tmpdir)

    elif action == 'close':
        if not check_if_luks(vc, device, managed_name):
            sys.exit(1)
        if managed_name is None:
            missing_managed_name()
        result = vc.close_volume()
        if result == 0:
            print 'The volume was successfully closed.'

    elif action == 'status':
        if not check_if_luks(vc, device, managed_name):
            sys.exit(1)
        if managed_name is None:
            missing_managed_name()
        vc.status_volume()

if __name__ == '__main__':
    agent_main()
