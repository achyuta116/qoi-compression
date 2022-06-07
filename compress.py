from ctypes import c_int8
from PIL import Image

im = Image.open('./qoi_test_images/wikipedia_008.png').convert('RGBA')
qoi_magic = [ord('q'), ord('o'), ord('i'), ord('f')]
qoi_padding = [0, 0, 0, 0, 0, 0, 0, 1]
channels = len(im.getbands())

index_position = lambda r, g, b, a = 255  : ((r*3 + g*5 + b*7 + a*11) %64)
pixel_values = list(im.getdata())
with open('a.txt', 'w') as o:
    for pixel in pixel_values:
        print(list(pixel), file=o)
    o.close()
index_list = [(0, 0, 0, 0)] * 64

qoi_list = []
i = 1
px = [0, 0, 0, 255]
pixel_values.insert(0, tuple(px))
run_length = 0
pos = index_position(pixel_values[0][0], pixel_values[0][1], pixel_values[0][2], pixel_values[0][3])
index_list[pos] = tuple(pixel_values[0])

while(i < len(pixel_values)):
    # Run Length
    if(pixel_values[i][3] == pixel_values[i - 1][3]):
        if(pixel_values[i] == pixel_values[i - 1]
            and run_length < 61):
            if(run_length == 0):
                run_length += 1
                qoi_list.append(192)
            else:
                qoi_list[-1] += 1
                run_length += 1
        else:
            pos = index_position(pixel_values[i][0], pixel_values[i][1], pixel_values[i][2], pixel_values[i][3])
            if(run_length > 0):
                run_length = 0
            # Hash Index
            if(index_list[pos] == pixel_values[i]):
                qoi_list.append(pos)
            else:
                # Calculate differences
                index_list[pos] = pixel_values[i]
                vr = c_int8((pixel_values[i][0] - pixel_values[i - 1][0])).value
                vg = c_int8((pixel_values[i][1] - pixel_values[i - 1][1])).value
                vb = c_int8((pixel_values[i][2] - pixel_values[i - 1][2])).value

                vg_r = c_int8(vr - vg).value
                vg_b = c_int8(vb - vg).value
            
                if(vr > -3 and vr < 2 and vg > -3 and vg < 2 and vb > -3 and vb < 2):
                    qoi_list.append(0x40 | (vr + 2) << 4 | (vg + 2) << 2 | (vb + 2))
                elif(vg_r > -9 and vg_r < 8 and vg > -33 and vg < 32 and vg_b > -9 and vg_b < 8):
                    qoi_list.append(0x80 | (vg + 32))
                    qoi_list.append((vg_r + 8) << 4 | (vg_b +  8))
                    
                else:
                    qoi_list += [254, pixel_values[i][0],pixel_values[i][1],pixel_values[i][2]]
    else:
        if(run_length > 0):
            run_length = 0
        pos = index_position(pixel_values[i][0], pixel_values[i][1], pixel_values[i][2], pixel_values[i][3])
        index_list[pos] = pixel_values[i]
        qoi_list += [255, pixel_values[i][0],pixel_values[i][1],pixel_values[i][2], pixel_values[i][3]]
    px = pixel_values[i]
    i += 1

try:
    with open('b.qoi', 'wb') as o:
        o.write(bytes(bytearray(qoi_magic))+
        im.size[0].to_bytes(4, 'big')+
        im.size[1].to_bytes(4, 'big')+
        (channels).to_bytes(1, 'big')+
        (0).to_bytes(1, 'big')+
        bytes(bytearray(qoi_list)+bytearray(qoi_padding)))
        o.close()
finally:
    with open('qoivalues.txt', 'w') as o:
        for i in qoi_list:
            print(i, file=o)
        o.close()