from PIL import Image

i = 0
key_list = [
    Image.open("frame/0020.png"),
    Image.open("frame/0022.png")
]

key = Image.new("RGB", (133, 100))
for w in range(133):
    for h in range(100):
        if h < 50:
            tmp_key = key_list[0]
            tmp_xy = (w, h)
        else:
            tmp_key = key_list[1]
            tmp_xy = (w, h-50)
        key.putpixel((w, h), tmp_key.getpixel(tmp_xy))

key_90 = key.transpose(Image.ROTATE_90)
key_90.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_90_LR = key_90.transpose(Image.FLIP_LEFT_RIGHT)
key_90_LR.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_90_TB = key_90.transpose(Image.FLIP_TOP_BOTTOM)
key_90_TB.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270 = key.transpose(Image.ROTATE_270)
key_270.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270_LR = key_270.transpose(Image.FLIP_LEFT_RIGHT)
key_270_LR.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270_TB = key_270.transpose(Image.FLIP_TOP_BOTTOM)
key_270_TB.save(f"key/{str(i).zfill(4)}.png")
i += 1

for w in range(133):
    for h in range(100):
        if h < 50:
            tmp_key = key_list[1]
            tmp_xy = (w, h)
        else:
            tmp_key = key_list[0]
            tmp_xy = (w, h-50)
        key.putpixel((w, h), tmp_key.getpixel(tmp_xy))

key_90 = key.transpose(Image.ROTATE_90)
key_90.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_90_LR = key_90.transpose(Image.FLIP_LEFT_RIGHT)
key_90_LR.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_90_TB = key_90.transpose(Image.FLIP_TOP_BOTTOM)
key_90_TB.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270 = key.transpose(Image.ROTATE_270)
key_270.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270_LR = key_270.transpose(Image.FLIP_LEFT_RIGHT)
key_270_LR.save(f"key/{str(i).zfill(4)}.png")
i += 1

key_270_TB = key_270.transpose(Image.FLIP_TOP_BOTTOM)
key_270_TB.save(f"key/{str(i).zfill(4)}.png")
i += 1