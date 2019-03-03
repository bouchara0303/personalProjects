import numpy as np
from PIL import Image
from reedSolomon import ReedSolomon

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
data = ""

URL = "google.com"
URL = URL.upper()
URLLength = len(URL)

#Encoding input string
i = 1
for char in URL:
    modules.append(char)
    if (i % 2) == 0:
        char1 = int(alphaNumericEncoding[modules[-2]])
        char2 = int(alphaNumericEncoding[modules[-1]])
        result = bin((45 * char1) + char2)[2:]
        del modules[-2:]
        while len(result) != 11:
            result = '0' + result
        modules.append(result)
    i = i + 1
if (URLLength % 2) == 1:
    char2 = int(alphaNumericEncoding[modules[-1]])
    result = bin(char2)[2:]
    del modules[-1]
    while len(result) != 6:
        result = '0' + result
    modules.append(result)


#Identify encoding mode for QR code
alphaNumericMode = "0010"

#Required number of bits for Version 4-M QR Code
requiredBits = 512

#Identify string length and format it to fit 9 bit block
if URLLength > 90:
    print("""The desired link is too long for QR Code version 4.
     Please consider using a link shortener...""")
    quit()
else:
    URLLength = bin(URLLength)[2:]
    while len(URLLength) != 9:
        URLLength = '0' + URLLength

#Add encoded data from array to form single string
data = alphaNumericMode + URLLength
for block in modules:
    data += block

#Add terminating indicator if encoded string is less than maximum capacity
i = 1
while (len(data) < requiredBits) and (i < 5):
    data += "0"
    i = i + 1

#Add zeros to encoded string until it can be split into bytes
while (len(data) % 8) != 0:
    data += "0"

#Add padding bits if encoded string is too short
i = 1
while len(data) != requiredBits:
    if i % 2 == 1:
        data += "11101100"
    elif i % 2 == 0:
        data += "00010001"
    i = i + 1

#Add codeword bytes to empty array
modules.clear()
modules = [data[i:i + 8] for i in range(0, len(data), 8)]

#Coefficients for reed solomon polynomial
coefficients = []
for codeword in modules:
    coefficients.append(int(codeword, 2))

#Reed solomon error correction codewords
ecBlock1 = ReedSolomon().RSEncode(coefficients[0:32], 18)[32:50]
ecBlock2 = ReedSolomon().RSEncode(coefficients[0:32], 18)[32:50]

#Convert decimal numbers to binary
for i in range(0,18):
    #First block
    temp = bin(ecBlock1[i])[2:]
    while len(temp) < 8:
        temp = "0" + temp
    ecBlock1[i] = temp

    #Second Block
    temp = bin(ecBlock2[i])[2:]
    while len(temp) < 8:
        temp = "0" + temp
    ecBlock2[i] = temp

#Split data codewords into two blocks
block1 = modules[0:32]
block2 = modules[32:64]

#Fill final data list
finalDataList = []
for i in range(0, 32):
    finalDataList.append(block1[i])
    finalDataList.append(block2[i])
for i in range(0, 18):
    finalDataList.append(ecBlock1[i])
    finalDataList.append(ecBlock2[i])

#Create single string of all datablocks
finalDataString = ""
for data in finalDataList:
    finalDataString += data

#Add remainder bits to end of string
finalDataString += "0000000"

#White QR image array
QRCode = np.full([33,33,3], dtype=np.uint8, fill_value=255)

#Empty finder pattern array
orientBlock = np.full([7, 7, 3], dtype=np.uint8, fill_value=255)

#Empty alignment pattern array
alignmentBlock = np.full([5, 5, 3], dtype=np.uint8, fill_value=255)

#Always placed besides lower left orientation block
darkModule = np.array([0, 0, 0])

#Fill finder pattern arrays
for i in range(0, 7):
    for j in range(0, 7):
        if (i == 0) or (i == 6) or (j == 0) or (j == 6):
            orientBlock[j][i] = [0, 0, 0]
        elif (i > 1) and (i < 5) and (j > 1) and (j < 5):
            orientBlock[j][i] = [0, 0, 0]

#Fill alignment pattern arrays
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

#Fill timing patterns
for i in range(7, 26):
    if (i % 2) == 0:
        QRCode[6, i] = [0, 0, 0]
        QRCode[i, 6] = [0, 0, 0]

i = 32
j = 32
deltaI = 0
deltaJ = 0
column = 1
subcolumn = 1
direction = 1
maxQRIndex = 32
for x in range(0, len(finalDataString)):
    #Convert data to array blocks
    if finalDataString[x] == '1':
        colorFill = [0, 0, 0]
    else:
        colorFill = [255, 255, 255]

    #Determine direction of fill
    if (column % 2) == 1:
        direction = 1
    elif (column % 2) == 0:
        direction = -1

    #Determine which subcolumn of the column the coordinates are in
    if (subcolumn % 2) == 1:
        deltaJ = 0
        deltaI = -1
    elif (subcolumn % 2) == 0:
        deltaJ = -direction
        deltaI = 1

    #Reverse once reaching reserved zone under upper right finder pattern
    if (i >= (maxQRIndex - 7)) and (j == 9) and ((subcolumn % 2) == 0) and (direction > 0):
        direction = -direction
        deltaJ = 0
        deltaI = -1
        column += 1
    #Reverse once reaching bottom of QRCode
    elif((i >= 9) and (i <= maxQRIndex) and (j == maxQRIndex) and (direction < 0)):
        direction = -direction
        column += 1
        deltaJ = 0
        deltaI = -1
    #Shift left once reaching alignment pattern
    elif ((j <= 28) and (j >= 24) and ((subcolumn % 2) == 0) and (i == (maxQRIndex - 9))):
        deltaJ = -1
        deltaI = 0
        subcolumn -= 1
    #Skip over timing pattern moving up
    elif((i <= 24) and (i >= 9) and (j == 7) and (subcolumn % 2 == 0) and (direction > 0)):
        deltaJ = 2
        deltaI = 1
    #Skip over timing pattern moving down
    elif((i <=24) and (i >= 9) and (j == 5) and (subcolumn % 2 == 0) and (direction < 0)):
        deltaJ = -2
        deltaI = 1
    #Reverse once reaching the top
    elif((i <=24) and (i >= 9) and (j == 0) and (subcolumn % 2 ==0) and (direction > 0)):
        direction = -direction
        column += 1
        deltaJ = 0
        deltaI = -1
    #Shift between lower left finder pattern and upper left reserved zone
    elif((i == 9) and (j == maxQRIndex)):
        deltaJ = -8
        deltaI = -1
    #Shift over vertical timing pattern
    elif((i == 7) and (j == 9)):
        column += 1
        deltaJ = 0
        deltaI = -2
    #Change directions between high and low finder patterns while moving up
    elif((i >=0) and (i <= 5) and (j == 9) and (direction > 0) and (subcolumn % 2 == 0)):
        direction = -direction
        deltaJ = 0
        deltaI = -1
    #Change directions between high and low finder patterns while moving down
    elif((i >=0) and (i <= 5) and (j == maxQRIndex - 8) and (direction < 0) and (subcolumn % 2 == 0)):
        direction = -direction
        deltaJ = 0
        deltaI = -1

    #Fill current coordinates
    QRCode[j, i] = colorFill

    #Update coordinates and subcolumn
    i += deltaI
    j += deltaJ
    subcolumn += 1



#Output array as png
QRCode = Image.fromarray(QRCode, "RGB")
QRCode.save("GeneratedQRCode.PNG")
