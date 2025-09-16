#!/bin/bash

if [ -z "$1" ]; then
  echo "Ошибка: директория не указана."
  exit 1
fi

if [ ! -d "$1" ]; then
  echo "Ошибка: директория '$1' не существует."
  exit 1
fi

ls -lt "$1"
