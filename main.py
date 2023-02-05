from web_scraper_class import NaturasiWebScraper
from utilities_module import TerminalPrint
import datetime
import json


# can compare both files or dictionaries. Files must be specified in string format
# with root directory the same as "main.py".
# return a dictionary with changed products by id and by values (eg. price, net weight, etc.)
def compare_product_dicts(old, new, file=True, write_to_file=False):

	if file == True:
		old_path, new_path = (old, new)
		with open(old_path, 'r') as old_file:
			old_products = json.loads(old_file.read())
		with open(new_path, 'r') as new_file:
			new_products = json.loads(new_file.read())
	else:
		old_products = old
		new_products = new

	#first it checks if some elements have been added/removed:

	changed_products = {'removed': [], 'added': []}

	for product in old_products:
		if product not in new_products:
			changed_products['removed'].append(product)

	for product in new_products:
		if product not in old_products:
			changed_products['added'].append(product)

	if changed_products == {}:
		print('No elements have been added/removed')
	else:
		for status in changed_products:
			print(f'Elements {status}: {changed_products[status]}')

	#then it checks if some info about the product has been updated:

	changed_fields = {}

	for product in old_products:
		if product not in changed_products['added'] and product not in changed_products['removed']:
			for field in old_products[product]:
				# do not count changes in the date as a field change
				if field == 'date':
					continue
				if old_products[product][field] != new_products[product][field]:
					changed_fields[product] = {
						field: {'old': old_products[product][field], 'new': new_products[product][field]}
					}

	if changed_fields == {}:
		print('No elements have seen changes in their fields')
	else:
		for el in changed_fields:
			for field in changed_fields[el]:
				print(f'Element {el} changed {field} (old: {changed_fields[el][field]["old"]}, new: {changed_fields[el][field]["new"]})')

	# tbd how to name the file concisely
	if write_to_file == True:
		pass

	return {'changed_products': changed_products, 'changed_fields': changed_fields}









#scraper for all products:
scraper = NaturasiWebScraper([43178, 43247, 43076, 43016, 43277, 43301, 43382, 43997, 43586, 43562, 44018, 43844, 43622, 43922, 43982, 44073])
scraper.write_product_dict_to_file(file_name='all_products_no_deals', add_date_to_filename=True, add_prices=True)

#scraper = NaturasiWebScraper([43076, 43076], add_prices=True)
#scraper = NaturasiWebScraper([43922], file_name='prod_id_43922', date=datetime.datetime.today())

#scraper.write_product_dict_to_file(add_date_to_filename=True)
#product_dict = scraper.get_product_dict()
#scraper.get_product_prices(product_dict)

#scraper.get_product_dict()
#print(scraper.get_products_size())
#print(scraper.endpoint)

#compare_product_dicts('data/all_products_no_deals_29_01_2023_10_43.json', 'data/all_products_no_deals_31_01_2023_18_40.json')


