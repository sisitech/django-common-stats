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


3. Run ``python manage.py migrate`` to create the stats models.




