from flask import Blueprint

crud_bp = Blueprint('crud', __name__, template_folder='templates')

# Use CrudView to attach new views to your own blueprint (probably not to crud_bp)