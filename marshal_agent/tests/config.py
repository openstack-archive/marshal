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
Configuration setup for Testing Marshal.
"""

import os
import sys
import errno
from oslo_config import cfg
from oslo_log import log

import marshal_agent.i18n as u
# import marshal.version

__builtins__['TESTING_MARSHAL'] = True

# Check if we have root perms.  May need tweaking here for SELinux, ACLs, etc..
if __builtins__.get('TESTING_MARSHAL', False) is False and os.getuid() != 0:
    print "Marshal needs to be run with root permissions."
    sys.exit(1)

KMS_TYPE = 'Barbican'
KMS_BASE = 'a_test_base'
KMS_API = 'a_test_api'
SECRET_ID = 'a_test_secret_id'
TENANT_ID = None
KEYSTONE_ENDPOINT = None

KM_OPT_GRP_NAME = 'KM-OPT'
VOL_CRYPT_GRP_NAME = 'crypt'

opt_group = cfg.OptGroup(name=KM_OPT_GRP_NAME,
                         title='Key Manager config settings')

openam = [
    cfg.StrOpt('kms_type', default=KMS_TYPE,
               help=('Key Management Store Type.')),
    cfg.StrOpt('kms_base', default=KMS_BASE,
               help=('Key management service base url')),
    cfg.StrOpt('kms_get_key_api', default=KMS_API,
               help=('Key management service key retrieval API')),
    cfg.StrOpt('kms_key_id', default=SECRET_ID,
               help=('Key management service key ID')),
    cfg.StrOpt('kms_project_id', default=TENANT_ID,
               help=('Key management service project/tenant ID')),
    cfg.StrOpt('keystone_endpoint', default=KEYSTONE_ENDPOINT,
               help=('Keystone endpoint for authentication'))
]

vol_crypt_opt_group = cfg.OptGroup(name=VOL_CRYPT_GRP_NAME,
                                   title='Volume Encryption Options')

vol_crypt_opts = [
    cfg.StrOpt('action', default='isLuks',
               help=u._('One of: set, unset, isLuks, open, close, format,\
                         status')),
    cfg.StrOpt('dev', default=None,
               help=u._('The target device.')),
    cfg.StrOpt('mn', default=None,
               help=u._('The managed name for the device.')),
    cfg.StrOpt('lf', default='license.json',
               help=u._('The key license file.')),
    # Direct keyfile input not supported at this time for security reasons.
    # cfg.StrOpt('kf', default=None,
    #           help=u._('The key file.')),
    cfg.IntOpt('ks', default=256,
               help=u._('Limits the key size to the specified number of bytes.\
                        ')),
    cfg.StrOpt('ci', default='aes-cbc-essiv:sha256',
               help=u._('Cipher. The encryption algorithm.'))
]


def new_config():
    conf = cfg.ConfigOpts()
    log.register_options(conf)
    conf.register_cli_opts(vol_crypt_opts, group=vol_crypt_opt_group)
    return conf


def parse_args(conf, args=None, usage=None, default_config_files=None):
    conf(args=args,
         project='marshal',
         prog='marshal',
         # version=marshal.version.__version__,
         version='0.1',
         usage=usage,
         default_config_files=["test_marshal.conf"])

CONF = new_config()
CONF.register_group(opt_group)
CONF.register_opts(openam, opt_group)
formatter = log.logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                    %(message)s')
log.set_defaults(formatter)
parse_args(CONF)
try:
    log.setup(CONF, 'marshal')
except IOError as e:
    if (e[0] == errno.ENOENT):
        print "Could not access logfile!  Continuing without logging..."
LOG = log.getLogger(__name__)
