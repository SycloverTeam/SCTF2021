from PIL import Image

i = 0
data = Image.open("data.png")
for i in range(12):
    xor = Image.new("RGB", (100, 133))
    key = Image.open(f"key/{str(i).zfill(4)}.png")
    for w in range(100):
        for h in range(133):
            r1, g1, b1 = key.getpixel((w, h))
            r2, g2, b2, _ = data.getpixel((w, h))
            xor.putpixel((w, h), (r1^r2, g1^g2, b1^b2))
    xor.save(f"xor/{str(i).zfill(4)}.png")