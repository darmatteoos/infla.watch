from python.web_scraper_class import NaturasiWebScraper
from python.web_scraper_class import ConadWebScraper
from python.utilities_module import TerminalPrint
from python.utilities_module import TelegramClient
from python.utilities_module import RUtility
from datetime import datetime
import time
import os
import sys
import subprocess
import telegram
import asyncio

# bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
# chat_id = os.environ.get('TELEGRAM_CHAT_ID')
# client = TelegramClient(bot_token, chat_id)

# #scraper for all products:
# scraper = NaturasiWebScraper([43178, 43247, 43076, 43016, 43277, 43301, 43382, 43997, 43586, 43562, 44018, 43844, 43622, 43922, 43982, 44073])
# scraper2 = ConadWebScraper()

# try:
# 	start1 = time.time()
# 	# scraper2.write_product_dict_to_file(file_name="to_transform/conad")
# 	end1 = time.time()

# 	start2 = time.time()
# 	scraper.write_product_dict_to_file(file_name='to_transform/naturasi', add_date_to_filename=True, add_prices=True)
# 	end2 = time.time()
# 	minsec = lambda diff: f"{int(diff)//60}m:{int(diff)%60}s"
# 	message = (f"Job finished in {minsec(end2 - start1)}," +
# 		f"\nThe first scraper started at {datetime.fromtimestamp(start1)}, ended at {datetime.fromtimestamp(end1)}, taking {minsec(end1 - start1)}." +
# 		f"\nThe second scraper started at {datetime.fromtimestamp(start2)}, ended at {datetime.fromtimestamp(end2)}, taking {minsec(end2 - start2)}."
# 	)
# 	formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 	client.message(f"[{formatted_time}] Successfully scraped prices:\n" + message)
# 	print(message)
# except Exception as e:	
# 	formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 	client.message(f"[{formatted_time}] {str(e)}")
# 	print(str(e))

# 	# removing any 0 byte file left from the interruption of the scraping
# 	root = "./data/to_transform"
# 	for file in os.listdir(root):
# 		file_path = root + "/" + file
# 		if os.path.getsize(file_path) == 0:
# 			os.remove(file_path) 
# 	sys.exit(1)


# ut = RUtility()
# ut.add_NAs("data/to_transform")
# ut.add_supermkt("data/to_transform")



# #running the R script that updates all plots for the website
# subprocess.run(
# 	args = ["/usr/local/bin/Rscript", "./R/import_json.R"],
# 	cwd = os.getcwd()
# 	)


# #moving the transformed file in a temporary directory to be deleted every once in a while (to avoid backup issues)
# for file in os.listdir("./data/to_transform"):
# 	source = "./data/to_transform/" + file
# 	dest = "./data/temp/" + file
# 	os.rename(source, dest)

# #running the quarto render function to reflect new data on the web page
# subprocess.run(
# 	args = ["quarto", "render", "./quarto/index.qmd"],
# 	cwd = os.getcwd()
# 	)

subprocess.run(
	args = ["quarto", "preview", "./quarto/index.qmd"],
	cwd = os.getcwd()
	)


