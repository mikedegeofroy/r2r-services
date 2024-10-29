from copy import deepcopy
import json

with open('payloads/payload_male_template.json', 'r') as file:
    male_payload_template = json.load(file)

with open('payloads/payload_female_template.json', 'r') as file:
    female_payload_template = json.load(file)

def generate_payload(image_url, description, jacket_color, background_color, agression, strength, is_male):
    # Create a copy of the template to avoid modifying the original
    if (is_male):
      payload = deepcopy(male_payload_template)
    else:
      payload = deepcopy(female_payload_template)

    # Replacing the description with the description of the person
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = payload["input"]["workflow"]["1106"]["inputs"][
        "Text"
    ].replace("{DESCRIPTION}", f"{strength}, {description}")
    
    # Jacket Color
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = payload["input"]["workflow"]["1106"]["inputs"][
        "Text"
    ].replace("{JACKET_COLOR}", jacket_color)
    
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = payload["input"]["workflow"]["1106"]["inputs"][
        "Text"
    ].replace("{AGRESSION}", str(agression))
    
    # Setting bg color
    
    print(background_color)
    
    if (background_color == 'transparent'):
      payload["input"]["workflow"]["1254"]["inputs"]["images"] = ["1231", 0]
    else:
      payload["input"]["workflow"]["1230"]["inputs"]["color"] = background_color

    payload["input"]["workflow"]["1250"]["inputs"]["url_or_path"] = image_url

    return payload
