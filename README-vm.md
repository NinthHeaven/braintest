# Virtual machine install

The virtual machine is not able to download over http or https, so the repository must be updated manually, and the python packages must be downloaded and transferd.

This assumes you are on a machine that is able to access the VM, and that `braintest` stands in for the address ssh needs to reach the VM.

## 1. Local machine

Create a zip of the archive. From the directory of the git repository, run

```
git archive --format zip --output ../braintest.zip main
rsync -aiv ../braintest.zip braintest:/srv/braincheck/braintest-main
```

## 2. Virtual machine

On the VM run:

```
cd /srv/braincheck
mv braintest-main/png ./
rm -rf braintest-main
unzip braintest.zip
mv png braintest-main/
```

## 3. Local machine

Then, to get the python packages:

```
mkdir -p packages
pip3 download -d packages/ -r requirements.txt --platform linux_x86_64 --python-version 38 --no-deps
rsync -aiv packages braintest:/srv/braincheck/braintest-main
```

## 4. Virtual machine

```
cd braintest-main/
docker build --tag braintest - < Dockerfile-vm
docker run -d --rm --name braintest -p 80:5000 braintest
```

