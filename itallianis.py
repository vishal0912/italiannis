import scrapy
import pycountry
from locations.items import GeojsonPointItem
from locations.categories import Code
from typing import List,Dict
from bs4 import BeautifulSoup
import uuid
import re
from urllib.parse import urlparse, parse_qs

class Italiannis(scrapy.Spider):
    name = 'italiannis_dac'
    brand_name = 'ITALIANNIS'
    spider_type: str = 'chain'
    spider_chain_id = "5101"
    spider_categories: List[str] = [Code.RESTAURANT]
    spider_countries = [pycountry.countries.lookup('mex').alpha_2]
    allowed_domains = ["italiannis.com.mx"]
    start_urls = ['https://www.italiannis.com.mx/ubicaciones/']
    def start_requests(self):
        headers = {
            'User-Agent': 'PostmanRuntime/7.32.3',
        }

        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    
    def parse(self, response):
        # Extract data from each location div
        for location_div in response.css('div.wpb_row.box-shadow-ubications'):
            location_name = location_div.css('p.ubication-title::text').get().strip()
            location_address = location_div.css('p.ubication-description::text').get().strip()
            telephone = location_div.css('a::text').get().replace("Telephone:", "").strip()

            
            for row in location_div.css('.vc_toggle_content table tr'):
                
                timing = row.css('td:nth-child(2) time::text').get().strip()
                
            # Extract latitude and longitude from Google Maps iframe URL
            iframe_url = location_div.css('iframe::attr(src)').get()
            if iframe_url:
                latitude, longitude = self.extract_latitude_longitude(iframe_url)
            else:
                latitude, longitude = None, None
            data = {
                'ref': uuid.uuid4().hex,
                'chain_id': '5101',
                'chain_name': 'ITALIANNIS',
                'addr_full':location_address,
                'name' :location_name, 
                'phone':telephone,
                'opening_hours':timing,
                'website': 'https://www.italiannis.com.mx/ubicaciones/',
                'lon':longitude,
                'lat':latitude,
                'brand':'ITALIANNIS'
                

            }

            yield GeojsonPointItem(**data)

    def extract_latitude_longitude(self, iframe_url):
        # Parse latitude and longitude from the Google Maps URL in the iframe src attribute
        latitude = None
        longitude = None
        try:
            start_idx = iframe_url.index('!2d') + 3
            end_idx = iframe_url.index('!3d')
            longitude = float(iframe_url[start_idx:end_idx])

            start_idx = iframe_url.index('!3d') + 3
            end_idx = iframe_url.index('!2m')
            latitude = float(iframe_url[start_idx:end_idx])
        except ValueError:
            pass

        return latitude, longitude