# Virtual machine install

The virtual machine is not able to download over http or https, so the repository must be updated manually, and the python packages must be downloaded and transferd.

From a machine that is able to access the VM, run:

```
mkdir -p packages
pip3 download -d packages/ -r requirements.txt --platform linux_x86_64 --python-version 38 --no-deps
rsync -aiv packages braintest:/srv/braincheck/braintest-main
```

Then on the VM, build the docker image using the Dockerfile-vm

Download the zip from github and get it to `/srv/braincheck/braintest.zip`

```
cd /srv/braincheck
mv braintest-main/png ./
rm -rf braintest-main
unzip braintest.zip
mv png braintest-main/
cd braintest-main/
docker build --tag braintest - < Dockerfile-vm
docker run -d --rm --name braintest -p 80:5000 braintest
```

