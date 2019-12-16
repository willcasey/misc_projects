import pandas as pd
import datetime
from selenium import webdriver
import time
import sqlite3



def scrape_ah(ah_webpages, df_total):
    for page, category in ah_webpages:
        print(page)
        driver = webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver')
        driver.get(page)

        # wait = WebDriverWait(driver, 20)
        time.sleep(5)
        # 'discount': [x.text for x in driver.find_elements_by_xpath(".//*[@class='discount-block']")]

        df = pd.DataFrame({'product': [x.text for x in driver.find_elements_by_xpath(".//*[@class='product-description__title  -multiline']") ],
                           'size': [x.text for x in driver.find_elements_by_xpath(".//*[@class='product-description__unit-size -multiline']")],
                           'price_int': [x.text for x in driver.find_elements_by_xpath(".//*[@class='price__integer']")],
                           'price_frac': [x.text for x in driver.find_elements_by_xpath(".//*[@class='price__fractional']")]

                          })

        driver.close()

        df['price'] = (df['price_int'] + '.' + df['price_frac']).astype('float')
        df = df.drop(['price_frac', 'price_int'], axis=1)
        df['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        df['category'] = category

        df_total = pd.concat([df_total, df])
    return df_total



def to_db(df_ah):
    sqlite_file = '/Users/wcasey/ah.db'
    conn = sqlite3.connect(sqlite_file)
#     c = conn.cursor()
    df_ah.to_sql(name='ah_daily_import', con=conn, if_exists='append', index=False)

    #commit changes to the db and close the connection
    conn.commit()
    conn.close()




def main():
    df_total = pd.DataFrame({'product': [], 'size': [], 'price': [], 'date': [], 'category': []})
    ah_webpages = [
              ('https://www.ah.nl/producten/aardappel-groente-fruit', 'produce'),
              ('https://www.ah.nl/producten/vlees-kip-vis-vega', 'meats'),
              ('https://www.ah.nl/producten/kaas-vleeswaren-delicatessen', 'deli-cheese'),
              ('https://www.ah.nl/producten/zuivel-eieren', 'dairy-eggs'),
              ('https://www.ah.nl/producten/frisdrank-sappen-koffie-thee','drinks-coffee-tea' ),
              ('https://www.ah.nl/producten/drogisterij-baby', 'drugstore-baby')
              ]

    df_ah = scrape_ah(ah_webpages, df_total)
    to_db(df_ah)
    return df_ah


if __name__ == '__main__':
    main()
