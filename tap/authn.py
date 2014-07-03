from flask_login import current_user, login_user
from flask_restless import ProcessingException
from hashlib import sha256
from sqlalchemy.orm.exc import NoResultFound
from tap.config import config
from tap.database import db_session
from tap.models import User

def hash_pass(password):
    salted_password = password + config.get('secrets', 'SECRET')
    return sha256(salted_password).hexdigest()

def verify_pass(password):
    if hash_pass(password) == current_user.password:
        return True
    else:
        return False

# POST preprocessor for session
def create_session(data=None, **kw):
    if data is not None:
        hashed_pass = hash_pass(data['password'])
        try:
            user = db_session.query(User).filter(User.username==data['username']).filter(User.password==hashed_pass).one()
            data['user_id'] = user.id
            del data['username']
            del data['password']
        except NoResultFound:
            pass

# POST postprocessor for session
def perform_login(result=None, **kw):
    if result is not None:
        try:
            user = db_session.query(User).filter(User.username==result['user']['username']).one()
            login_user(user, remember=True)
            print('ran login_user')
        except NoResultFound:
            pass

# preprocessor for any API call that requires authentication
def authn_func(*args, **kw):
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not authenticated', code=401)
    return True

