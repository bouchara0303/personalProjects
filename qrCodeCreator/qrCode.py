import numpy as np
from PIL import Image

"""
Program for creating Version 4 QR Codes with error correction level M
"""

alphaNumericEncoding = {'0':'0', '1':'1', '2':'2',  '3':'3', '4':'4', '5':'5',
'6':'6', '7':'7', '8':'8', '9':'9', 'A':'10', 'B':'11', 'C':'12', 'D':'13',
'E':'14', 'F':'15', 'G':'16', 'H':'17', 'I':'18', 'J':'19', 'K':'20', 'L':'21',
'M':'22', 'N':'23', 'O':'24', 'P':'25', 'Q':'26', 'R':'27', 'S':'28', 'T':'29',
'U':'30', 'V':'31', 'W':'32', 'X':'33', 'Y':'34', 'Z':'35', ' ':'36', '$':'37',
'%':'38', '*':'39', '+':'40', '-':'41', '.':'42', '/':'43', ':':'44'}

#Create list of modules for encoded data
modules = []

URL = " "
URL = URL.upper()
URLLength = len(URL)

i = 1
for char in URL:
    modules.append(char)
    if (i % 2) == 0:
        char1 = int(alphaNumericEncoding[modules[-2]])
        char2 = int(alphaNumericEncoding[modules[-1]])
        result = bin((45 * char1) + char2)[2:]
        del modules[-2:]
        modules.append(result)
if (URLLength % 2) == 1:
    char2 = int(alphaNumericEncoding[modules[-1]])
    result = bin(char2)[2:]
    del modules[-1]
    # while len(result) !=
    modules.append(result)


#Identify encoding mode for QR code
alphaNumericMode = "0010"

#Identify string length and format it to fit 9 bit block
if URLLength > 90:
    print("""The desired link is too long for QR Code version 4.
     Please consider using a link shortener...""")
    quit()
else:
    URLLength = bin(URLLength)[2:]
    while len(URLLength) != 9:
        URLLength = '0' + URLLength

encodedURL = []
for URLChar in URL:
    if URLChar in alphaNumericEncoding:
        encodedURL.append(bin(int(alphaNumericEncoding[URLChar]))[2:])

#White QR image array
QRCode = np.full([33,33,3], dtype=np.uint8, fill_value=255)

#White orientation block array
orientBlock = np.full([7, 7, 3], dtype=np.uint8, fill_value=255)

#White alignment block array
alignmentBlock = np.full([5, 5, 3], dtype=np.uint8, fill_value=255)

#Always placed besides lower left orientation block
darkModule = np.array([0, 0, 0])

#Version information areas
versionInfo = np.full([6, 3, 3], dtype=np.uint8, fill_value=120)

#Create orientation arrays
for i in range(0, 7):
    for j in range(0, 7):
        if (i == 0) or (i == 6) or (j == 0) or (j == 6):
            orientBlock[j][i] = [0, 0, 0]
        elif (i > 1) and (i < 5) and (j > 1) and (j < 5):
            orientBlock[j][i] = [0, 0, 0]

#Create alignment array
for i in range(0, 5):
    for j in range(0, 5):
        if (i == 0) or (i == 4) or (j == 0) or (j == 4):
            alignmentBlock[j, i] = [0, 0, 0]
alignmentBlock[2, 2] = [0, 0, 0]

#Insert blocks
QRCode[0:7, 26:33] = orientBlock
QRCode[0:7, 0:7] = orientBlock
QRCode[26:33, 0:7] = orientBlock
QRCode[24:29, 24:29] = alignmentBlock
QRCode[26, 8] = darkModule

#Add reserved areas with arbitrary terminating value
for i in range(0, 9):
    for j in range(0, 9):
        if ((i == 8) or (j == 8)) and ([0, 0, 0] not in QRCode[j, i]):
            QRCode[j, i] = [120, 120, 120]
for i in range(25, 33):
    QRCode[8, i] = [120, 120, 120]
for j in range(25, 33):
    QRCode[j, 8] = [120, 120, 120]


#Add version information areas
QRCode[0:6, 23:26] = versionInfo
QRCode[23:26, 0:6] = np.rot90(versionInfo)

for i in range(7, 26):
    if (i % 2) == 0:
        QRCode[6, i] = [0, 0, 0]
        QRCode[i, 6] = [0, 0, 0]

#Output array as png
QRCode = Image.fromarray(QRCode, "RGB")
QRCode.save("GeneratedQRCode.PNG")
