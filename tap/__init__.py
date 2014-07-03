from flask import Flask
from flask_login import LoginManager
from flask_restless import APIManager, ProcessingException
from tap.authn import authn_func, create_session, current_user, perform_login
from tap.config import config
from tap.database import Base, db_session, engine
from tap.models import Association, Opportunity, Provider, Session, User

app = Flask(__name__)
app.secret_key = config.get('secrets', 'SECRET')
#app.config['SERVER_NAME'] = 'localhost:5000'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong' # or 'basic'

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

# Flask-Restless API endpoints
manager = APIManager(app, session=db_session,
                     preprocessors=dict(DELETE=[authn_func],
                                        GET_SINGLE=[authn_func], GET_MANY=[authn_func],
                                        PATCH=[authn_func]))
opportunity_blueprint = manager.create_api(Opportunity,
                                           methods=['GET', 'DELETE', 'PATCH', 'POST'],
                                           collection_name='opportunity',
                                           url_prefix='/v1',
                                           max_results_per_page=300,
                                           preprocessors=dict(POST=[authn_func]))
provider_blueprint = manager.create_api(Provider,
                                        methods=['GET', 'DELETE', 'PATCH', 'POST'],
                                        collection_name='provider',
                                        url_prefix='/v1',
                                        max_results_per_page=300,
                                        preprocessors=dict(POST=[authn_func]))
session_blueprint = manager.create_api(Session, methods=['POST'],
                                       collection_name='session',
                                       url_prefix='/v1',
                                       preprocessors=dict(POST=[create_session]),
                                       postprocessors=dict(POST=[perform_login]))
user_blueprint = manager.create_api(User,
                                    methods=['GET', 'PATCH', 'POST'],
                                    collection_name='user',
                                    url_prefix='/v1',
                                    max_results_per_page=300,
                                    preprocessors=dict(POST=[authn_func]))

# Allow API to be accessed from anywhere
def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

app.after_request(add_cors_header)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
