import scrapy
import pandas as pd
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
import time
df = pd.read_csv('F:\Web Scraping\Golabal\keywords.csv')
base_url = 'https://www.mcdougallbay.com/search.php?tab=all&category=&search={}&location=&sortbid=Closing'

class BaySpider(scrapy.Spider):
    name = 'bay'
    # allowed_domains = ['https://www.mcdougallbay.com']
    def start_requests(self):
        for index in df:
            SCROLL_PAUSE_TIME = 3
            settings = get_project_settings()
            driver_path = settings['SELENIUM_DRIVER_EXECUTABLE_PATH']
            options = webdriver.ChromeOptions()
            options.headless = False
            driver = webdriver.Chrome(driver_path, options=options)
            driver.get(base_url.format(index))
            driver.maximize_window()
            time.sleep(5)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")           
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:                    
                    break
                last_height = new_height
                
            time.sleep(5)
            link_elements = driver.find_elements(By.XPATH,"//div[@class='details details2']/a")        
            print(len(link_elements))
            for link in link_elements:
                yield scrapy.Request(link.get_attribute('href'),callback=self.parse,cb_kwargs={'index':index})
                
            driver.quit()
    def parse(self, response,index): 
        print(".................")  
        product_url = response.url
        print(product_url)  
        print(index)    
        image = "https://www.mcdougallbay.com/"+response.xpath("//div[@class='top_left']/div/a/@href").get()  
        print(image)
        date1 = response.css('[id=lblLotEndTime]::text').get()
        date2 = date1.strip("(Ends ")
        auction_date = date2.strip(" CST)")
        print(auction_date)  
        location = ''
        try:      
            loc = response.xpath('//*[@id="divPlaceBidBox"]/div[7]/div[5]/font/text()').get()
            location = loc.strip("Location: ")
        except:
            loc = response.xpath('//*[@id="divPlaceBidBox"]/div[7]/div[3]/font/text()').get()    
            location = loc.strip("Location: ")
        print(location)
        
        product = response.xpath("//div[@class='inner_left_top']/h2/text()[1]").get()
        product_name = product.strip()
        print(product_name)
        lot_number = ''
        try:
            lot= response.xpath("//div[@class='inner_left_top']/h2/text()[2]").get()                                 
            lot_number = lot[7:]
            print(lot_number)  
        except:
            lot = response.xpath("//div[@class='inner_left_top']/h2/text()").get()
            lot_num = lot.split('Lot ')
            lot_number = lot_num[1]
            print(lot_number)        
        auctioner = "McDougall Auctioneers"
        print(auctioner)        
        
        yield{            
            'product_url' : response.url, 
            'item_type' : index,                 
            'image_link' : image,          
            'auction_date' : auction_date,            
            'location' : location,           
            'product_name' : product_name,            
            'lot_id' : lot_number,          
            'auctioner' : auctioner,
            'website' : 'mcdougallbay',            
            'description' : ''             
        }