import json
import math
import scrapy
from urllib.parse import urlencode
from crawlers.items import WalmartProduct, WalmartProductLoader


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    
    custom_settings = {
        'FEEDS': { 'data/%(name)s_%(time)s.csv': { 'format': 'csv',}}
        } 

    def start_requests(self):
        keyword_list = ['targus']
        for keyword in keyword_list:
            payload = {'q': keyword, 'sort': 'best_match', 'page': 1, 'affinityOverride': 'default'}
            walmart_search_url = 'https://www.walmart.ca/search?' + urlencode(payload)
            yield scrapy.Request(url=walmart_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': 1})

    def parse_search_results(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 
        script_tag  = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)

            ## Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
            for idx, product in enumerate(product_list):
                walmart_product_url = 'https://www.walmart.ca' + product.get('canonicalUrl', '').split('?')[0]
                yield scrapy.Request(url=walmart_product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page, 'position': idx + 1})
            
            ## Request Next Page
                if page == 1:
                    total_product_count = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["count"]
                    max_pages = math.ceil(total_product_count / 40)
                    if max_pages > 10:
                        max_pages = 10
                    for p in range(2, max_pages):
                        payload = {'q': keyword, 'sort': 'best_seller', 'page': p, 'affinityOverride': 'default'}
                        walmart_search_url = 'https://www.walmart.ca/search?' + urlencode(payload)
                        yield scrapy.Request(url=walmart_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': p})
                 
    def parse_product_data(self, response):
        script_tag  = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)
            product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
            url_values = [image["url"] for image in product_data['imageInfo'].get('allImages')]
            idml_data = json_blob["props"]["pageProps"]["initialData"]["data"]["idml"]
            review_data = json_blob["props"]["pageProps"]["initialData"]["data"]["reviews"]
            manufacturer_name = None
            for spec in idml_data.get('specifications'):
                if spec.get('name') == 'Manufacturer':
                    manufacturer_name = spec.get('value')
                    
            yield {
                'platform_product_id': product_data.get('id'),
                'platform_marketplace_id': 'WALMART-CA',
                'product_title': product_data.get('name'),
                'currency': product_data['priceInfo']['currentPrice'].get('currencyUnit'),
                'buy_box_price': product_data['priceInfo']['currentPrice'].get('price'),
                'manufacturer_name': manufacturer_name,
                'brand': product_data.get('brand'),
                'model_number': product_data.get('model'),
                'part_number': 'NA',
                'model_name': 'NA',
                'product_dimensions': 'NA',
                'product_weight': 'NA',
                'ratings_count': review_data.get('totalReviewCount'),
                'average_rating': review_data.get('averageOverallRating'),
                'listing_url': 'https://www.walmart.ca' + product_data.get('canonicalUrl'),
                'image_urls': url_values,
                'buy_box_seller': product_data.get('sellerName'),
                'seller_url': 'https://www.walmart.ca/seller/' + str(product_data.get('catalogSellerId')),
                
                # 'upc': product_data.get('upc'),
                # 'availability': product_data.get('availabilityStatus'),
                # 'seller_id': product_data.get('sellerId'),
                # 'brandUrl': 'https://www.walmart.com' + product_data.get('brandUrl'),
                # 'category_name': product_data.get('category'),
                # 'offer_id': product_data.get('offerId'),    
            }




    
