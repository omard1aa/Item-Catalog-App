#!/usr/bin/python

import sys
sys.stdout = sys.stderr

sys.path.insert(0,"/var/www/Item-Catalog-App")

from app import app as application

