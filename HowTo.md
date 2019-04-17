# Usage: Ubuntu

```sh 
# Install SystemTap (follow https://wiki.ubuntu.com/Kernel/Systemtap#Where_to_get_debug_symbols_for_kernel_X.3F for Ubuntu) 
apt-get install linux-image-$(uname -r)-dbgsym build-essential systemtap systemtap-runtime linux-headers-$(uname -r)
stap-prep
# Install python-pip and python module docopt
apt-get install python-pip 
pip install -r requirements_build.txt
# Make sure that python exists 
python --version
# build the kernel module
make clean;make VERBOSE=1  
```

# Usage: Ubuntu 18.04

See https://wiki.ubuntu.com/Debug%20Symbol%20Packages

```sh
# Add debugsym packages 
echo "deb http://ddebs.ubuntu.com $(lsb_release -cs) main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-proposed main restricted universe multiverse" | \
sudo tee -a /etc/apt/sources.list.d/ddebs.list
sudo apt install ubuntu-dbgsym-keyring
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F2EDC64DC5AEE1F6B9C621F0C8CAB6595FDFF622
sudo apt-get update 

# Install SystemTap (follow https://wiki.ubuntu.com/Kernel/Systemtap#Where_to_get_debug_symbols_for_kernel_X.3F for Ubuntu)
sudo apt-get install -y build-essential systemtap systemtap-runtime 
sudo apt-get install -y linux-image-$(uname -r)-dbgsym linux-headers-$(uname -r) linux-image-unsigned-$(uname -r)-dbgsym
stap-prep
# Install python-pip and python module docopt
apt-get install python-pip 
pip install -r requirements_build.txt
# Make sure that python exists 
python --version
# build the kernel module
make clean;make VERBOSE=1  
```

# Usage: CentOS 6

```sh 
# Install SCL environment
yum -y install rpm-build git  zlib zlib-devel libjpeg libjpeg-devel zlib zlib-devel libjpeg libjpeg-devel wget which tar systemtap scl-utils centos-release-scl stap-prep
# Edit file /etc/yum.repos.d/CentOS-Debuginfo.repo - enable the debug info
yum -y install  kernel-devel-$(uname -r) kernel-$(uname -r) kernel-debuginfo-$(uname -r) kernel-debuginfo-common-$(uname -r)
# Install GCC toolchain 5.3  
yum -y install devtoolset-4-gcc* python27 python27-python-devel.x86_64
scl enable devtoolset-4 bash                                                                                  
source /opt/rh/python27/enable                                                                          
pip install -r requirements.txt 
# Make sure that python exists 
python --version
# build the kernel module
make clean;make VERBOSE=1
```

# Usage: CentOS 7

```sh 
# Install SCL environment
yum -y install rpm-build git  zlib zlib-devel libjpeg libjpeg-devel zlib zlib-devel libjpeg libjpeg-devel wget which tar systemtap scl-utils centos-release-scl
stap-prep 
yum -y group install "Development Tools"
# Edit file /etc/yum.repos.d/CentOS-Debuginfo.repo - enable the debug info
yum -y install  kernel-devel-$(uname -r) kernel-$(uname -r) kernel-debuginfo-$(uname -r) kernel-debuginfo-common-$(uname -r)
yum -y install python27 python27-python-devel.x86_64
yum install epel-release
yum -y update
yum -y install python-pip
pip install -r requirements_build.txt 
# Make sure that python exists 
python --version
# build the kernel module
make clean;make VERBOSE=1
```

# Usage: Kernel module

```sh 
# load the module
sudo make load 
# check if the module is alive
cat /sys/kernel/yalas/probes 
while [ 1 ];do echo -en "\\033[0;0H";cat /sys/kernel/yalas/hit_counters | ./scripts/print_columns.py;sleep 0.2;done;
# Run application to read the data
./yalas --logs=/tmp/yalas --watch=/usr/lib/firefox/firefox --watch=/usr/bin/firefox
```

# Deployment

The deployment process allows to build the kernel driver on a development machine for further deployment 
in the production environment. The build script runs inside a Docker container where correct linux headers 
and kernel debug information are installed.  
 
