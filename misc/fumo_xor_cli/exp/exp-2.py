from PIL import Image

x, y = 0, 0
a = Image.open("a3.png")
flag = Image.new("RGB", (100, 133))
for w in range(0, a.size[0] - 8, 9):
    for h in range(0, a.size[1] - 8, 9):
        r,g,b,_ = a.getpixel((w+1, h+1))
        rgba = flag.putpixel((x, y), (r,g,b))
        y += 1
    x += 1
    y = 0

flag.save("data.png")