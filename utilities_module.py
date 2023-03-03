import datetime
import json
import os

class TerminalPrint(object):
	"""Utility to correctly format time expressions in front of a terminal message
	and avoid redundancies in code. Also gives the possibility flush terminal"""
	def __init__(self):
		
		self.was_refreshed = False


	def print(self, text, flush=False, show_time=False):

		print_string = ''

		if show_time == True:
			print_string += f'{self.format_time()} '
		
		if flush == False:
			if self.was_refreshed == False:
				print(f'{print_string}{text}')
			else:
				print(f'\n{print_string}{text}')

		else:
			print(f'\r{print_string}{text}', end='')
			self.was_refreshed = True


	def format_time(self):

		return f'[{datetime.datetime.today().strftime("%d:%m:%Y-%H:%M:%S")}]'


class RUtility(object):
	"""docstring for RUtility"""
	def __init__(self, arg):
			pass

	def to_R_json_parser(self, data, path=False):

		parsed_data = []
		
		if path == True:
			with open(data, "r") as f:
				data = json.loads(f.read())


		#removes nesting of products, removing id association and leaving onlu SKUs
		for product in data:
			parsed_data.append(data[product])

		return json.dumps(parsed_data)

	def save_to_file(self, parsed_data, file_name):

		working_directory_path = ''
		for count, el in enumerate(__file__.split('/')[0:-1]):
			if count != 0:
				working_directory_path += f'/{el}'
		os.chdir(working_directory_path)

		data_rel_path = "/R_analysis/R_formatted_data"
		data_path = os.getcwd() + data_rel_path
		if not os.path.exists(data_path):
			os.mkdir(data_path)
			terminal = TerminalPrint()
			message = (f"Data folder in R directory not present.\n" 
				f"Creating directory R_formatted_data at {data_path}"
				)
			terminal.print(message, show_time=True)

		with open(data_path + "/" + file_name, "w") as file:
			file.write(parsed_data)


		

if __name__ == "__main__":
	ut = RUtility("ciao")
	ut.save_to_file(ut.to_R_json_parser("/Users/matteodaros/Documents/coding/natura_web_scraper/data/all_products_no_deals_01_03_2023_10_51.json", path=True), "R_all_products_no_deals_01_03_2023_10_51.json")

		