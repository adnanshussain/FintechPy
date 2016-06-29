import flask
from . import fintech_services

api_bp = flask.Blueprint('api', __name__, url_prefix="/api")

__api = api_bp

@__api.route('/q1/aggregate') # TODO: Only used for url_for in the makeChart JS, need to fix an alternative
@__api.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>/<top_n>')
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order, top_n):
    return flask.jsonify(fintech_services.
                         get_number_of_times_stockentities_that_were_upordown_bypercent_in_year_range(setid, direction,
                                                                                                      float(percent),
                                                                                                      from_yr, to_yr,
                                                                                                      sort_order, top_n))

@__api.route("/test")
def testapi():
    # resp = flask.Response()
    resp = flask.jsonify(fintech_services.get_number_of_times_stockentities_that_were_upordown_bypercent_in_year_range(1, 10, 1993, 2016))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
