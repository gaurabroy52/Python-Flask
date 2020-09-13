import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or b'Zw\x93_\x83\x81\xcf\x1a\xd0\xff\xd6\xea\xc3\xac\xa1 '

    MONGODB_SETTINGS = { 'db' : 'UTA_Enrollment' }