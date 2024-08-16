import yaml

with open('diameter_avp.yaml', 'r') as file:
    data = yaml.safe_load(file)
diameter_fields = data.get('diameter_fields', [])

with open('avp_values.yaml', 'r') as file:
    avp_values = yaml.safe_load(file)
