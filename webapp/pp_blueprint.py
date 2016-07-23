import flask
from . import fintech_services
import json

publicweb_bp = flask.Blueprint('publicweb', __name__)

_pwbp = publicweb_bp

# @__pwbp.after_request
# def after_request(response: flask.Response):
#     response.cache_control.no_cache = True
#     return response

@_pwbp.route('/')
def index():
    return flask.render_template('publicweb/index.html')

@_pwbp.route('/questions/all')
def all_questions():
    return flask.render_template('publicweb/questions_home.html')

@_pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>', defaults = {'sort_order': 'desc', 'top_n':10})
@_pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>', defaults = {'top_n':10})
@_pwbp.route('/q1/aggregate/<int:setid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>/<sort_order>/<top_n>')
def q1_aggregate(setid, direction, percent, from_yr, to_yr, sort_order, top_n):
    return flask.render_template('publicweb/q1_aggregate.html', title='Insight #1', setid=setid, direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 sort_order=sort_order, top_n=top_n,
                                 all_sectors=fintech_services.get_all_sectors())

@_pwbp.route('/q1/individual')
@_pwbp.route('/q1/individual/<int:setid>/<int:seid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>')
def q1_individual(setid, seid, direction, percent, from_yr, to_yr):
    return flask.render_template('publicweb/q1_individual.html', title='Insight #1.1', setid=setid, seid=seid,
                                 direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 # TODO: These should be get_stock_entities cos this page will handle all kinds of stock entities
                                 all_companies=fintech_services.get_all_companies(),
                                 selected_company=fintech_services.get_company(seid))

@_pwbp.route('/q2/aggregate/<int:setid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_aggregate(setid, from_yr, to_yr):
    return flask.render_template('publicweb/q2_aggregate.html', setid=setid, from_yr=from_yr, to_yr=to_yr,
                                 min_yr=1993, max_yr=2016)

@_pwbp.route('/q2/aggregate/partial') # This route is specifically to satisfy jQuery Ajax calls with the url_for()
@_pwbp.route('/q2/aggregate/partial/<int:setid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_aggregate_partial(setid, from_yr, to_yr):
    return flask.render_template('publicweb/partials/q2_aggregate_partial.html',
                                 result=fintech_services.get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(setid, from_yr, to_yr),
                                 from_yr=from_yr, to_yr=to_yr)

@_pwbp.route('/q2/individual/<int:setid>/<int:seid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_individual(setid, seid, from_yr, to_yr):
    return flask.render_template('publicweb/q2_individual.html', setid=setid, seid=seid, from_yr=from_yr, to_yr=to_yr,
                                 min_yr=1993, max_yr=2016,
                                 all_companies=fintech_services.get_all_companies(),
                                 selected_company=fintech_services.get_company(seid))

@_pwbp.route('/q2/individual/partial') # This route is specifically to satisfy jQuery Ajax calls with the url_for()
@_pwbp.route('/q2/individual/partial/<int:setid>/<int:seid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_individual_partial(setid, seid, from_yr, to_yr):
    return flask.render_template('publicweb/partials/q2_individual_partial.html',
                                 result=fintech_services.get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(setid, seid, from_yr, to_yr))

@_pwbp.route('/testquery')
def test_query():
    return flask.render_template('publicweb/partials/macros.html')
