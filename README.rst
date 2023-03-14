====================
Django Dynamic Stats
====================

Contains Common modules across Django Rest projects

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "stats" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        "stats.apps.StatsConfig",
    ]

2. Include the polls URLconf in your project urls.py like this::

    url("^exports/", include("stats.exports.urls")),


3. Run ``python manage.py migrate`` to create the polls models.

4. Visit http://127.0.0.1:8000/exports/ to participate in the poll.

Contributing
-------------
1. ``python setup.py sdist``

2. ``python setup.py bdist_wheel``
