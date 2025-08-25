import json

with open("data.json", "r") as fs:
	data = json.loads(fs.read())
	data_tagged = {row["tag"]: row["ano"] for row in data}
with open("data_complete.json", "r") as fs:
	data_complete = json.loads(fs.read())

new_data = []
for row in data_complete:
	new_data.append(row | {"year": data_tagged[row["tag"]]})

with open("../data_complete.json", "w") as fs:
	fs.write(json.dumps(new_data, indent=4))