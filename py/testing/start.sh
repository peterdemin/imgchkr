#!/bin/sh

celery flower -A imgchkr_bg.cli &
python testing/printer.py
