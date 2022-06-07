from ctypes import c_uint8
from PIL import Image
qoi_list = []
qoi_header = []
read_values = []
with open('./qoi_test_images/dice.qoi', 'rb') as binary_file:
    read_values = [x for x in binary_file.read()]
    qoi_list = read_values[14:-8]
    qoi_header = read_values[:14]
    binary_file.close()

index_position = lambda r, g, b, a : ((r*3 + g*5 + b*7 + a*11)%64)

i = 0;
index_list = [(0, 0, 0, 0)] * 64

decoded_image = []
run_length = 0
px = [0, 0, 0, 255]
index_list[int(index_position(px[0], px[1], px[2], px[3]))] = tuple(px)
while(i < len(qoi_list)):
    b = qoi_list[i]
    if run_length > 0:
        while run_length:
            decoded_image.append(tuple(px))
            run_length -= 1;
        i += 1
    else:
        if(b == 0b11111110):
            i += 1
            px[0] = qoi_list[i]
            px[1] = qoi_list[i + 1]
            px[2] = qoi_list[i + 2]
            decoded_image.append(tuple(px))
            i += 3
        elif(b == 0b11111111):
            i += 1
            px[0] = qoi_list[i]
            px[1] = qoi_list[i + 1]
            px[2] = qoi_list[i + 2]
            px[3] = qoi_list[i + 3]
            decoded_image.append(tuple(px))
            i += 4
        elif ((b & 0b11000000) == 0b00000000):
            px = list(index_list[b])
            decoded_image.append(tuple(px))
            i += 1
        elif ((b & 0b11000000) == 0b01000000):
            px[0] += ((b >> 4) & 3) - 2
            px[1] += ((b >> 2) & 3) - 2
            px[2] += ( b       & 3) - 2
            px[0] = c_uint8(px[0]).value
            px[1] = c_uint8(px[1]).value
            px[2] = c_uint8(px[2]).value
            decoded_image.append(tuple(px))
            i += 1
        elif ((b & 0b11000000) == 0b10000000):
            b2 = qoi_list[i + 1];
            vg = (b & 0x3f) - 32;
            px[0] += vg - 8 + ((b2 >> 4) & 0x0f);
            px[1] += vg
            px[2] += vg - 8 +  (b2 & 0x0f)
            px[0] = c_uint8(px[0]).value
            px[1] = c_uint8(px[1]).value
            px[2] = c_uint8(px[2]).value
            decoded_image.append(tuple(px))
            i += 2
        elif ((b & 0b11000000) == 0b11000000):
            run_length = (b & 0x3f) + 1
        index_list[int(index_position(px[0], px[1], px[2], px[3]))] = tuple(px)

img = Image.new('RGB', ((
    qoi_header[4] << 24 | qoi_header[5] << 16 | qoi_header[6] << 8 | qoi_header[7]), 
    qoi_header[8] << 24 | qoi_header[9] << 16 | qoi_header[10] << 8 | qoi_header[11]
    )).convert('RGBA')
img.putdata(decoded_image)
img.save('new.png')
img.show()
    