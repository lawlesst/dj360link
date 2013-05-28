#360Link demo

This is a basic [Django application](http://damp-tor-3124.herokuapp.com/).  It serves as a basic library OpenURL resolver using the 360Link API from Serials Solutions.

See [Django, Heroku, and the 360Link API](http://lawlesst.github.com/notebook/heroku360link.html) for a more complete description of this app and more information on how to get started. 

To install use pip.  Virtualenv is recommended.   
~~~~
$ git clone git://github.com/lawlesst/dj360link.git
$ cd dj360link
$ pip install -r requirements
$ export SERSOL_KEY=yoursersolkey
$ python manage.py syncdb
$ python manage.py runserver 0.0.0.0:8000
~~~~
point your browser at http://localhost:8000

This app could run on Heroku with minimal addittional setup.  See Heroku's [getting started guide](https://devcenter.heroku.com/articles/django) for more information. 
