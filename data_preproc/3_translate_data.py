import threading
from googletrans import Translator
import asyncio
import json
from time import sleep
import random as rd
from datetime import datetime, timedelta
print("imported")


def strfdelta(tdelta):
	d = {"days": tdelta.days}
	d["hours"], rem = divmod(tdelta.seconds, 3600)
	d["minutes"], d["seconds"] = divmod(rem, 60)
	
	return "%02d:%02d:%02d"%(d["hours"],d["minutes"],d["seconds"])


def acompanhamento():
	global finished_threads
	start = datetime.now()
	while finished_threads < THREAD_COUNT:
		#eta = (i * len(data)) / (len(new_data)+1) - i
		delta = datetime.now()-start
		print("%s - %6d / %6d (%5.2f %%) - %2d of %2d finished - ETA = %s"%(
			strfdelta(delta),
			len(new_data),
			len(data),
			100*len(new_data)/(len(data)+1),
			finished_threads,
			THREAD_COUNT,
			strfdelta(timedelta(seconds=delta.seconds*len(data)/(1+len(new_data))) - delta)
		))
		sleep(2)


async def translate(j):
	for i in range(HOW_MANY_PER_THREAD):
		for k in range(5):
			try:
				idx0 = int((len(data)/THREAD_COUNT)*j) + i*HOW_MANY_PER_REQUEST
				text = ""
				lines = [data[idx0+l] for l in range(HOW_MANY_PER_REQUEST)]
				text =		     "\n".join([line["title"]    for line in lines])
				abstracts = "\n;;;\n".join(["{"+line["abstract"]+"}" for line in lines])

				translation = await Translator().translate(text + "\n///\n" + abstracts, "en")
				#print(str(i*THREAD_COUNT + j).ljust(4) + "    " + translation.text)
				trans_text, trans_abstracts = translation.text.split("\n///\n")
				trans_text_list = trans_text.split("\n")
				trans_abstracts_list = [element.strip("}{") for element in trans_abstracts.split("\n;;;\n")]
				for m in range(len(lines)):
					line = lines[m]
					new_data.append({"lattes":line["lattes"], "areas":line["areas"], "tag":line["tag"], "title":trans_text_list[m], "doi":line["doi"], "abstract":trans_abstracts_list[m]})
				break
			except IndexError as e:
				print(f"\n ERRO {k+1} DE 5 NA THREAD {j} PROCESSANDO O BLOCO {idx0}:{idx0+HOW_MANY_PER_REQUEST}\n\t{e}\n")
				#print(len(lines), len(trans_text_list), len(trans_abstracts_list))
				print(text + "\n///\n" + abstracts + "\n|\nV\n\n" + translation.text)
				break
			except Exception as e:
				print(f"\n ERRO {k+1} DE 5 NA THREAD {j} PROCESSANDO O BLOCO {idx0}:{idx0+HOW_MANY_PER_REQUEST}\n\t{e}\n")
				sleep(rd.randrange(100,1000)/100)

				if "too long" in str(e):
					print(f"\tFAZENDO UM POR UM... \n")
					for line in lines:
						try:
							translation = await Translator().translate(line["title"] + "\n///\n" + line["abstract"])
							trans_text, trans_abstracts = translation.text.split("\n///\n")
							new_data.append({"lattes":line["lattes"], "areas":line["areas"], "tag":line["tag"], "title":trans_text, "doi":line["doi"], "abstract":trans_abstracts})
						except:
							continue
					break

async def translate(j):
	for i in range(HOW_MANY_PER_THREAD):
		for k in range(5):
			try:
				idx0 = int((len(data)/THREAD_COUNT)*j) + i*HOW_MANY_PER_REQUEST
				text = ""
				lines = [data[idx0+l] for l in range(HOW_MANY_PER_REQUEST)]
				text =		     "\n".join([line["title"]    for line in lines])

				translation = await Translator().translate(text, "en")
				#print(str(i*THREAD_COUNT + j).ljust(4) + "    " + translation.text)
				trans_text = translation.text
				trans_text_list = trans_text.split("\n")
				for m in range(len(lines)):
					line = lines[m]
					new_data.append({"lattes":line["lattes"], "areas":line["areas"], "tag":line["tag"], "title":trans_text_list[m], "doi":line["doi"], "abstract":""})
				break

			except Exception as e:
				print(f"\n ERRO {k+1} DE 5 NA THREAD {j} PROCESSANDO O BLOCO {idx0}:{idx0+HOW_MANY_PER_REQUEST}\n\t{e}\n")
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


INPUT_FILE: str = input("Enter input (portuguese) file name (blank for data.json): ")
OUTPUT_FILE: str = input("Enter output (english) file name (blank for data_en.json): ")

if not INPUT_FILE:
	INPUT_FILE = "data.json"
	
if not OUTPUT_FILE:
	OUTPUT_FILE = "data_en.json"

with open(INPUT_FILE, "r", encoding="utf8") as fs:
	data = json.loads(fs.read())

print("data loaded")

THREAD_COUNT = 80
HOW_MANY_PER_REQUEST = 25
HOW_MANY_PER_THREAD = int(len(data)/(THREAD_COUNT*HOW_MANY_PER_REQUEST))

new_data = []
finished_threads = 0

time_elapsed = 1 + run_threads(THREAD_COUNT, True)
print(f"{THREAD_COUNT}: {THREAD_COUNT/time_elapsed}")

with open(OUTPUT_FILE, "w", encoding="utf8") as fs:
	fs.write(json.dumps(new_data, indent=4))

	
