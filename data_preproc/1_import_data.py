import xml.etree.ElementTree as ET
import os
import html
import json
from unidecode import unidecode
from hashlib import shake_128


DATA_FILE: str = input("Enter data file name (blank for data.json): ")
if not DATA_FILE:
	DATA_FILE = "data.json"


def decode(s) -> str:
	return unidecode(s).replace("_", " ").strip().lower()


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


def extract_area_name(root: ET.Element) -> str:
	if "AREA-DO-CONHECIMENTO" not in root.tag:
		raise(Exception)
	
	hierarchy: list = [
		"NOME-DA-ESPECIALIDADE",
		"NOME-DA-SUB-AREA-DO-CONHECIMENTO",
		"NOME-DA-AREA-DO-CONHECIMENTO",
		"NOME-GRANDE-AREA-DO-CONHECIMENTO",
	]
	
	for level in hierarchy:
		if root.attrib[level] != "":
			return root.attrib[level]
		
	return ""


def dfs(root: ET.Element) -> list:
	dados_basicos: ET.Element = None
	areas_do_conhecimento: ET.Element = None

	output: list = []

	for child in root:
		if "DADOS-BASICOS-D" in child.tag:
			dados_basicos = child
		elif "AREAS-DO-CONHECIMENTO" in child.tag:
			areas_do_conhecimento = child
	
	if dados_basicos == None:
		for child in root:
			output += dfs(child)
		return output

	titulo = ""
	ano = None
	doi = None
	for key in dados_basicos.attrib:
		if "TITULO" in key and (titulo == "" or ("INGLES" in key and html.unescape(dados_basicos.attrib[key]) != "")):
			titulo = html.unescape(dados_basicos.attrib[key])
		elif "ANO" in key and ano == None:
			ano = int(html.unescape(dados_basicos.attrib[key])) if dados_basicos.attrib[key] != "" else 0
		elif key == "DOI" and doi == None:
			doi = html.unescape(dados_basicos.attrib[key])

		if titulo != "" and ano != None and doi != None:
			break

	if titulo == "":
		return output
	
	output += [{
		"tag": shake_128(titulo.encode()).hexdigest(10),
		"title": titulo,
		"areas": [],
		"ano": ano,
		"doi": doi,
	}]

	if areas_do_conhecimento == None:
		return output
	
	for area in areas_do_conhecimento:
		area_name = extract_area_name(area)
		if area_name != "":
			output[0]["areas"].append(decode(area_name))

	return output


data = []
if DATA_FILE in os.listdir():
	with open(DATA_FILE, "r", encoding="utf8") as fs:
		data = json.loads(fs.read())

else:
	filenames = os.listdir('lattes')
	for i in range(len(filenames)):
		filename = filenames[i]
		tree = ET.parse('lattes/' + filename)
		root = tree.getroot()

		lattes_data: list = dfs(root)
		for line in lattes_data:
			line |= {"lattes": filename[:-4]}
			line["tag"] = line["lattes"] + "-" + line["tag"]

		data += lattes_data
		print(
			"Processing...   |" +
			"=" * int(100*i/len(filenames)) +
			" " * int(100*(len(filenames)-i)/len(filenames)) +
			"| %5.2f %%"%(100*(i+1)/len(filenames)),
			end="\r")
	print("All data parsed!")
	
	with open(DATA_FILE, "w", encoding="utf8") as fs:
		fs.write(json.dumps(data, indent=4))
		
for line in data[:20]:
	print(line)