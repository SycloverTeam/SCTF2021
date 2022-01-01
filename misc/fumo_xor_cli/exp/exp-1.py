import re
from PIL import Image

with open("233", "r") as fp:
    farmes = fp.read().split("\x1b[A"*51)

i = 0
farmes.pop(0)
for frame in farmes:
    rgb_list = re.findall(r"\[38;2;(\d*);(\d*);(\d*)m", frame)
    # print(frame)
    img = Image.new("RGB", (133, 50))
    for w in range(img.size[0]):
        for h in range(img.size[1]):
            r, g, b = rgb_list[h * 133 + w]
            img.putpixel((w, h), (int(r), int(g), int(b)))
    img.save(f"frame/{str(i).zfill(4)}.png")
    print(f"Saved frame/{str(i).zfill(4)}.png")
    i += 1

