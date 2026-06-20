"""Generate the Fable: TLC-inspired Bedrock form skin and UI-only item art."""

from PIL import Image, ImageDraw

from fc_lib import RP, write_json


UI = RP / "textures" / "ui"
HUD = UI / "fable_hud"
ITEMS = RP / "textures" / "items"

INK = (35, 22, 16, 255)
LEATHER = (63, 38, 25, 255)
LEATHER_LIGHT = (91, 57, 34, 255)
PARCHMENT = (218, 190, 132, 255)
PARCHMENT_LIGHT = (242, 222, 171, 255)
PARCHMENT_DARK = (154, 116, 65, 255)
GOLD = (191, 143, 52, 255)
GOLD_LIGHT = (242, 205, 105, 255)


def save(image: Image.Image, name: str):
    UI.mkdir(parents=True, exist_ok=True)
    image.save(UI / f"{name}.png")


def save_hud(image: Image.Image, name: str):
    HUD.mkdir(parents=True, exist_ok=True)
    image.save(HUD / f"{name}.png")


def panel_texture():
    image = Image.new("RGBA", (18, 33), LEATHER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 17, 32), fill=INK)
    draw.rectangle((1, 1, 16, 31), fill=GOLD)
    draw.rectangle((2, 2, 15, 30), fill=LEATHER_LIGHT)
    draw.rectangle((3, 3, 14, 21), fill=PARCHMENT)
    draw.rectangle((4, 4, 13, 20), fill=PARCHMENT_LIGHT)
    draw.line((3, 22, 14, 22), fill=GOLD_LIGHT)
    draw.rectangle((3, 23, 14, 29), fill=LEATHER)
    draw.point((3, 3), fill=GOLD_LIGHT)
    draw.point((14, 3), fill=GOLD_LIGHT)
    draw.point((3, 29), fill=GOLD_LIGHT)
    draw.point((14, 29), fill=GOLD_LIGHT)
    save(image, "dialog_background_hollow_3")
    write_json(UI / "dialog_background_hollow_3.json", {
        "nineslice_size": [8, 23, 8, 8],
        "base_size": [18, 33],
    })


def button_texture(name: str, fill, edge, highlight, pressed=False):
    image = Image.new("RGBA", (8, 8), fill)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 7, 7), fill=INK)
    draw.rectangle((1, 1, 6, 6), fill=edge)
    draw.rectangle((2, 2, 5, 5), fill=fill)
    if pressed:
        draw.line((2, 2, 5, 2), fill=PARCHMENT_DARK)
        draw.line((2, 2, 2, 5), fill=PARCHMENT_DARK)
    else:
        draw.line((2, 2, 5, 2), fill=highlight)
        draw.line((2, 2, 2, 5), fill=highlight)
    save(image, name)
    write_json(UI / f"{name}.json", {"nineslice_size": 2, "base_size": [8, 8]})


def scroll_textures():
    rail = Image.new("RGBA", (5, 8), INK)
    draw = ImageDraw.Draw(rail)
    draw.rectangle((1, 0, 3, 7), fill=LEATHER_LIGHT)
    draw.line((2, 0, 2, 7), fill=GOLD)
    save(rail, "ScrollRail")
    write_json(UI / "ScrollRail.json", {"nineslice_size": [2, 3, 2, 3], "base_size": [5, 8]})

    handle = Image.new("RGBA", (5, 8), GOLD)
    draw = ImageDraw.Draw(handle)
    draw.rectangle((0, 0, 4, 7), outline=INK)
    draw.rectangle((1, 1, 3, 6), fill=PARCHMENT_DARK)
    draw.line((1, 2, 3, 2), fill=GOLD_LIGHT)
    save(handle, "ScrollHandle")
    write_json(UI / "ScrollHandle.json", {"nineslice_size": [2, 3, 2, 3], "base_size": [5, 8]})


def hud_support_textures():
    """Small authored-style rails used to place live HUD text cleanly."""
    awareness = Image.new("RGBA", (160, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(awareness)
    draw.rounded_rectangle((2, 5, 146, 15), radius=5, fill=INK, outline=GOLD, width=2)
    draw.rounded_rectangle((5, 8, 142, 12), radius=2, fill=(20, 61, 50, 235))
    draw.line((8, 8, 138, 8), fill=(80, 151, 112, 220))
    draw.ellipse((0, 4, 12, 16), fill=INK, outline=GOLD_LIGHT, width=1)
    draw.ellipse((4, 8, 8, 12), fill=(98, 177, 150, 255))
    save_hud(awareness, "awareness_bar")

    details = Image.new("RGBA", (240, 28), (0, 0, 0, 0))
    draw = ImageDraw.Draw(details)
    draw.rounded_rectangle((8, 4, 231, 23), radius=8, fill=(30, 24, 17, 225), outline=INK, width=3)
    draw.rounded_rectangle((10, 6, 229, 21), radius=7, outline=GOLD, width=2)
    draw.line((18, 8, 221, 8), fill=GOLD_LIGHT)
    draw.polygon([(0, 14), (10, 5), (15, 14), (10, 23)], fill=GOLD, outline=INK)
    draw.polygon([(239, 14), (229, 5), (224, 14), (229, 23)], fill=GOLD, outline=INK)
    save_hud(details, "map_details")


def will_focus_icon():
    ITEMS.mkdir(parents=True, exist_ok=True)
    output = ITEMS / "will_focus.png"
    # This is an authored asset; full procedural regeneration must preserve it.
    if output.exists():
        return
    image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Dark handle and warm metal bindings.
    draw.line((5, 27, 21, 11), fill=(20, 30, 54, 255), width=5)
    draw.line((6, 27, 22, 11), fill=(50, 66, 100, 255), width=2)
    draw.line((10, 23, 14, 19), fill=(174, 126, 54, 255), width=3)
    draw.line((14, 19, 18, 15), fill=(224, 184, 82, 255), width=2)
    # Will crystal.
    crystal = [(23, 4), (29, 10), (23, 17), (17, 10)]
    draw.polygon(crystal, fill=(37, 111, 224, 255), outline=(14, 29, 61, 255))
    draw.polygon([(23, 5), (27, 10), (23, 14), (21, 10)], fill=(94, 189, 255, 255))
    draw.line((22, 6, 25, 9), fill=(202, 244, 255, 255), width=2)
    draw.point((28, 5), fill=(223, 250, 255, 220))
    draw.point((29, 4), fill=(223, 250, 255, 160))
    image.save(output)


def main():
    panel_texture()
    button_texture("button_borderless_light", PARCHMENT, PARCHMENT_DARK, PARCHMENT_LIGHT)
    button_texture("button_borderless_lighthover", GOLD, PARCHMENT_DARK, GOLD_LIGHT)
    button_texture("button_borderless_lightpressed", PARCHMENT_DARK, INK, GOLD, pressed=True)
    button_texture("button_borderless_lightpressednohover", PARCHMENT_DARK, INK, GOLD, pressed=True)
    scroll_textures()
    hud_support_textures()
    will_focus_icon()
    print("generated Fable parchment UI skin and Will Focus icon")


if __name__ == "__main__":
    main()
