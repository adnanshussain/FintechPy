import webapp.fintech_services as fs
import webapp.fintech_stock_query_services as fqs

# result1 = fs.get_number_of_times_stockentities_that_were_upordown_bypercent_in_year_range(5, 'above', 10, 2010, 2015)
#
# for r in result1['main_data']:
#     print(r)
#
# print('=======================================')
#
# result2 = fqs.get_the_number_of_times_stockentities_were_upordown_bypercent_in_year_range(2, 'above', 10, 2010, 2015)
#
# for r in result2['main_data']:
#     print(r)

# result1  = fs.get_number_of_times_a_single_stockentity_was_upordown_bypercent_in_year_range(1, 77, 'above', 5, 2010, 2015)
#
# for r in result1['main_data']:
#     print(r)
#
# print('=======================================')
#
# result2 = fqs.get_the_number_of_times_a_single_stockentity_was_upordown_bypercent_in_year_range(1, 46, 'above', 5, 2010, 2015)
#
# print(result2['name_en'], result2['name_ar'])
#
# for r in result2['main_data']:
#     print(r)

# res1 = fs.get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(1, 2010, 2012)
#
# for r in res1['main_data']:
#     print(r)
#
# print('=======================================')
#
# res2 = fqs.get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(1, 2010, 2012)
#
# for r in res2['main_data']:
#     print(r)

res1 = fs.get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(1, 77, 2010, 2012)

for r in res1['main_data']:
    print(r)

print('=======================================')

res2 = fqs.get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(1, 46, 2010, 2012)

for r in res2['main_data']:
    print(r)