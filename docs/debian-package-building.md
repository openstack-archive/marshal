**1. Adding official Openstack Kilo PPA repository.**  
It's needed because some marshal dependencies available only from it.
```
sudo apt-get install ubuntu-cloud-keyring
echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu" \
     "trusty-updates/kilo main" \
     | sudo tee /etc/apt/sources.list.d/cloudarchive-kilo.list
```
**2. Update index of system packages.**
```
sudo apt-get update
```
**3. Install build tools and Marshal dependencies**
```
sudo apt-get install build-essential debhelper fakeroot git python-setuptools python-pbr python-all
```
**4. Clone fresh Marshal repo**
```
git clone https://github.com/CiscoCloud/marshal
cd marshal
```
**5. Build deb package**
```
dpkg-buildpackage -us -uc
```
**6. Install package to the target system**
```
sudo dpkg -i ../marshal_*_all.deb   # Errors on this step are normal, next step fixes them.
sudo apt-get -f install             # (Optional) This installs broken marshal dependencies.
```
**7. And try to use it**
```
sudo marshal --help
sudo marshal.sh -h
```
