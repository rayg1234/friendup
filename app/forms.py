from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    	PID1 = TextField('PID', validators = [Required()])
 	Interest1 = TextField('Interest', validators = [Required()])
    	remember_me = BooleanField('remember_me', default = False)
