import time
import requests
from bs4 import BeautifulSoup

# with open(r'tadawul_events\lora.txt', mode='a') as f:
#     f.writelines(['yeah baby', '\n'])
# exit()

# while True:
#     print('lala land')
#     time.sleep(2)
# exit()


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

# r = requests.get('http://beta.haystaxs.org:9980', headers=headers)
# print(r.text)
# exit()

stock_symbol = 7010


def fetch_all_events(stock_symbol, max_pg_no):
    for pg in range(1, max_pg_no + 1):
        url_en = 'https://www.tadawul.com.sa/wps/portal/tadawul/markets/Press-Release/news-%26-announcements/!ut/p/z1/pZLPc6IwFMf_lh441rwAKrs3ihYQZGuRVrh0gqbIDCRMjLbuX78B7EzrtvXQTC7vvc_3_UpQhlYoY-RQFkSWnJFK2Wk2eoq80PHA0gNYTgHs-Z_Z7f1whq0Q0GMH6Lpj4V8mhBCOMdgjF_zF3DRgYaDsvd6dLg0Vnsyd-8jXAf7Tu340Bnthew-3Dwq19J_pwfyov9j_md41LuuzM8TTJ6rFaRBMnKEON8MT8N2KPgKf7OBboB2yA-CLY8MJ8O9cE_uqSWs5ugE7ccJoEsUYhqMLJdQeZigrKp73f2IrZfNbAw0k2ZCXfaWpCmteN4Qd42OdcwWNAUOL2iw3rAJlgj5TQcVgL1Sw1e-6BDUpq0HBeVHRgcrQOzTYa6CCn-m3fCfR6kyGUvWM43fzRYH6J1McgOnNMZgmShgXtWr-8VDSFxS3826IpHdUlHyD0mvcehpS0IijtDMkfZUxJWK9VdmVTRjj-3VNmVweG6qgJ2y1_l3HnHxveQVhBe11u34habeQjl9LLvy-aEwZauokSVZQ-qV_neVHozrUTv6Xvt3nwr66-gf9P7M0/p0/IZ7_IPG41I82K8NK30AE1K04HM1044=CZ6_NHLCH082K0TE00AMOJFR5J18L0=M/?searchType=1&pageNo={pg_no}&annoucmentType=1_-1&sectorId=-1&symbol={stock_symbol}&daterange=&datePeriod=-1&textSearch=&findButton='. \
            format(pg_no=pg, stock_symbol=stock_symbol)
        url_ar = 'https://www.tadawul.com.sa/wps/portal/tadawul/markets/Press-Release/news-%26-announcements/!ut/p/z1/pZJdc6IwFIZ_y15wWXMCqOzeIVpAkK1FWuWmEzRFZiBhYrB1f_0GcGZb--HFZnJzznne85WgFK1RysixyIksOCOlsjfp6CnyQscDSw9gNQOwF7_nt_fDObZCQI8doOuOhX-aEEI4xmCPXPCXC9OApYHSt3p3tjJUeLpw7iNfB_igd_1oDPbS9h5uHxRq6f-nB_O9_mr_F3rXuK5PLxBPn6oWZ0EwdYY6TIZn4LsVvQc-2cG3QDtkB8AXx4Yz4N-5JvZVk9ZqNAE7ccJoGsUYhqMrJdQe5ijNS571f2IvZf1LAw0k2ZGXptRUhS2vasJO8anKuILGgKFFbZYZVo5SQZ-poGLQCBVs9YcuQUWKcpBznpd0oDL0Dg0aDVTwM_2eHyRaX8jQRj3j-M18UaD-yQwHYHoLDKaJEsZFpZp_PBb0BcXtvDXJacTRBnf72xFJBWE5VbmUeejH2HRjKPu5YLtJIyVn5zjdSi78Hdrc4N4mYrtfnWql7xyEMd5sK8rk2fnUg5K-yriD-0Rt3TsqCt6niolAdZUkyRoKv_Bv0uxklMfKyf7Qf9eyf_wFVxRGFQ!!/p0/IZ7_IPG41I82K8NK30AE1K04HM1044=CZ6_NHLCH082K0TE00AMOJFR5J18L0=M/?searchType=1&pageNo={pg_no}&annoucmentType=1_-1&sectorId=-1&symbol={stock_symbol}&daterange=&datePeriod=-1&textSearch=&findButton='. \
            format(pg_no=pg, stock_symbol=stock_symbol)

        response = requests.get(url_ar, headers=headers)
        file_name_ar = 'tadawul_events\\all_{stock_symbol}_events_ar_pg_{pg_no}.html'.format(stock_symbol=stock_symbol,
                                                                                             pg_no=pg)
        with open(file_name_ar, mode='w', encoding='utf8') as f:
            f.write(response.text)

        response = requests.get(url_en, headers=headers)
        file_name_en = 'tadawul_events\\all_{stock_symbol}_events_en_pg_{pg_no}.html'.format(stock_symbol=stock_symbol,
                                                                                             pg_no=pg)
        with open(file_name_en, mode='w', encoding='utf8') as f:
            f.write(response.text)

        print('Fetched page ', pg)
        time.sleep(2)

def write_csv_for(stock_symbol, max_pg_no):
    csv_file_name = 'tadawul_events\\all_{stock_symbol}_events.csv'.format(stock_symbol=stock_symbol)

    for pg in range(1, max_pg_no + 1):
        file_name_ar = 'tadawul_events\\all_{stock_symbol}_events_ar_pg_{pg_no}.html'.format(stock_symbol=stock_symbol,
                                                                                             pg_no=pg)
        with open(file_name_ar, mode='r', encoding='utf8') as f:
            html_ar = f.read()

        file_name_ar = 'tadawul_events\\all_{stock_symbol}_events_en_pg_{pg_no}.html'.format(stock_symbol=stock_symbol,
                                                                                             pg_no=pg)
        with open(file_name_ar, mode='r', encoding='utf8') as f:
            html_en = f.read()

        soup_ar = BeautifulSoup(html_ar, "html.parser")
        all_events_anchors_ar = soup_ar.find_all('a', 'news_box hvr-shutter-out-vertical')

        soup_en = BeautifulSoup(html_en, "html.parser")
        all_events_anchors_en = soup_en.find_all('a', 'news_box hvr-shutter-out-vertical')

        with open(csv_file_name, mode='a', encoding='utf8') as csvf:
            for i, (a_ar, a_en) in enumerate(zip(all_events_anchors_ar,
                                                 all_events_anchors_en)):
                date_time_components = a_ar.span.find('span', 'time_stamp').get_text(strip=True).replace('\xa0', '').split(' ')
                if len(date_time_components) == 3:
                    date_index = 1
                    time_index = 2
                else:
                    date_index = 0
                    time_index = 1

                csvf.writelines([
                    date_time_components[date_index], ',',
                    date_time_components[time_index], ',',
                    a_ar.contents[3].get_text(strip=True).replace('\n', ' ').replace(',', ';'), ',',
                    # a_en.span.find('span', 'time_stamp').get_text(strip=True), ',',
                    a_en.contents[3].get_text(strip=True).replace('\n', ' ').replace(',', ';'), ',',
                    '\n'])

# fetch_all_events(stock_symbol, 14)
write_csv_for(stock_symbol, 14)
