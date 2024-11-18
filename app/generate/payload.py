from copy import deepcopy
import json

with open('payloads/payload_male_template.json', 'r') as file:
    male_payload_template = json.load(file)

with open('payloads/payload_female_template.json', 'r') as file:
    female_payload_template = json.load(file)


def generate_payload(image_url,
                     description,
                     jacket_color,
                     background_color,
                     agression,
                     strength,
                     upscale,
                     is_male):
    if (is_male):
        payload = deepcopy(male_payload_template)
    else:
        payload = deepcopy(female_payload_template)

    set_description(payload, description, strength)
    set_jacket(payload, jacket_color)
    set_agression(payload, agression)

    set_background_color(payload, background_color)
    set_upscale(payload)

    set_image_url(payload, image_url)

    return payload


def set_upscale(payload):
    return


def set_image_url(payload, image_url):
    payload["input"]["workflow"]["1250"]["inputs"]["url_or_path"] = image_url


def set_description(payload, description, strength):
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = (
        payload["input"]["workflow"]["1106"]["inputs"]["Text"]
        .replace("{DESCRIPTION}", f"{strength}, {description}")
    )


def set_background_color(payload, background_color):
    if (background_color == 'transparent'):
        payload["input"]["workflow"]["1254"]["inputs"]["images"] = ["1231", 0]
    else:
        payload["input"]["workflow"]["1230"]["inputs"]["color"] = (
            background_color
        )


def set_agression(payload, agression):
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = (
        payload["input"]["workflow"]["1106"]["inputs"]["Text"]
        .replace("{AGRESSION}", str(agression))
    )


def set_jacket(payload, jacket_color):
    payload["input"]["workflow"]["1106"]["inputs"]["Text"] = (
        payload["input"]["workflow"]["1106"]["inputs"]["Text"]
        .replace("{JACKET_COLOR}", jacket_color)
    )
