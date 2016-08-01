import flask
from webapp.data_access import fintech_stock_query_services as fsqs
from webapp.data_access import dal

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
                                 all_sectors=fsqs.get_all_sectors())

@_pwbp.route('/q1/individual')
@_pwbp.route('/q1/individual/<int:setid>/<int:seid>/<direction>/<percent>/<int:from_yr>/<int:to_yr>')
def q1_individual(setid, seid, direction, percent, from_yr, to_yr):
    all_companies = fsqs.get_all_companies()
    selected_company = fsqs.get_company(seid)

    return flask.render_template('publicweb/q1_individual.html', title='Insight #1.1', setid=setid, seid=seid,
                                 direction=direction,
                                 percent=float(percent),from_yr=from_yr, to_yr=to_yr, min_yr=1993, max_yr=2016,
                                 # TODO: These should be get_stock_entities cos this page will handle all kinds of stock entities
                                 all_companies=all_companies,
                                 selected_company=selected_company)

@_pwbp.route('/q2/aggregate/<int:setid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_aggregate(setid, from_yr, to_yr):
    return flask.render_template('publicweb/q2_aggregate.html', setid=setid, from_yr=from_yr, to_yr=to_yr,
                                 min_yr=1993, max_yr=2016)

@_pwbp.route('/q2/aggregate/partial') # This route is specifically to satisfy jQuery Ajax calls with the url_for()
@_pwbp.route('/q2/aggregate/partial/<int:setid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_aggregate_partial(setid, from_yr, to_yr):
    return flask.render_template('publicweb/partials/q2_aggregate_partial.html',
                                 result=fsqs.get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(setid, from_yr, to_yr),
                                 from_yr=from_yr, to_yr=to_yr)

@_pwbp.route('/q2/individual/<int:setid>/<int:seid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_individual(setid, seid, from_yr, to_yr):
    return flask.render_template('publicweb/q2_individual.html', setid=setid, seid=seid, from_yr=from_yr, to_yr=to_yr,
                                 min_yr=1993, max_yr=2016,
                                 all_companies=fsqs.get_all_companies(),
                                 selected_company=fsqs.get_company(seid))

@_pwbp.route('/q2/individual/partial') # This route is specifically to satisfy jQuery Ajax calls with the url_for()
@_pwbp.route('/q2/individual/partial/<int:setid>/<int:seid>/<int:from_yr>/<int:to_yr>') #, defaults = { 'sort_order':'desc', 'top_n':10 })
def q2_individual_partial(setid, seid, from_yr, to_yr):
    return flask.render_template('publicweb/partials/q2_individual_partial.html',
                                 result=fsqs.get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(setid, seid, from_yr, to_yr))

@_pwbp.route('/q4/aggregate/<int:setid>/<int:days_before>/<int:days_after>/<string:event_date>')
def q4_aggregate(setid, days_before, days_after, event_date):
    return flask.render_template('publicweb/q4_aggregate.html',
                                 days_before=days_before, days_after=days_after, events=dal.get_all_events())

@_pwbp.route('/q4/aggregate/partial')
@_pwbp.route('/q4/aggregate/partial/<int:setid>/<int:days_before>/<int:days_after>/<string:event_date>')
def q4_aggregate_partial(setid, days_before, days_after, event_date):
    return flask.render_template('publicweb/partials/q4_aggregate_partial.html',
                                 result=fsqs.what_was_the_performance_of_stock_entities_n_days_before_and_after_a_single_day_event(
                                     set_id=setid, se_id=None, date_of_event=event_date, days_before=days_before,
                                     days_after=days_after))

@_pwbp.route('/q4/aggregate_probabilities/<int:setid>/<int:days_before>/<int:days_after>/<int:event_group_id>')
def q4_aggregate_probabilities(setid, days_before, days_after, event_group_id):
    return flask.render_template('publicweb/q4_aggregate_probabilities.html',
                                 days_before=days_before, days_after=days_after, event_groups=dal.get_all_event_groups(),
                                 selected_event_group=event_group_id)

@_pwbp.route('/q4/aggregate_probabilities/partial')
@_pwbp.route('/q4/aggregate_probabilities/partial/<int:setid>/<int:days_before>/<int:days_after>/<int:event_group_id>')
def q4_aggregate_probabilities_partial(setid, days_before, days_after, event_group_id):
    return flask.render_template('publicweb/partials/q4_aggregate_probabilities_partial.html',
                                 result=fsqs.what_is_the_effect_of_event_group_on_stock_entities(set_id=setid, se_id=None,
                                    eg_id=event_group_id, days_before=days_before, days_after=days_after))

@_pwbp.route('/testquery')
def test_query():
    return flask.render_template('publicweb/partials/macros.html')
