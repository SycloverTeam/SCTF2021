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
