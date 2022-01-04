# in_the_vaporwaves

# writeup

此题的音频的左右声道被反相了，且左右声道的波形上下相反。那么可以尝试将左右声道的波形相加。
```python
import wave
import struct

with wave.open("c.wav", "rb") as c:
    with wave.open("a.wav", "wb") as a:
        a.setnchannels(1)
        a.setsampwidth(1)
        a.setframerate(44100)

        for i in range(c.getnframes()):
            L, R = struct.unpack('hh', c.readframes(1))
            data = L + R

            a_data = struct.pack('h', data)
            a.writeframes(a_data)

```

获得`a.wav`，发现有一段莫斯电码。

![image-20211222142149332](https://gitee.com/AFKL/image/raw/master/img/image-20211222142149332.png)

![qq_pic_merged_1640154750159](https://gitee.com/AFKL/image/raw/master/img/qq_pic_merged_1640154750159.jpg)

获得flag

