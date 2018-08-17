#!/usr/bin/env bash
rm -rf /var/tmp/django_cache
cd butterbot
celery flower -A butterbot --address=127.0.0.1 --port=5555
sleep 3
cd butterbot
celery flower -A butterbot --broker=amqp://guest:guest@localhost:5672//
sleep 3
cd butterbot
celery -A butterbot beat
sleep 1
cd butterbot
celery -A butterbot worker -l info
cd butterbot
celery -A butterbot control shutdown

