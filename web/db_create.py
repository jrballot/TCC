from views import db
from models import User
from datetime import date

db.create_all()
db.session.commit()
