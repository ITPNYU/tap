import sys

activate_this = '/var/www/dev/tap/venv/tap-v1/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, '/var/www/dev/tap/tap')

from tap import app as application
