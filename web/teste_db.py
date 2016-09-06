from views import db
from models import User, Model
from datetime import date

model = db.session.query(Model).filter_by(id=2).first()

print model.initial_date.year
print "0"+str(model.initial_date.month)
print "0"+str(model.initial_date.day)
