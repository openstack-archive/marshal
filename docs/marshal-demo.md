1.Create symmetric keys using Barbican Order API.

2.Inject license file into VM using a cloud-config script:

```
#cloud-config
write_files:
-   content: |
      {
         "license":
         {
            "identity": {
               "version":"v3",
               "endpoint":"[KMS endpoint url]"
            },
            "project": {
               "id":"f383613fbcd74d6f8f9d4a40721ef811",
               "name":"marshal-demo"
            },
            "credentials": {
               "type":"user",
               "user": {
                  "id":"[user_id]",
                  "password":"[user_password]"
               }
            },
            "key": {
               "id":"[key id]"
            }
         }
      }
    owner: root:root
    path: /tmp/license.json
    permissions: '0644'

```
3.Create volume and attach to vm using Horizon

4.Look for the attached disk 

```
lsblk

lsblk -d -n -oNAME,RO | grep '0$' | awk {'print $1'}
  
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
vda    253:0    0  50G  0 disk 
└─vda1 253:1    0  50G  0 part /
vdb    253:16   0   2G  0 disk 
```
    
5.Set v-disk with marshal and dm-crypt

```
sudo marshal.sh set -d /dev/vdb -m vdb1 -l /tmp/license.json
```
 
7.Look for the attached disk  

```
lsblk

NAME               MAJ:MIN RM SIZE RO TYPE  MOUNTPOINT
vda                253:0    0  50G  0 disk  
└─vda1             253:1    0  50G  0 part  /
vdb                253:16   0   2G  0 disk  
└─vdb1 (dm-0) 252:0    0   2G  0 crypt 
```
    
8.Check status

```
sudo marshal.sh status -d /dev/vdb -m vdb1 -v

/dev/mapper/vdb1 is active.
  type:    LUKS1
  cipher:  aes-cbc-essiv:sha256
  keysize: 256 bits
  device:  /dev/vdb
  offset:  4096 sectors
  size:    4190208 sectors
  mode:    read/write
Command successful.
```
    
9.create file system before mount

```
sudo mkfs.ext4 /dev/mapper/vdb1
```

10.Create mount point and mount the device point

```
sudo mkdir /cryptdisk1
sudo mount /dev/mapper/vdb1 /cryptdisk1
```
    
11.Verify file system on device

```
sudo df -PTH /dev/mapper/vdb1

or 
sudo df -PTH /dev/mapper/vdb1 | awk '{print $2}' | sed -n '1!p'
```

12.Write something 

```
cd /cryptdisk1
sudo vi crypttest.txt
```
    
13.Search content

```
sudo grep "super" /cryptdisk1/*
```

14.Unmount disk

```
sudo umount /cryptdisk1
```

15.Unset disk

```
sudo ./marshal.sh unset -d /dev/vdb -m vdb1
```
16.Search content on device 

```
sudo grep "super" /dev/vdb
```

