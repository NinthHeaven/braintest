# braintest  installment instructions 

After cloning the repository, type into the terminal:
```
  cd braintest 
```

After you are in the braincheck directory, create a virtual environment in the terminal and activate it
```
  # This will create the virtual environment (/venv) directory
  python -m venv venv
  
  # If you are on Windows, type this into terminal
  source venv/Scripts/activate
  
  (type venv\Scripts\activate.bat if that doesn't work)
  
  # If you are on Mac, type this instead
  source venv/bin/activate
  
```
Once the virtual environment is running (you will see (venv) in the terminal if it is), install the required modules by typing
```
  pip install -r requirements.txt
```

Finally, to run the app just input
```
  flask run
```
  
  
# braintest docker instructions

First, make sure you put png files in the `png` directory in the root of the braintest repository. The Dockerfile copies these in and then moves them to the correct place in the application.

For example:

```
  mkdir /path/to/braintest/png
  cp /path/to/my_png_folder/* /path/to/braintest/png/
```

Next, to build, run:

```
  docker build --tag braintest .
```

To run the docker container:

```
  docker run --rm -p 5000:5000 braintest
```

Then navigate to 127.0.0.1:5000 in a browser. C'est viola.

