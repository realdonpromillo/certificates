from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Certificate

# Eigenentwicklung
class CSRForm(FlaskForm):
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=2)], default='CH')
    # Dropdown-Liste für die Auswahl des Kantons
    state = SelectField('State', validators=[DataRequired()], default = 'Bern',choices = [
        ('Aargau', 'Aargau'),
        ('Appenzell Ausserrhoden', 'Appenzell Ausserrhoden'),
        ('Appenzell Innerrhoden', 'Appenzell Innerrhoden'),
        ('Basel-Landschaft', 'Basel-Landschaft'),
        ('Basel-Stadt', 'Basel-Stadt'),
        ('Bern', 'Bern'),
        ('Fribourg', 'Fribourg'),
        ('Geneva', 'Geneva'),
        ('Glarus', 'Glarus'),
        ('Graubünden', 'Graubünden'),
        ('Jura', 'Jura'),
        ('Luzern', 'Luzern'),
        ('Neuchâtel', 'Neuchâtel'),
        ('Nidwalden', 'Nidwalden'),
        ('Obwalden', 'Obwalden'),
        ('Schaffhausen', 'Schaffhausen'),
        ('Schwyz', 'Schwyz'),
        ('Solothurn', 'Solothurn'),
        ('St. Gallen', 'St. Gallen'),
        ('Ticino', 'Ticino'),
        ('Uri', 'Uri'),
        ('Valais', 'Valais'),
        ('Vaud', 'Vaud'),
        ('Zug', 'Zug'),
        ('Zürich', 'Zürich'),
    ] )
    # Dropdown-Liste für die Auswahl des Kantons
    locality = SelectField('Locality', validators=[DataRequired()], default = 'Bern',choices = [
        ('Aargau', 'Aargau'),
        ('Appenzell Ausserrhoden', 'Appenzell Ausserrhoden'),
        ('Appenzell Innerrhoden', 'Appenzell Innerrhoden'),
        ('Basel-Landschaft', 'Basel-Landschaft'),
        ('Basel-Stadt', 'Basel-Stadt'),
        ('Bern', 'Bern'),
        ('Fribourg', 'Fribourg'),
        ('Geneva', 'Geneva'),
        ('Glarus', 'Glarus'),
        ('Graubünden', 'Graubünden'),
        ('Jura', 'Jura'),
        ('Luzern', 'Luzern'),
        ('Neuchâtel', 'Neuchâtel'),
        ('Nidwalden', 'Nidwalden'),
        ('Obwalden', 'Obwalden'),
        ('Schaffhausen', 'Schaffhausen'),
        ('Schwyz', 'Schwyz'),
        ('Solothurn', 'Solothurn'),
        ('St. Gallen', 'St. Gallen'),
        ('Ticino', 'Ticino'),
        ('Uri', 'Uri'),
        ('Valais', 'Valais'),
        ('Vaud', 'Vaud'),
        ('Zug', 'Zug'),
        ('Zürich', 'Zürich'),
    ] )
    organization = StringField('Organization', validators=[DataRequired(), Length(max=64)])
    organizational_unit = StringField('Organizational Unit', validators=[Length(max=64)])
    common_name = StringField('Common Name', validators=[DataRequired(), Length(max=64)])
    subject_alternative_name = StringField('Subject Alternative Name')
    submit = SubmitField('Generate CSR')

# Eigenentwicklung
class CertForm(FlaskForm):
    common_name = StringField('Common Name', validators=[DataRequired()])
    certificate = TextAreaField('Signed Certificate (-----BEGIN CERTIFICATE-----)', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password'), Length(min=8, max=128)])
    submit = SubmitField('Generate PFX')

# Übernommen aus den Beispielen von Miguel Grinberg
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4, max=120)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

# Eigenentwicklung
class ConvertCertificateForm(FlaskForm):
    private_key = TextAreaField('Private Key (-----BEGIN PRIVATE KEY-----)', validators=[DataRequired()])
    public_key = TextAreaField('Signed Certificate (-----BEGIN CERTIFICATE-----)', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password'), Length(min=8, max=128)])
    submit = SubmitField('Convert to PFX')