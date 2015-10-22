###Marshal Getting Started Guide

####Deploying Marshal
Marshal is currently deployable for Debian-based Linux systems and a Debian package is available and has been tested in Ubuntu 14.04.  The intention is to have Marshal pre-installed on certain images.  However, in cases where Marshal is not pre-installed, it can be installed as a Debian package.  The procedure to install the Debian package is given here:

######ToDo: get clean Debian installation procedure

To check if Marshal is installed, run the following command:

```
sudo marshal -h
```

There are several ways to configure Marshal.  The primary way to configure Marshal defaults is in the /etc/marshal/marshal.conf file:

```
[DEFAULT]
# Show more verbose log output (sets INFO log level output)
# verbose = True

# Show debugging output in logs (sets DEBUG log level output)
# debug = True

# log file location
log_file = /var/log/marshal/marshal.log

[KM-OPT]
# This section intended for dev/test purposes only
# Default Auth Endpoint - for dev/test purposes only
keystone_endpoint=http://173.39.224.159:35357/v3/auth/tokens
# Default KMS fields - for dev/test purposes only
kms_base=[HOST]
kms_get_key_api=[some API]
kms_key_id=[some key id]
kms_project_id=[some project id]

[crypt]
#This section for 
lf=/tmp/license.json
ci=aes-cbc-essiv:sha256
ks=256

```

More sensitive configuration details are configured in a JSON-formatted license file.  The license file can come in 3 different flavors depending on the type of credentials to be used by the Marshal agent to authenticate.  The 3 types are as follows:

* user-based
* certififcate
* trust

Example license configuration files for each of these 3 types are given here:

user-based license:
```
{
   "license":
   {
      "identity": {
         "version":"v3",
         "endpoint":"http://[KEYSTONE_HOST]/v3/auth/tokens"
      },
      "project": {
         "id":"f383613fbcd74d6f8f9d4a40721ef811",
         "name":"marshal-demo"
      },
      "credentials": {
         "type":"user",
         "user": {
            "id":"4c49397e2d9f41e392498b8079c65343",
            "password":"changeit"
         }
      },
      "key": {
         "id":"e2ccc708-7c8d-437d-aaac-12bad476dd25"
      }
   }
}
```

certificate-based license:
```
{
   "license":
   {
      "identity": {
         "version":"v3",
         "endpoint":"http://[KEYSTONE_HOST]/v3/auth/tokens"
      },
      "project": {
         "id":"12345",
         "name":"marshal-demo"
      },
      "credentials": {
         "type":"cert",
         "cert": {
            "subject":"some_subject"
            "signature":"some_signature"
            "pub_key":"some_key"
         }
      },
      "key": {
         "id":"1b13ffdc-1b79-40ce-b94e-f4a2f9253d91"
      }
   }
}
```

trust-based license:
```
{
   "license":
   {
      "identity": {
         "version":"v3",
         "endpoint":"http://[KEYSTONE_HOST]/v3/auth/tokens"
      },
      "project": {
         "id":"12345",
         "name":"marshal-demo"
      },
      "credentials": {
         "type":"trust",
         "trust": {
            "id":"4c49397e2d9f41e392498b8079c65343"
         }
      },
      "key": {
         "id":"1b13ffdc-1b79-40ce-b94e-f4a2f9253d91"
      }
   }
}
```

The license path+file can be specified in the Marshal configuration file, or passed as a parameter with the '--crypt-lf' switch.  Eg:

```
sudo marshal --crypt-action open --crypt-dev /dev/vdc2 --crypt-mn priv_part --crypt-lf /tmp/license.json
```
It is recommended that the license file be placed in the /tmp folder or otherwise be disposed of once the desired encryption state is achieved.

####Understanding Marshal
#####Authentication and Key retrieval
######General Behavior
Using the Keystone endpoint given by the configuration license:identity:endpoint, Marshal will attempt to authenticate using the configuration license:credentials:type and associated credential details.  

######Barbican-specifc behavior
Upon successfully authenticating, Marshal will receive an OpenStack token which should provide a Barbican Key Management Store (KMS) endpoint.  Marshal will then attempt to retrieve the binary key associated with the key id given in the configuration 

######Other-KMS bevahior
Other KMS systems (non-Barbican) are not currently supported, but are expected to be in the near future.

#####Encryption operations
Once Marshal has successfully retrieved the key, an encryption operation can commence against that key.  Currently, only volume and volume partition encryption operations are supported, but other operations are anitipated in the future possibly including encrypted communications. The Marshal 'set' action will open an encrypted volume (if it can find the key), and it will format the target using LUKS formatting, if needed.  The Marshal 'unset' command will close the target.

####Example Marshal operations:
#####Formatting a block device:
```
sudo marshal --crypt-action format --crypt-dev <device> --crypt-mn <managed name>
```

Example:
```
cloud-user@marshal-test-8:~/marshal$ lsblk
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
vda    253:0    0  50G  0 disk 
└─vda1 253:1    0  50G  0 part /
vdb    253:16   0   2G  0 disk 
vdc    253:32   0   2G  0 disk  

sudo marshal --crypt-action format --crypt-dev /dev/vdb --crypt-mn backup

cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action format --crypt-dev /dev/vdb --crypt-mn backup
Device /dev/vdb is not a valid LUKS device.
Command failed with code 22: Device /dev/vdb is not a valid LUKS device.
Could not establish /dev/vdb as a valid LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully formatted.

```

