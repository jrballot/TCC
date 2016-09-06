from views import db
from models import User, Model
from datetime import date

db.create_all()
db.session.commit()
