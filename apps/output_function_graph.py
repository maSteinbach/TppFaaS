import sys
import yaml

with open(f"{sys.argv[1]}/serverless.yaml", "r") as f:
    try:
        data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(e)
result = {}
for fname, value in data["functions"].items():
    parameters = value["parameters"]
    if "nextFn" in parameters:
        result[fname] = [parameters["nextFn"]]
    else:
        result[fname] = "None"
print(yaml.dump(result))