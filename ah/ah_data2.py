import pandas as pd
import datetime
from selenium import webdriver
import time
import sqlite3



def scrape_ah(ah_webpages, df_total):
    for page, category in ah_webpages:
        product = []
        size = []
        price_frac = []
        price_int = []
        discount = []
        print(page)
        driver = webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver')
        driver.get(page)

        # wait = WebDriverWait(driver, 20)
        time.sleep(5)

        child_tags = driver.find_elements_by_xpath(".//*[@class=' row collapse product__content product__content--link']")

        for i in range(len(child_tags)):
            product.append(child_tags[i].find_element_by_xpath(".//*[@class='product-description__title  -multiline']").text)
            size.append(child_tags[i].find_element_by_xpath(".//*[@class='product-description__unit-size -multiline']").text)
            price_frac.append(child_tags[i].find_element_by_xpath(".//*[@class='price__fractional']").text)
            price_int.append(child_tags[i].find_element_by_xpath(".//*[@class='price__integer']").text)
            try:
                discount.append(child_tags[i].find_element_by_xpath(".//*[@class='discount-block']").text)
            except:
                discount.append(0)

        df = pd.DataFrame({'product': product, 'size': size, 'price_frac': price_frac, 'price_int': price_int, 'discount': discount})
        time.sleep(2)
        driver.close()

        df['price'] = (df['price_int'] + '.' + df['price_frac']).astype('float')
        df = df.drop(['price_frac', 'price_int'], axis=1)
        df['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        df['category'] = category

        df_total = pd.concat([df_total, df], sort=True)
    return df_total.drop_duplicates()



def to_db(DF_AH):
    sqlite_file = '/Users/wcasey/Documents/personal_projects/projects/ah/ah.db'
    conn = sqlite3.connect(sqlite_file)
    DF_AH.to_sql(name='ah_inventory', con=conn, if_exists='append', index=False)

    #commit changes to the db and close the connection
    conn.commit()
    conn.close()



def main():
    df_total = pd.DataFrame({'product': [], 'size': [], 'price': [], 'date': [],'discount': [] , 'category': []})
    ah_webpages = [
              ('https://www.ah.nl/producten/aardappel-groente-fruit', 'produce'),
              ('https://www.ah.nl/producten/vlees-kip-vis-vega', 'meats'),
              ('https://www.ah.nl/producten/kaas-vleeswaren-delicatessen', 'deli-cheese'),
              ('https://www.ah.nl/producten/zuivel-eieren', 'dairy-eggs'),
              ('https://www.ah.nl/producten/frisdrank-sappen-koffie-thee','drinks-coffee-tea' ),
              ('https://www.ah.nl/producten/drogisterij-baby', 'drugstore-baby')
              ]

    DF_AH = scrape_ah(ah_webpages, df_total)
    to_db(DF_AH)
    #return DF_AH


if __name__ == '__main__':
    main()

