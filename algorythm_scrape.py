import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import statistics

def wait_for_non_empty_text(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(*locator).text.strip(),
        f"Element with locator {locator} did not have non-empty text after {timeout} seconds"
    )

def get_card_name(driver):
    try:
        card_name = wait_for_non_empty_text(driver, (By.CSS_SELECTOR, 'h1.product-details__name'))
    except TimeoutException:
        card_name = "NA"
    return card_name

def get_listings_info(driver):
    listings_info = []

    try:
        prices = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.listing-item__listing-data__info__price')))
        stocks = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.add-to-cart__available')))
        stocks = stocks[1:]
        sellers = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.listing-item__listing-data__seller .seller-info__name')))
        sales = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.listing-item__listing-data__seller .seller-info__sales')))
        seller_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.listing-item__listing-data__seller')))

        for price, stock, seller, sale, seller_div in zip(prices, stocks, sellers, sales, seller_divs):
            shipping_cost = "0"
            try:
                shipping_cost_element = price.find_element(By.XPATH, "..").find_element(By.CSS_SELECTOR, '.shipping-messages__price')
                shipping_cost = shipping_cost_element.text.strip('+ ').strip(' Shipping').replace('$', '').strip()
            except NoSuchElementException:
                pass

            direct_seller = "no"
            try:
                direct_seller_element = seller_div.find_element(By.CSS_SELECTOR, 'a[title="Direct Seller"]')
                if direct_seller_element:
                    direct_seller = "yes"
            except NoSuchElementException:
                pass

            listings_info.append({
                'Price': price.text.replace('$', '').replace(',', '').strip(),
                'Stock': stock.text.strip(' of'),
                'Shipping Cost': shipping_cost,
                'Seller': seller.text,
                'Sales': sale.text.strip(' ()'),
                'Direct': direct_seller
            })

        if not listings_info:
            listings_info.append({
                'Price': "NA",
                'Stock': "NA",
                'Shipping Cost': "NA",
                'Seller': "NA",
                'Sales': "NA",
                'Direct': "NA"
            })

    except TimeoutException:
        listings_info.append({
            'Price': "NA",
            'Stock': "NA",
            'Shipping Cost': "NA",
            'Seller': "NA",
            'Sales': "NA",
            'Direct': "NA"
        })

    return listings_info

def get_spotlight_price(driver):
    try:
        price_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.spotlight__price')))
        price = price_element.text.strip().replace('$', '').replace(',', '').strip()
    except TimeoutException:
        price = "NA"
    return price

def get_spotlight_stock(driver):
    try:
        stock_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.add-to-cart__available')))
        stock = stock_element.text.strip().split()[-1]
    except TimeoutException:
        stock = "NA"
    return stock

def is_spotlight_direct(driver):
    direct_seller = "no"
    try:
        driver.find_element(By.CSS_SELECTOR, '.spotlight__banner.direct')
        direct_seller = "yes"
    except NoSuchElementException:
        pass
    return direct_seller

