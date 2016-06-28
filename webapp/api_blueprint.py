import flask
from . import fintech_services

api_bp = flask.Blueprint('api', __name__, url_prefix="/api")

__api = api_bp

@__api.route('/q1/aggregate/<int:setid>/<direction>/<float:percent>/<int:from_yr>/<int:to_yr>/<sort_order>')
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order):
    pass

@__api.route("/test")
def testapi():
    return flask.jsonify(fintech_services.get_all_sectors())