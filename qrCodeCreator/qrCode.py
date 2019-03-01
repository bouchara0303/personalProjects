import numpy as np
from PIL import Image

#White QR image array
QRCode = np.full([33,33,3], dtype=np.uint8, fill_value=255)

#White orientation block array
orientBlock = np.full([7, 7, 3], dtype=np.uint8, fill_value=255)


#Create orientation arrays
for i in range(0, 7):
    for j in range(0, 7):
        if (i == 0) or (i == 6) or (j == 0) or (j == 6):
            orientBlock[i][j] = [0, 0, 0]
        elif (i > 1) and (i < 5) and (j > 1) and (j < 5):
            orientBlock[i][j] = [0, 0, 0]

QRCode[0:7, 26:34] = orientBlock
QRCode[0:7, 0:7] = orientBlock
QRCode[26:34, 0:7] = orientBlock

for i in range(7, 26):
    if (i % 2) == 0:
        QRCode[6, i] = [0, 0, 0]
        QRCode[i, 6] = [0, 0, 0]

QRCode = Image.fromarray(QRCode, "RGB")
QRCode.save("GeneratedQRCode.PNG")
