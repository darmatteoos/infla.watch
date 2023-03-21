import requests
import json
import time
import datetime
import os
import xml.etree.ElementTree as ET
from os.path import exists
from utilities_module import TerminalPrint
import random
import html
import re

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
				#time.sleep(0.5)
				try:
					payload = r.json()
				except RequestsJSONDecodeError as e:
					print(("The following response couldn't be"
						f"parsed as json:\n{r.text()}"
						f"\nError message: {e.msg} at position {e.pos}"
						))
				except Exception as e:
					print(e)
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
							'fresh': el['fields']['fresh'],
							'frozen': el['fields']['frozen'],
							'is_package': el['fields']['is_package'],
							'thumbnail': el['fields']['thumbnail'] if ('thumbnail' in el['fields']) else None,							
							'price': None 	#added later
						}		

						#checking for duplicates:

						if duplicate == True:
							self.terminal.print(f"{el['id']} already present in the dictionary")
							self.terminal.print(product_dict[el['id']], duplicate_el)
							duplicate = False
					
				#finished parsing data aside from stock info
				else:

					self.terminal.print(f'Successfully gathered information on {len(product_dict)} products.', show_time=True)

					#adding prices if specified:
					if add_prices == True:

						prices_info = self.get_product_price_and_qty(product_dict)
						for el in product_dict:
							try:
								product_dict[el]['price'] = prices_info[el][0]
								product_dict[el]['qty'] = prices_info[el][1]
							except Exception as e:
								self.terminal.print(e, show_time=True)
								self.terminal.print(f'No price/qty found for item {el}, defaulting to None.')

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
	def get_product_price_and_qty(self, product_dict, buffer=200):

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
				#time.sleep(0.5)
				req = requests.get(product_url)
				product_stock_info_parcel = req.json()
				self.terminal.print(f'Downloading stock info.. {round(dl_progress_index/len(product_dict)*100, 2)}% complete.', show_time=True, flush=True)
				for product in product_stock_info_parcel: 
					#casting the product_id to string to match the product_dict synthax and 
					#provide faster runtime performance when comparing keys
					#for info: https://stackoverflow.com/questions/11162201/is-it-always-faster-to-use-string-as-key-in-a-dict
					product_stock_info[str(product['stock_item']['product_id'])] = [product['price'], product['qty']]
				

				#resets string and counter for the next iteration
				sku_string = ''	

		return product_stock_info

	def terminal_time(self):

		return f'[{datetime.datetime.today().strftime("%d:%m:%Y-%H:%M")}]'



