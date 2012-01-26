import os
import sys

DEBUG = True

try:
    if 'DATABASE_URL' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
except:
    print "Unexpected error:", sys.exc_info()