#!/bin/bash

if [[ "${1}" == "celery"  ]]; then
  celery --app=src.tasks.tasks:celery_app worker -l INFO
elif [[ "${1}" == "flower"  ]]; then
  celery --app=src.tasks.tasks:celery_app flower
  fi
