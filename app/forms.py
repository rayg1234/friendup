from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    	PID1 = TextField('PID', validators = [Required()])
 	Interest1 = TextField('Pick an activity', validators = [Required()])
	Interest2 = TextField('Select an interest', validators = [Required()])
	Interest3 = TextField('Select an interest', validators = [Required()])
	Interest4 = TextField('Select an interest', validators = [Required()])
    	#remember_me = BooleanField('remember_me', default = False)
