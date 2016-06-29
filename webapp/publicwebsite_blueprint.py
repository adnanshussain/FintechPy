import flask
from . import fintech_services
import json

publicweb_bp = flask.Blueprint('publicweb', __name__)

__pwbp = publicweb_bp

@__pwbp.route('/')
def index():
    return flask.render_template('publicweb/index.html', result=fintech_services.get_all_stock_entity_types())

@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>', defaults = { 'sort_order':'desc', 'top_n':10 })
@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>', defaults = { 'top_n':10 })
@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>/<top_n>')
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order, top_n):
    return flask.render_template('publicweb/q1_aggregate.html', title='Insight #1', setid=setid, direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 sort_order=sort_order, top_n=top_n,
                                 all_sectors=fintech_services.get_all_sectors())

@__pwbp.route('/testquery')
def test_query():
    return flask.render_template('testquery.html')