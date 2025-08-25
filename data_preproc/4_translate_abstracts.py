import threading
from googletrans import Translator
import asyncio
import json
from time import sleep
import random as rd
from datetime import datetime, timedelta
import os

def strfdelta(tdelta):
	d = {"days": tdelta.days}
	d["hours"], rem = divmod(tdelta.seconds, 3600)
	d["minutes"], d["seconds"] = divmod(rem, 60)
	
	return "%02d:%02d:%02d"%(d["hours"],d["minutes"],d["seconds"])


def create_or_load(json_filename: str, parameter_creator) -> list:
	data: list = []
	if json_filename in os.listdir():
		with open(json_filename, "r", encoding="utf8") as fs:
			data = json.loads(fs.read())
	else:
		data = parameter_creator()
		with open(json_filename, "w", encoding="utf8") as fs:
			fs.write(json.dumps(data, indent=4))

	return data


def acompanhamento():
	global finished_threads
	global new_data
	global queue
	global THREAD_COUNT

	start = datetime.now()
	while finished_threads < THREAD_COUNT:
		delta = datetime.now()-start
		print("%s - %6d / %6d (%5.2f %%) - %2d of %2d finished - ETA = %s"%(
			strfdelta(delta),
			len(new_data),
			len(queue),
			100*len(new_data)/(len(queue)+1),
			finished_threads,
			THREAD_COUNT,
			strfdelta(timedelta(seconds=delta.seconds*len(queue)/(1+len(new_data))) - delta)
		))
		sleep(1)


async def translate(j):
	global new_data
	global queue
	global HOW_MANY_PER_THREAD

	for i in range(HOW_MANY_PER_THREAD):
		for k in range(5):
			try:
				idx0 = int((len(queue)/THREAD_COUNT)*j) + i
				line = queue[idx0]
				translation = await Translator().translate(queue[idx0]["abstract"], "en")
				new_data |= {line["tag"]: translation.text}
				break

			except Exception as e:
				print(f"\n ERRO {k+1} DE 5 NA THREAD {j} PROCESSANDO O ITEM {idx0}\n\t{e}\n")
				sleep(rd.randrange(100,1000)/100)


def run_threads(n, do_print=False) -> int:
	global finished_threads
	start = datetime.now()
	threads = []
	for i in range(n):
		threads.append(threading.Thread(target=asyncio.run, args=(translate(i),)))

	if do_print:
		threads.append(threading.Thread(target=acompanhamento))

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
		finished_threads += 1
	
	elapsed = datetime.now() - start

	return elapsed.seconds

	
INPUT_FILE: str = input("Enter input (portuguese WITH ABSTRACTS) file name (blank for data.json): ")
INPUT_EN_FILE: str = input("Enter input (english WITHOUT ABSTRACTS) file name (blank for data_en.json): ")
OUTPUT_FILE: str = input("Enter output (english final) file name (blank for data_complete.json): ")

if not INPUT_FILE:
	INPUT_FILE = "data.json"
	
if not INPUT_EN_FILE:
	INPUT_EN_FILE = "data_en.json"

with open(INPUT_FILE, "r", encoding="utf8") as fs:
	data = json.loads(fs.read())

with open(INPUT_EN_FILE, "r", encoding="utf8") as fs:
	data_en = json.loads(fs.read())

if not OUTPUT_FILE:
	OUTPUT_FILE = "data_complete.json"

def fetch():
	global finished_threads
	global new_data
	global queue
	global THREAD_COUNT

	print(len(queue))

	time_elapsed = 1 + run_threads(THREAD_COUNT, True)
	print(f"{THREAD_COUNT}: {THREAD_COUNT/time_elapsed}")

	print(len(new_data))
	return new_data


queue = [line for line in data if line["abstract"] != ""]
new_data: dict = {}
finished_threads = 0

THREAD_COUNT = 80
HOW_MANY_PER_THREAD = int(len(queue)/(THREAD_COUNT))

new_data = create_or_load("temp.json", fetch)

data_complete: list = []
for line in data_en:
	if line["tag"] not in new_data:
		line["abstract"] = ""
	else:
		line["abstract"] = new_data[line["tag"]]
	data_complete.append(line)

with open(OUTPUT_FILE, "w", encoding="utf8") as fs:
	fs.write(json.dumps(data_complete, indent=4))
