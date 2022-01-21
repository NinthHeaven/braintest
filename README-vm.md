# Virtual machine install

The virtual machine is not able to download over http or https, so the repository must be updated manually, and the python packages must be downloaded and transferd.

This assumes you are on a machine that is able to access the VM, and that `braintest` stands in for the address ssh needs to reach the VM.

## 1. Local machine

Create a zip of the archive. From the directory of the git repository, run

```
git push ssh://braintest/srv/braincheck/braintest/.git
```

## 2. Local machine

Then, to get the python packages:

```
mkdir -p packages
pip3 download -d packages/ -r requirements.txt --platform linux_x86_64 --python-version 38 --no-deps
rsync -aiv packages braintest:/srv/braincheck/braintest
```

## 4. Virtual machine

```
cd braintest/
docker build --tag braintest -f Dockerfile-vm .
docker run -d --rm -v /srv/braincheck/braintest_db/usernames.db:/app/usernames.db --name braintest -p 80:5000 braintest
```

The option `-v /srv/braincheck/braintest_db/usernames.db:/app/usernames.db` ensures that database changes are saved outside the container so that when it is restarted or rebuilt, the database persists.