Install [DockerCE](https://docs.docker.com/engine/installation/linux/ubuntu/)

Install required python modules 

```
pip install -r requirements_build.txt 
pip install -r requirements_deployment.txt
``` 

Generate dockerfiles (modify ./containers.yml if necessary)

```sh 
rm -f Dockerfile.* ;./scripts/dockerfile_generator.py --config=./docker/containers.yml   
```

Build Docker images. This operation should be done every time ./containers.yml is modified
See docker setup tips on https://github.com/larytet/dockerfile-generator

```sh 
for f in ./Dockerfile.*; do filename=`echo $f | sed -E 's/\..Dockerfile.(\S+)/\1/'`;echo Processing $filename;sudo docker build --tag $filename --file $f  .; done
# Create a local copy of the container for delivery by adding to the command 
# sudo docker save $filename -o $filename.tar;
```

The rest of the deployment can be done by running something like 

```sh
./scripts/build_driver.py -k Ubuntu:4.15.0-46-generic,Ubuntu:4.18.0-17-generic -v DEBUG
```
The script build_driver.py will download neccessary packages, install the packages in the container, run the container, run build. The end result is a 
kernel module `yalas-4.15.0-46-generic.ko`.

Alternatively it is possible to do the build in a couple of steps. Download the kernel debug information for the target kernels 

```sh
rm -f images.txt
./scripts/distro/scrape.py -k Ubuntu:4.2.0-38-generic,Ubuntu:4.8.0-41-generic,CentOS:2.6.32-71.7.1.el6.x86_64,CentOS:2.6.32-642.el6.x86_64 > images.txt
wget --continue --input-file=../images.txt
```
	
Run container and build the kernel driver
 
```sh 
make clean;make yalas_drv.stp;
cp yalas_drv.stp ./docker
# Enter the container shell
docker run -it -v $PWD/docker:/etc/docker centos6
export KERNEL_VERSION=2.6.32-642.el6.x86_64	
$SHARED_FOLDER/build_module_centos.sh $SHARED_FOLDER/kernel-debuginfo-$KERNEL_VERSION.rpm $SHARED_FOLDER/kernel-debuginfo-common-x86_64-$KERNEL_VERSION.rpm $SHARED_FOLDER/kernel-devel-$KERNEL_VERSION.rpm $SHARED_FOLDER/kernel-$KERNEL_VERSION.rpm
# Exit the container shell
exit  
# Remove the container and free the storage
docker rm -fv $(docker ps -a -q) 

# For Ubuntu try something like
docker run -it -v $PWD:/etc/yalas ubuntu.16.10
$SHARED_FOLDER/docker/build_module_ubuntu.sh $SHARED_FOLDER/linux-image-4.8.0-41-generic-dbgsym_4.8.0-41.44~16.04.1_amd64.ddeb $SHARED_FOLDER/linux-image-4.8.0-41-generic_4.8.0-41.44~16.04.1_amd64.deb $SHARED_FOLDER/linux-headers-4.8.0-41-generic_4.8.0-41.44~16.04.1_amd64.deb  $SHARED_FOLDER/linux-headers-4.8.0-41_4.8.0-41.44~16.04.1_all.deb
exit  
```

Optionally cleanup to free the disk space

```sh 
sudo docker rm -fv $(sudo docker ps -a -q) 
# kernel images in the *.rpm and *.*deb files can be removed as well
```

# Development

Install VirtualBox and create a Ubuntu 18.04 VM

	# Install SSH server
	sudo apt-get instal openssh-server
	# Disable SW updates
	vi /etc/apt/apt.conf.d/20auto-upgrades
	

Insert VB Guest Additions (menu devices)
	
	sudo mkdir /mnt/cdrom
	sudo mount /dev/cdrom /mnt/cdrom
	sudo apt-get update
	sudo apt-get -y install build-essential linux-headers-`uname -r`
	sudo /mnt/cdrom/./VBoxLinuxAdditions.run
	sudo shutdown -r now
	
Share YALAS folder in the VBox manager, mount the shred folder in the VM
	
	mkdir ~/YALAS
	sudo mount -t vboxsf -o uid=1000,gid=1000  YALAS ~/YALAS
	vi /etc/fstab
	# Add line 
	# YALAS	/home/$USER/YALAS	vboxsf	defaults	0	0	
	vi /etc/modules
	# Add vboxsf
	
Install python2.7 and missing packages

	sudo apt-get install python python-pip -y
	sudo pip install -r requirements_build.txt

See Usage above	
		

# SystemTap build

```
#sudo apt-get install gawk bison flex zlib1g-dev
#git clone git://sourceware.org/git/elfutils.git
#cd elfutils
#autoreconf -i -f && ./configure --enable-maintainer-mode && make && make check
#sudo make install

sudo apt-get install texinfo gettext elfutils libdw-dev libjson0 libjson0-dev libncurses-dev
git clone git://sourceware.org/git/systemtap.git
# or https://sourceware.org/systemtap/ftp/releases/
cd systemtap
PKG_CONFIG=/usr/bin/pkg-config ./configure --prefix=<install-folder> && make && make install
```