#####Opening a block device:
```
sudo marshal --crypt-action open --crypt-dev <device> --crypt-mn <managed name>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action open --crypt-dev /dev/vdb --crypt-mn backup
/dev/vdb is a LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully opened.

cloud-user@marshal-test-8:~/marshal$ lsblk
NAME            MAJ:MIN RM SIZE RO TYPE  MOUNTPOINT
vda             253:0    0  50G  0 disk  
└─vda1          253:1    0  50G  0 part  /
vdb             253:16   0   2G  0 disk  
└─backup (dm-0) 252:0    0   2G  0 crypt 
vdc             253:32   0   2G  0 disk  

```

#####Unsetting/Closing a block device:
Unset=close.  Either command can be used to achieve the same result.
```
sudo marshal --crypt-action unset --crypt-dev <device> --crypt-mn <managed name>
sudo marshal --crypt-action close --crypt-dev <device> --crypt-mn <managed name>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action close --crypt-dev /dev/vdb --crypt-mn backup
/dev/vdb is a LUKS device.
The volume was successfully closed.
cloud-user@marshal-test-8:~/marshal$ lsblk
NAME             MAJ:MIN RM SIZE RO TYPE  MOUNTPOINT
vda              253:0    0  50G  0 disk  
└─vda1           253:1    0  50G  0 part  /
vdb              253:16   0   2G  0 disk  
vdc              253:32   0   2G  0 disk  

```

#####Setting a block device:
To "set" the device means to open it as a LUKS volume if possible, and if not then LUKS format and then open the device.
```
sudo marshal --crypt-action set --crypt-dev <device> --crypt-mn <managed name>
```
Example requiring format
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action set --crypt-dev /dev/vdc --crypt-mn backup2
Device /dev/vdc is not a valid LUKS device.
Command failed with code 22: Device /dev/vdc is not a valid LUKS device.
Could not establish /dev/vdc as a valid LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully formatted.
The volume was successfully opened.

cloud-user@marshal-test-8:~/marshal$ lsblk
NAME             MAJ:MIN RM SIZE RO TYPE  MOUNTPOINT
vda              253:0    0  50G  0 disk  
└─vda1           253:1    0  50G  0 part  /
vdb              253:16   0   2G  0 disk  
└─backup (dm-0)  252:0    0   2G  0 crypt 
vdc              253:32   0   2G  0 disk  
└─backup2 (dm-1) 252:1    0   2G  0 crypt 
```

Example not requiring format
```
cloud-user@marshal-test-8:~/marshal$  sudo marshal --crypt-action set --crypt-dev /dev/vdb --crypt-mn backup
/dev/vdb is a LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully opened.
cloud-user@marshal-test-8:~/marshal$ lsblk
NAME             MAJ:MIN RM SIZE RO TYPE  MOUNTPOINT
vda              253:0    0  50G  0 disk  
└─vda1           253:1    0  50G  0 part  /
vdb              253:16   0   2G  0 disk  
└─backup (dm-0)  252:0    0   2G  0 crypt 
vdc              253:32   0   2G  0 disk  
└─backup2 (dm-1) 252:1    0   2G  0 crypt 
```

#####Statusing a block device:
```
sudo marshal --crypt-action status --crypt-dev <device> --crypt-mn <managed name>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action status --crypt-dev /dev/vdc --crypt-mn backup2
/dev/vdc is a LUKS device.
```

#####Statusing a block device with verbosity:
Adding the -v flag enables INFO messages to appear at the CLI
```
sudo marshal --crypt-action status --crypt-dev <device> --crypt-mn <managed name> -v
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action status --crypt-dev /dev/vdc --crypt-mn backup2 -v
2015-10-06 22:26:16.186 1669 INFO marshal_agent.common.config [-] status action requested.
/dev/vdc is a LUKS device.
2015-10-06 22:26:16.192 1669 INFO marshal_agent.common.config [-] Status output was: /dev/mapper/backup2 is active.
  type:    LUKS1
  cipher:  aes-cbc-essiv:sha256
  keysize: 256 bits
  device:  /dev/vdc
  offset:  4096 sectors
  size:    4190208 sectors
  mode:    read/write
Command successful.
```

#####Overriding the license file default as set in the configiration file:
```
sudo marshal --crypt-action <action> --crypt-dev <device> --crypt-mn <managed name> --crypt-lf <license file>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ mv /tmp/license.json .
License file not found.
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action status --crypt-dev /dev/vdc --crypt-mn backup2
License file not found.
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action status --crypt-dev /dev/vdc --crypt-mn backup2 --crypt-lf license.json
/dev/vdc is a LUKS device.
```
#####Overriding the cipher default as set in the configiration file:
```
sudo marshal --crypt-action <action> --crypt-dev <device> --crypt-mn <managed name> --crypt-ci <cipher>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action format --crypt-dev /dev/vdc --crypt-mn backup2 --crypt-ci aes-xts-plain64
/dev/vdc is a LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully formatted.
```

#####Overriding the key size default as set ub the configuration file:
```
sudo marshal --crypt-action <action> --crypt-dev <device> --crypt-mn <managed name> --crypt-ks <key size>
```
Example
```
cloud-user@marshal-test-8:~/marshal$ sudo marshal --crypt-action format --crypt-dev /dev/vdc --crypt-mn backup2 --crypt-ci aes-xts-plain64 --crypt-ks 512
/dev/vdc is a LUKS device.
Attempting to fetch key from KMS...
Key successfully retrieved from KMS...
The volume was successfully formatted.

```