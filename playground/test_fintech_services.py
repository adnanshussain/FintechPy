import webapp.fintech_services as fs
import webapp.fintech_stock_query_services as fqs

result1 = fs.get_number_of_times_stockentities_that_were_upordown_bypercent_in_year_range(5, 'above', 10, 2010, 2015)

for r in result1['main_data']:
    print(r)

print('=======================================')

result2 = fqs.get_the_number_of_times_stockentities_were_upordown_bypercent_in_year_range(2, 'above', 10, 2010, 2015)

for r in result2['main_data']:
    print(r)