class ConadWebScraper(object):
	"""docstring for ConadWebScraper"""
	def __init__(self):

		self.time = datetime.datetime.now()
		self.endpoint = "https://spesaonline.conad.it"
		#this is the only necessary cookie to get a full product response from the server, meaning one
		#that has not only the general products, but also the ones ready for delivery in the location selected 
		#Via Mario Pagano, 10, 20145 Milano MI, Italia
		cookies = {
    		"ecAccess": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlY0FjY2VzcyIsInVzZXJJZCI6IjM2NjM1NTgiLCJ0aW1lc3RhbXAiOjE2NzkyNDY3ODYyNjYsInR5cGVPZlNlcnZpY2UiOiJIT01FX0RFTElWRVJZIiwicG9pbnRPZlNlcnZpY2VJZCI6IjAwOTE5MiIsImRlbGl2ZXJ5QXJlYSI6ImFyZWFfMDA5MTkyXzIwNSIsImNhcnRJZCI6ImMtZS1DLTIzLTAwNDM0Njg5IiwiYW5vbnltb3VzQ2FydElkIjoiMWM3MmJhMjQtYzY2NC0xMWVkLWFiNjctNTU3MzY1NzI1MzY4IiwiY2FydENyZWF0aW9uVGltZSI6MTY3OTIzNjg3OTAwMCwidGltZXNsb3RFeHBpcmF0aW9uIjowLCJkZWxpdmVyeUFkZHJlc3MiOiJWaWEgTWFyaW8gUGFnYW5vLCAxMCwgMjAxNDUgTWlsYW5vIE1JLCBJdGFsaWEiLCJjb21wbGV0ZUFkZHJlc3MiOiJ7XCJjZWxscGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiY291bnRyeVwiOntcImlzb2NvZGVcIjpcIklUXCIsXCJuYW1lXCI6XCJJdGFseVwifSxcImRpc3RyaWN0XCI6XCJNaWxhbm9cIixcImZsb29yXCI6MCxcImZvcm1hdHRlZEFkZHJlc3NcIjpcIlZpYSBNYXJpbyBQYWdhbm8sIDEwLCAyMDE0NSBNaWxhbm8gTUksIEl0YWxpYVwiLFwibGF0aXR1ZGVcIjo0NS40NzQzMTcsXCJsaWZ0XCI6ZmFsc2UsXCJsaW5lMVwiOlwiVmlhIE1hcmlvIFBhZ2FubywgMjAxNDUsIE1pbGFubywgSXRhbGlhXCIsXCJsaW5lMlwiOlwiMTBcIixcImxvbmdpdHVkZVwiOjkuMTcwMDgxOSxcIm5vdENvbXBsZXRlZFwiOmZhbHNlLFwicG9zdGFsQ29kZVwiOlwiMjAxNDVcIixcInJlY2VwdGlvblwiOmZhbHNlLFwidG93blwiOlwiTWlsYW5vXCJ9IiwibGF0aXR1ZGluZSI6NDUuNDc0MzE3LCJsb25naXR1ZGluZSI6OS4xNzAwODE5LCJuU3RvcmVzRm91bmQiOjIsIm1pc3NpbmdDYXJ0Q291bnRlciI6MCwidXNlckZpbmdlcnByaW50IjoiRkQxNzIxNENFQjg4QzlEMkQ1NTIyRjVDNjVFNjc2NjciLCJpc3MiOiJjb25hZCIsImlhdCI6MTY3OTMwMDA3Mn0.PEuNy5635fCxQiQgL40mHUxYbPA8YbZGx6g-pxt2rmo"
		}
		headers = {
    		"Sec-Ch-Ua": '"Chromium";v="111", "Not(A:Brand";v="8"',
    		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.65 Safari/537.36",
    		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    		"Accept-Encoding": "gzip, deflate",
    		"Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
		}
		self.session = requests.Session()
		self.session.headers.update(headers)
		self.session.cookies.update(cookies)
		self.mkt_id = "conad"
		self.terminal = TerminalPrint()
		
	#omit is a list of keywords to be excluded from categories URIs (to be tested)
	def get_categories(self, omit=None):
		
		url = self.endpoint + "/home"
		r = self.session.get(url)
		if r.status_code == 200:
			cats = re.findall(r'<a onclick=\"Header\.trackSecondLevel\(this\)\" href=\"/c(/.+)\">', r.text)
		else:
			print(f"Http code: {status_code}! Cannot access the homepage correctly.")

		#to be tested...
		if omit != None:
			new_cats = []
			to_remove = False
			for cat in cats:

				for el in omit:
					if el in cat:
						to_remove = True
						break

				if to_remove != True:
					new_cats.append(cat)
				else:
					to_remove = False
			cats = new_cats
		
		return cats


	def get_products(self, omit=None):
		base_url = self.endpoint + "/c/level2/_jcr_content/root/search.loader.html"
		cats = self.get_categories(omit)
		tot = 0
		tot_prods = []
		i = 0
		while i < len(cats):
			cat = cats[i]
			i += 1
			url = base_url + cat + ".html"
			r = self.session.get(url)
			if r.status_code == 200:
				text = self.session.get(url).text
				tot_cat = int(re.search(r"<b class=\"results\">(\d+).+</b>", text).group(1))

				self.terminal.print(f"Attempting to get {tot_cat} products at {url}")
				index = 0
				pages = tot_cat // 30 + 1
				prods = []
				for page in range(1, pages+1):
					if page == 1:
						batch = self.find_products(text)
						index += len(batch)
						prods.extend(batch)
						self.terminal.print(f"Got {index}/{tot_cat} elements.", flush = True)
					else:
						#resets the url erasing page queries from previous iterations
						time.sleep(random.random())
						url = url.split("?")[0]
						url = url + f"?page={page}"
						text = self.session.get(url).text
						batch = self.find_products(text)
						index += len(batch)
						prods.extend(batch)
						self.terminal.print(f"Got {index}/{tot_cat} elements.", flush = True)


				tot_prods.extend(prods)
				tot += tot_cat
			else:
				i =- 1
				self.terminal.print(f"Cannot access {url} correctly (http code: {r.status_code})")
				self.terminal.print("Retrying in 30s..")
				time.sleep(30)


		self.terminal.print(f"Total products: {len(tot_prods)}/{tot}")
		return tot_prods


	def find_products(self, text):

		escaped_prods = re.findall(r"<div nkPage=\"ProductCard\" class=\"component-ProductCard\" data-product=\"(.+)\">", text)
		prods = []
		for prod in escaped_prods:
			prod = json.loads(html.unescape(prod))
			prods.append({
				'sku': prod["code"],
				'name': prod["nome"],
				'brand': prod["marchio"],
				'netweight': prod["netQuantity"] if "netQuantity" in prod else None,
				'unit_of_measurement': prod["netQuantityUm"],
				'date': self.time.strftime("%Y-%m-%d %H:%M:%S"),				
				'price': prod["basePrice"],
				'cat1': prod["categoriaPrimoLivello"],
				'cat2': prod["categoriaSecondoLivello"],
				'cat3': prod["categoriaTerzoLivello"]
			})
		return prods



	


	def write_product_dict_to_file(
			self, 
			add_date_to_filename=True,
			file_name=None
			):

		if file_name != None:

			if add_date_to_filename == True:
				file_path = f'data/{file_name}_{self.time.strftime("%d_%m_%Y_%H_%M_%S")}.json'
			else:
				file_path = f'data/{file_name}.json'

		else:

			self.terminal.print('No file-name specified.\nDefaulting to [mkt_id][date].json', show_time=True)
			file_path = f'data/{self.mkt_id}_{self.time.strftime("%d_%m_%Y_%H_%M_%S")}.json'

		with open(file_path, "w") as file:
				file.write(json.dumps(self.get_products()))
				self.terminal.print(f"Data written to file: {file_path}", show_time=True)
	








