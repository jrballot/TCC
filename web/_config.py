
import os

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.abspath('./tmp')

DATABASE="bas_database.db"
CSRF_ENABLE=True
SECRET_KEY = 'security'


DATABASE_PATH = os.path.join(basedir, DATABASE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH


WTF_CSRF_ENABLED = True
