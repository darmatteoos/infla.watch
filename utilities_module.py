import datetime

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