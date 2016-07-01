import flask
from . import fintech_services
import json

publicweb_bp = flask.Blueprint('publicweb', __name__)

__pwbp = publicweb_bp

# @__pwbp.after_request
# def after_request(response: flask.Response):
#     response.cache_control.no_cache = True
#     return response

@__pwbp.route('/')
def index():
    return flask.render_template('publicweb/index.html')

@__pwbp.route('/questions/all')
def all_questions():
    return flask.render_template('publicweb/questions_home.html')

@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>', defaults = { 'sort_order':'desc', 'top_n':10 })
@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>', defaults = { 'top_n':10 })
@__pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>/<top_n>')
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order, top_n):
    return flask.render_template('publicweb/q1_aggregate.html', title='Insight #1', setid=setid, direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 sort_order=sort_order, top_n=top_n,
                                 all_sectors=fintech_services.get_all_sectors())

@__pwbp.route('/q1/individual')
@__pwbp.route('/q1/individual/<int:setid>/<int:seid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>')
def q1_individual(setid, seid, direction, percent, from_yr, to_yr):
    return flask.render_template('publicweb/q1_individual.html', title='Insight #1.1', setid=setid, seid=seid,
                                 direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 # TODO: These should be get_stock_entities cos this page will handle all kinds of
                                        # stock entities
                                 all_companies=fintech_services.get_all_companies(),
                                 selected_company=fintech_services.get_company(seid))

@__pwbp.route('/testquery')
def test_query():
    return flask.render_template('testquery.html')
