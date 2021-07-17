#!/bin/sh
export FLASK_APP=avito_clone.py && export ELASTICSEARCH_URL=http://localhost:9200 && FLASK_ENV=development && flask run