# FUMO_xor_cli

# How to start and stop

## start
```
docker-compose up -d
```

## stop
```
docker-compose down --rmi all
```

# writeup
nc可以发现一串命令行的动画，将其下载到文件`nc 124.70.150.39 2333 > 233`。

观察到每个帧直接是有51个`\xb1[A`可以以此为分界线提取图片：

```python
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


```

可以发现1~2个不一样的图片
![image-20211222165546964](https://gitee.com/AFKL/image/raw/master/img/image-20211222165546964.png)

同时nc中存在一个网址，是赛前的宣传。https://mp.weixin.qq.com/s/E_iDJBkVEC4jZanzvqnWCA
将其最后一张特供的图片下载下来，发现其每个9x9的方格内有一个不一样的像素点。将其提取出一个100x133的图片。
```python
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
```

发现之前提取出的2张图片的规格是50x133，可以想到将其合并后，与上面提取出来的`data.png`进行处理。
```python
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
```

最后在尝试将两者之间的每个像素点异或时可以得到flag
```python
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
```

![image-20211222170023658](https://gitee.com/AFKL/image/raw/master/img/image-20211222170023658.png)

