import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Join, MapCompose, Compose
import re

class WalmartProduct(scrapy.Item):
    platform_product_id = scrapy.Field()
    product_title = scrapy.Field()
    buy_box_price = scrapy.Field()
    currency = scrapy.Field()
    model_number = scrapy.Field()
    listing_url = scrapy.Field()
    manufacturer = scrapy.Field()
    brand = scrapy.Field()
    part_number = scrapy.Field()
    model_name = scrapy.Field()
    product_dimensions = scrapy.Field()
    ratings_count = scrapy.Field()
    average_rating = scrapy.Field()
    image_url = scrapy.Field()
    product_weight = scrapy.Field()
    platform_marketplace_id = scrapy.Field()
    seller_url = scrapy.Field()
    buy_box_seller = scrapy.Field()
    platform = scrapy.Field()



class WalmartProductLoader(ItemLoader):
    
    default_output_processor = TakeFirst()
    
    product_title_in = MapCompose(str.strip)
    buy_box_price_in = MapCompose(lambda x: x.split("$")[-1])
    listing_url_in = MapCompose(lambda x: 'https://www.walmart.ca' + x)
    manufacturer_in = MapCompose()
    brand_in = MapCompose()
    part_number_in = MapCompose()
    model_number_in = MapCompose()
    model_name_in = MapCompose()
    product_dimensions_in = MapCompose()
    ratings_count_in = MapCompose()
    average_rating_in = MapCompose()
    image_url_in = MapCompose()
    product_weight_in = MapCompose()
    seller_url_in = MapCompose()