def get_spotlight_info(driver):
    spotlight_info = {}
    try:
        spotlight_price = get_spotlight_price(driver)
        spotlight_stock = get_spotlight_stock(driver)
        direct_seller = is_spotlight_direct(driver)

        spotlight_info = {
            'Spotlight Price': spotlight_price,
            'Spotlight Stock': spotlight_stock,
            'Direct': direct_seller
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        spotlight_info = {
            'Spotlight Price': "NA",
            'Spotlight Stock': "NA",
            'Direct': "NA"
        }

    return spotlight_info

def get_listing_info(driver, url):
    listings_data = []
    spotlight_data = {}
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        card_info = get_card_name(driver)
        listings_info = get_listings_info(driver)

        for listing in listings_info:
            listings_data.append((
                card_info,
                listing['Price'],
                listing['Stock'],
                listing['Shipping Cost'],
                listing['Seller'],
                listing['Sales'],
                listing['Direct']
            ))

        # Get spotlight info
        spotlight_info = get_spotlight_info(driver)
        spotlight_data = (
            card_info,
            spotlight_info['Spotlight Price'],
            spotlight_info['Spotlight Stock'],
            "Free Shipping" if spotlight_info['Direct'] == "yes" else "NA",
            spotlight_info['Direct']
        )

    except Exception as e:
        print(f"An error occurred with URL {url}: {e}")

    return listings_data, spotlight_data

def initialize_webdriver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

if __name__ == "__main__":
    urls = [
        'https://www.tcgplayer.com/product/477061/pokemon-crown-zenith-galarian-gallery-glaceon-vstar?Condition=Near+Mint&Language=English&page=1&ListingType=standard',
        'https://www.tcgplayer.com/product/502589?irclickid=QxPxEZ2hUxyKWHgV6XVKNVrtUkHXse0VrRa:X80&sharedid=&irpid=4944541&irgwc=1&utm_source=impact&utm_medium=affiliate&utm_campaign=Scrydex&Printing=Reverse+Holofoil&ListingType=standard&page=1&Condition=Near+Mint&Language=English',
        'https://www.tcgplayer.com/product/197646/pokemon-hidden-fates-paras?Condition=Near+Mint&Language=English&page=1&Printing=Normal&ListingType=standard',
        'https://www.tcgplayer.com/product/107006/pokemon-base-set-shadowless-nidoking?page=1&Language=English&Printing=1st+Edition+Holofoil&Condition=Near+Mint|Lightly+Played',
        'https://www.tcgplayer.com/product/283885?irclickid=2m4y842hRxyKWHgV6XVKNVrtUkHXseWNrRa:X80&sharedid=&irpid=4944541&irgwc=1&utm_source=impact&utm_medium=affiliate&utm_campaign=Scrydex&Printing=Normal&ListingType=standard&page=1&Condition=Near+Mint&Language=English',
        'https://www.tcgplayer.com/product/234199?irclickid=21sU372hRxyKWHgV6XVKNVrtUkHXseWBrRa:X80&sharedid=&irpid=4944541&irgwc=1&utm_source=impact&utm_medium=affiliate&utm_campaign=Scrydex&Printing=Normal&ListingType=standard&page=1&Condition=Near+Mint&Language=English',
        'https://www.tcgplayer.com/product/183964?irclickid=y-vSdB2hUxyKWHgV6XVKNVrtUkHXsZRBrRa%3AX80&sharedid=&irpid=4944541&irgwc=1&utm_source=impact&utm_medium=affiliate&utm_campaign=Scrydex&Printing=Holofoil&ListingType=standard&page=1&Condition=Lightly+Played|Near+Mint',
        'https://www.tcgplayer.com/product/107067/pokemon-base-set-shadowless-clefairy-doll?page=1&Language=English&Printing=1st+Edition&Condition=Near+Mint|Lightly+Played',
        'https://www.tcgplayer.com/product/44419/pokemon-fossil-lapras-10?page=1&Language=English&Printing=1st+Edition+Holofoil&Condition=Lightly+Played|Near+Mint&ListingType=standard'

    ]
    
    driver = initialize_webdriver()
    all_listings = []
    spotlight_infos = {}
    try:
        for url in urls:
            listings_data, spotlight_data = get_listing_info(driver, url)
            all_listings.extend(listings_data)
            spotlight_infos[spotlight_data[0]] = spotlight_data

            for data in listings_data:
                print(f"Card Name: {data[0]}")
                print(f"Price: ${data[1]}")
                print(f"Stock: {data[2]}")
                print(f"Shipping Cost: {data[3]}")
                print(f"Seller: {data[4]}")
                print(f"Sales: {data[5]}")
                print(f"Direct: {data[6]}")
                print("-" * 40)

            print("Spotlight Listing:")
            print(f"Card Name: {spotlight_data[0]}")
            print(f"Price: {spotlight_data[1]}")
            print(f"Stock: {spotlight_data[2]}")
            print(f"Shipping Cost: {spotlight_data[3]}")
            print(f"Direct: {spotlight_data[4]}")
            print("=" * 40)
    finally:
        print("python algorythm_scrape.py")
        driver.quit()

    # Calculate mean average of all listings prices (including shipping) for each card
    card_prices = {}
    for listing in all_listings:
        card_name = listing[0]
        price = listing[1]
        shipping_cost = listing[3]
        if price != "NA":
            total_price = float(price)
            if shipping_cost != "NA":
                total_price += float(shipping_cost)
            if card_name not in card_prices:
                card_prices[card_name] = []
            card_prices[card_name].append(total_price)

    for card_name, prices in card_prices.items():
        if prices:
            mean_price = statistics.mean(prices)
            std_dev_price = statistics.stdev(prices) if len(prices) > 1 else 0
            print(f"Mean average price (including shipping) for {card_name}: ${mean_price:.2f}")
            print(f"Standard deviation (including shipping) for {card_name}: ${std_dev_price:.2f}")
        else:
            print(f"Mean average price (including shipping) for {card_name}: NA")
            print(f"Standard deviation (including shipping) for {card_name}: NA")

    # Calculate box price idea
    print("\nBox Price Idea:")
    for card_name, spotlight_data in spotlight_infos.items():
        spotlight_price = spotlight_data[1]
        spotlight_stock = spotlight_data[2]
        spotlight_direct = spotlight_data[4]

        if spotlight_direct == "yes" and spotlight_stock != "NA" and int(spotlight_stock) >= 25:
            # Calculate the average and standard deviation of the first 10 listings
            first_10_prices = [float(listing[1]) + float(listing[3]) for listing in all_listings if listing[0] == card_name][:10]
            avg_first_10 = statistics.mean(first_10_prices)
            std_dev_first_10 = statistics.stdev(first_10_prices)

            if abs(float(spotlight_price) - avg_first_10) <= 2 * std_dev_first_10:
                box_price = float(spotlight_price)
            else:
                box_price = statistics.mean(card_prices[card_name])
        else:
            # Calculate the weighted average excluding vendors with fewer than 500 sales and prices outside 2 standard deviations
            filtered_prices = [price for price in card_prices[card_name] if abs(price - statistics.mean(card_prices[card_name])) <= 2 * statistics.stdev(card_prices[card_name])]
            filtered_prices = [price for price in filtered_prices if any(listing[4] == card_name and int(listing[5].replace(' Sales', '')) >= 500 for listing in all_listings)]
            box_price = statistics.mean(filtered_prices) if filtered_prices else statistics.mean(card_prices[card_name])

        print(f"Box price idea for {card_name}: ${box_price:.2f}" if box_price != "NA" else f"Box price idea for {card_name}: NA")
