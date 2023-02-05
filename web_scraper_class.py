import requests
import json
import time
import datetime
import os
import xml.etree.ElementTree as ET
from os.path import exists
from utilities_module import TerminalPrint

class NaturasiWebScraper:
	"""
	A web-scraper for https://www.naturasi.it
	----
	Category_ids:
	43178 -> Proteine animali
	43247 -> Proteine vegetali
	43076 -> Pasta, riso e cereali
	43016 -> Frutta e verdura
	43277 -> Bevande 
	43301 -> Dispensa e condimenti
	43382 -> Colazione e dessert
	43997 -> Oriente e macrobiotica
	43586 -> Tisane e infusi
	43562 -> Piatti pronti
	44018 -> Vino e birra
	43844 -> Cura della casa
	43622 -> Cura della persona
	43922 -> Bambini
	43982 -> Animali
	44073 -> Offerte e promozioni
	----
	category_ids is a list of ids
	"""

	# date in datetime format
	# file_name must be specified without extension name
	def __init__(self, category_ids, date=None):

		#setting the correct working directory
		working_directory_path = ''
		for count, el in enumerate(__file__.split('/')[0:-1]):
			if count != 0:
				working_directory_path += f'/{el}'
		os.chdir(working_directory_path)

		self.date = datetime.datetime.today()
	
		#setting the category-specific endpoint
		string_categories = ''
		for index, category_id in enumerate(category_ids):
			if index < len(category_ids)-1:
				string_categories += f'"{category_id}",'
			else:
				string_categories += f'"{category_id}"'

		self.endpoint = f'https://naturasi-ecommerce-search.mlreply.net/indexes/products/documents?filters=category_ids:({string_categories})'
		
		#initializing a terminal printer to avoid newline/carriage return conflicts
		self.terminal = TerminalPrint()


	def get_product_dict(self, add_prices=False):

		product_dict = {}
		spacing = 50
		index = 0

		self.terminal.print('Attempting to download product info..', show_time=True)
		while True:
			duplicate = False
			url = self.endpoint+f'&from={index}&limit={spacing}'		
			total_hits = requests.get(self.endpoint+f'&from=1000000&limit={spacing}').json()['totalHits']
			load_time = round(index/total_hits*100, 2)
			self.terminal.print(f'Downloading product info.. {load_time}% complete', show_time=True, flush=True)
			with requests.get(url) as r: 
				time.sleep(0.5)
				payload = r.json()
				#self.terminal.print(payload)
				if len(payload['documents']) != 0:

					index += len(payload['documents'])

					for el in payload['documents']:
						len_product_dict = len(product_dict)

						if el['id'] in product_dict:
							duplicate_el = product_dict[el['id']]
							duplicate = True

						product_dict[el['id']] = {
							'sku': el['fields']['sku'],
							'name': el['fields']['name'],
							'brand': el['fields']['brand'],
							'netweight': el['fields']['netweight'],
							'package_detail': el['fields']['package_detail'],
							'unit_of_measurement': el['fields']['unit_of_measurement'],
							'date': str(self.date),
							'price': None 	#added later
						}		

						#checking for duplicates:

						if duplicate == True:
							self.terminal.print(f"{el['id']} already present in the dictionary")
							self.terminal.print(product_dict[el['id']], duplicate_el)
							duplicate = False
					
				#finished parsing data aside from price	
				else:

					self.terminal.print(f'Successfully gathered information on {len(product_dict)} products.', show_time=True)

					#adding prices if specified:
					if add_prices == True:

						prices_info = self.get_product_prices(product_dict)
						for el in product_dict:
							try:
								product_dict[el]['price'] = prices_info[el]
							except Exception as e:
								self.terminal.print(e, show_time=True)
								self.terminal.print(f'No price found for item {el}, defaulting to None.')

					return product_dict


	def write_product_dict_to_file(self, 
			file_name=None, 
			add_date_to_filename=False,
			add_prices=False):

		if file_name != None:

			if add_date_to_filename == True and self.date != None:
				file_path = f'data/{file_name}_{self.date.strftime("%d_%m_%Y_%H_%M")}.json'
			else:
				file_path = f'data/{file_name}.json'

		else:

			self.terminal.print('No file-name specified.\nDefaulting to [datetime].json', show_time=True)
			file_path = f'data/{file_name}_{self.date.strftime("%d_%m_%Y_%H_%M")}.json'

		with open(file_path, "w") as file:
				file.write(json.dumps(self.get_product_dict(add_prices=add_prices)))
				self.terminal.print(f"Data written to file: {file_path}", show_time=True)



	def get_products_size(self):
	
		total_hits = requests.get(self.endpoint+'&from=1000000&limit=50').json()['totalHits']
		return total_hits


	# buffer of 200 seems to produce a valid response (with 200 elements)
	def get_product_prices(self, product_dict, buffer=200):

		#sku string is a concatenated list of sku numbers for url query purposes
		sku_string = ''
		product_stock_info = {}
		dl_progress_index = 0
		for i, product in enumerate(product_dict):

			sku_string += f"{str(product_dict[product]['sku'])},"
			dl_progress_index += 1

			#checks if the product index is a multiple of buffer (or 
			#the last element of the dict), if it is,
			#it resets the sku_string and starts with a fresh url

			if i != 0 and (i % buffer == 0  or (i == len(product_dict)-1)):
				#removes the last comma (otherwise the request gives a broken xml file)
				sku_string = sku_string[:-1]

				#the file format is formatted to a JSON array
				product_url = f'https://app.naturasi.it/rest/store_vetrina0/V1/prices-stocks?skus={sku_string}'
				#self.terminal.print(product_url)
				time.sleep(0.5)
				req = requests.get(product_url)
				product_stock_info_parcel = req.json()
				self.terminal.print(f'Downloading prices.. {round(dl_progress_index/len(product_dict)*100, 2)}% complete.', show_time=True, flush=True)
				for product in product_stock_info_parcel: 
					#casting the product_id to string to match the product_dict synthax and 
					#provide faster runtime performance when comparing keys
					#for info: https://stackoverflow.com/questions/11162201/is-it-always-faster-to-use-string-as-key-in-a-dict
					product_stock_info[str(product['stock_item']['product_id'])] = product['price']
				

				#resets string and counter for the next iteration
				sku_string = ''	

		return product_stock_info

	def terminal_time(self):

		return f'[{datetime.datetime.today().strftime("%d:%m:%Y-%H:%M")}]'


	











