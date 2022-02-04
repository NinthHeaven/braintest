# Virtual machine install



```
git clone https://github.com/NinthHeaven/braintest.git
cd braintest/
docker build --tag braintest -f Dockerfile-vm .
docker run -d --rm -v /srv/braincheck/braintest_db/usernames.db:/app/usernames.db --name braintest -p 80:5000 braintest
```

The option `-v /srv/braincheck/braintest_db/usernames.db:/app/usernames.db` ensures that database changes are saved outside the container so that when it is restarted or rebuilt, the database persists.
