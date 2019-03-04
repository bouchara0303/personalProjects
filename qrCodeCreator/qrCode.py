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

###############Encoding data###############

URL = "github.com"
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

###############Filling QR Code with orientation patterns###############

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

#Fill timing patterns
for i in range(7, 26):
    if (i % 2) == 0:
        QRCode[6, i] = [0, 0, 0]
        QRCode[i, 6] = [0, 0, 0]

###############Placing data and EC modules###############

#Function for better readability
def isBetween(num, x1, x2):
    return ((num >= x1) and (num <= x2))

#Location of data coordinates
dataCoordinates = []

i = 32
j = 32
deltaI = 0
deltaJ = 0
column = 1
subColumn = 1
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

    #Boolean expressions for readability
    up = (direction > 0)
    down = (direction < 0)
    leftSubColumn = ((subColumn % 2) == 0)

    #Determine which subColumn of the column the coordinates are in
    if (subColumn % 2) == 1:
        deltaJ = 0
        deltaI = -1
    elif (subColumn % 2) == 0:
        deltaJ = -direction
        deltaI = 1

    #Reverse once reaching reserved zone under upper right finder pattern
    if (isBetween(i, (maxQRIndex - 7), maxQRIndex) and (j == 9) and leftSubColumn and up):
        column += 1
        deltaJ = 0
        deltaI = -1
    #Reverse once reaching bottom of QRCode
    elif(isBetween(i, 9, maxQRIndex) and (j == maxQRIndex) and leftSubColumn and down):
        column += 1
        deltaJ = 0
        deltaI = -1
    #Jump over alignment pattern moving up
    elif(isBetween(i, 25, 28) and (j == 29) and leftSubColumn and up):
        deltaJ = -6
        deltaI = 1
    #Jump over alignment pattern moving down
    elif(isBetween(i, 25, 28) and (j == 23) and leftSubColumn and down):
        deltaJ = 6
        deltaI = 1
    # Shift left once reaching alignment pattern
    elif (isBetween(j, 25, 29) and leftSubColumn and (i == maxQRIndex - 9)):
        deltaJ = -1
        deltaI = 0
        subColumn -= 1
    #Skip over timing pattern moving up
    elif(isBetween(i, 9, 24) and (j == 7) and leftSubColumn and up):
        deltaJ = -2
        deltaI = 1
    #Reverse once reaching the top
    elif(isBetween(i, 9, 24) and (j == 0) and leftSubColumn and up):
        column += 1
        deltaJ = 0
        deltaI = -1
    #Skip over timing pattern moving down
    elif(isBetween(i, 9, 24) and (j == 5) and leftSubColumn and down):
        deltaJ = 2
        deltaI = 1
    #Shift over vertical timing pattern
    elif((i == 7) and (j == 9)):
        column += 1
        deltaJ = 0
        deltaI = -2
    #Change directions between high and low finder patterns while moving up
    elif(isBetween(i, 0, 5) and (j == 9) and up and leftSubColumn):
        column += 1
        deltaJ = 0
        deltaI = -1
    #Change directions between high and low finder patterns while moving down
    elif(isBetween(i, 0, 5) and (j == maxQRIndex - 8) and down and leftSubColumn):
        column += 1
        deltaJ = 0
        deltaI = -1

    #Shift between lower left finder pattern and upper left reserved zone
    if((i == 9) and (j == maxQRIndex)):
        deltaJ = -8
        deltaI = -1

    #Fill current coordinates
    QRCode[j][i] = colorFill

    #Add coordinates to list
    dataCoordinates.append((i, j))

    #Update coordinates and subColumn
    i += deltaI
    j += deltaJ
    subColumn += 1

###############Masking data pattern###############

#Create list describing full QR code rows and columns
totalQRString = ""
for y in range(0, maxQRIndex + 1):
    for x in range(0, maxQRIndex + 1):
        if ([0, 0, 0] in QRCode[y, x]):
            totalQRString += "1"
        else:
            totalQRString += "0"
totalQRList = [totalQRString[x: x + maxQRIndex + 1] for x in range(0, len(totalQRString), (maxQRIndex + 1))]


#Give penalty score to different masks
def maskEval(QRList):
    score = 0
    i = 0

    #####Score for 5 or more consecutive modules of same color in row/column#####
    #Row penalty score
    for row in QRList:
        #Iterate over row
        while(i <= maxQRIndex):
            count = 1
            while(((i + 1) < maxQRIndex) and (row[i] == row[i + 1])):
                count += 1
                i += 1
            if (count >= 5):
                score += 3 + (count - 5)
            i += 1

    #Change list to iterate over columns
    columnList = []
    column = ""
    for i in range(0, (maxQRIndex + 1)):
        for row in QRList:
            column += row[i]
        columnList.append(column)
        column = ""

    #Column penalty score
    for column in columnList:
        #Iterate over row
        i = 0
        while(i < maxQRIndex):
            count = 1
            while(((i + 1) < maxQRIndex) and (row[i] == row[i + 1])):
                count += 1
                i += 1
            if (count >= 5):
                score += 3 + (count - 5)
            i += 1

    #####Score for number of 2x2 blocks of same color#####
    #####AND#####
    #####Score for number of finder pattern in code#####

    pattern1 = "10111010000"
    pattern2 = "00001011101"
    #Scan over QR code for 2x2 blocks
    for x in range(0, (maxQRIndex)):
        for y in range(0, (maxQRIndex)):
            if(QRList[y][x] == QRList[y+1][x] == QRList[y][x+1] == QRList[y+1][x+1]):
                score += 3
            if(x < (maxQRIndex - 10)):
                #Check for pattern to right
                checkPatX = ""
                for i in range(0, 11):
                    checkPatX += QRList[y][x + i]
                if((checkPatX == pattern1) or (checkPatX == pattern2)):
                    score += 40
            if(y < (maxQRIndex - 10)):
                #Check for pattern below
                checkPatY = ""
                for i in range(0, 11):
                    checkPatY += QRList[y + i][x]
                if((checkPatY == pattern1) or (checkPatY == pattern2)):
                    score += 40

    #####Calculate ratio of light modules to dark modules and give score#####

    #Percentage calculation
    totalMod = (maxQRIndex + 1) * (maxQRIndex + 1)
    darkMod = 0
    for x in range(0, (maxQRIndex + 1)):
        for y in range(0, (maxQRIndex + 1)):
            darkMod += int(QRList[y][x])
    darkModPerc = int((darkMod / totalMod) * 100)

    #Convert percentage to score
    if(darkModPerc % 5 == 0):
        high = darkModPerc + 5
        low = darkModPerc - 5
    else:
        high = darkModPerc
        low = darkModPerc
        while(((low - 1) % 5) != 0):
            low -= 1
        low -= 1
        while(((high + 1) % 5) != 0):
            high += 1
        high += 1
        low = (abs(low - 50) / 5)
        high = (abs(high - 50) / 5)
        if low > high:
            score += (high * 10)
        else:
            score += (low * 10)

    #Returns total score of the mask
    return score

#Assign copies of qr code to each mask
mask0 = totalQRList.copy()
mask1 = totalQRList.copy()
mask2 = totalQRList.copy()
mask3 = totalQRList.copy()
mask4 = totalQRList.copy()
mask5 = totalQRList.copy()
mask6 = totalQRList.copy()
mask7 = totalQRList.copy()

#Used to insert character into string
def charChange(word, position, replacment):
    return word[:position] + replacment + word[position + 1:]

for x,y in dataCoordinates:
    if((y + x) % 2) == 0:
        if totalQRList[y][x] == '1':
            mask0[y] = charChange(mask0[y], x, '0')
        else:
            mask0[y] = charChange(mask0[y], x, '1')
    if((y % 2) == 0):
        if totalQRList[y][x] == '1':
            mask1[y] = charChange(mask1[y], x, '0')
        else:
            mask1[y] = charChange(mask1[y], x, '1')
    if((x % 3) == 0):
        if totalQRList[y][x] == '1':
            mask2[y] = charChange(mask2[y], x, '0')
        else:
            mask2[y] = charChange(mask2[y], x, '1')
    if((y + x) % 3 == 0):
        if totalQRList[y][x] == '1':
            mask3[y] = charChange(mask3[y], x, '0')
        else:
            mask3[y] = charChange(mask3[y], x, '1')
    if((((y // 2) + (x // 3)) % 2) == 0):
        if totalQRList[y][x] == '1':
            mask4[y] = charChange(mask4[y], x, '0')
        else:
            mask4[y] = charChange(mask4[y], x, '1')
    if(((y * x) % 2) + ((y * x) % 3)) == 0:
        if totalQRList[y][x] == '1':
            mask5[y] = charChange(mask5[y], x, '0')
        else:
            mask5[y] = charChange(mask5[y], x, '1')
    if((((y * x) % 2) + ((y * x) % 3)) % 2) == 0:
        if totalQRList[y][x] == '1':
            mask6[y] = charChange(mask6[y], x, '0')
        else:
            mask6[y] = charChange(mask6[y], x, '1')
    if ((((x + y) % 2) + ((y * x) % 3)) % 2) == 0:
        if totalQRList[y][x] == '1':
            mask7[y] = charChange(mask7[y], x, '0')
        else:
            mask7[y] = charChange(mask7[y], x, '1')

#Get score for each mask
mask0Eval = maskEval(mask0)
mask1Eval = maskEval(mask1)
mask2Eval = maskEval(mask2)
mask3Eval = maskEval(mask3)
mask4Eval = maskEval(mask4)
mask5Eval = maskEval(mask5)
mask6Eval = maskEval(mask6)
mask7Eval = maskEval(mask7)

# Mask evalution scores
maskList = [mask0Eval, mask1Eval, mask2Eval, mask3Eval, mask4Eval, mask5Eval, mask6Eval, mask7Eval]

#List of masks
masks = [mask0, mask1, mask2, mask3, mask4, mask5, mask6, mask7]

#Find mask with smallest penalty
min = mask0Eval
bestMask = 0
for i in range(0, len(maskList)):
    if (maskList[i] < min):
        min = maskList[i]
        bestMask = i

###############Add format and version information###############
#Create string to tell error correction level and the mask type
errorCorrectionLevel = '00'
maskType = bin(bestMask)[2:]
while len(maskType) < 3:
    maskType = '0' + maskType
errAndMask = errorCorrectionLevel + maskType

#Split to coefficients for reed solomon polynomial
errAndMask = [int(errAndMask[i]) for i in range(0, len(errAndMask))]

#Add error correction bits
errAndMask = ReedSolomon().RSEncode(errAndMask, 10)

bestMask = masks[bestMask]

#Placing version info
#Around upper left finder pattern
for i in range(0, 6):
    if errAndMask[i] == 1:
        bestMask[8] = charChange(bestMask[8], i, '1')
    if errAndMask[-i] == 1:
        bestMask[i] = charChange(bestMask[i], 8, '1')
if errAndMask[6] == 1:
    bestMask[8] = charChange(bestMask[8], 7, '1')
if errAndMask[7] == 1:
    bestMask[8] = charChange(bestMask[8], 8, '1')
if errAndMask[8] == 1:
    bestMask[8] = charChange(bestMask[8], 7, '1')
print(errAndMask)
#Below upper right finder pattern and besides lower left finder pattern
for i in range(0, 7):
    if errAndMask[i] == 1:
        bestMask[maxQRIndex - i] = charChange(bestMask[maxQRIndex - i], 8, '1')
    if errAndMask[-i] == 1:
        bestMask[8] = charChange(bestMask[8], maxQRIndex - i, '1')
#Create empty output block
outputQRCode = np.full([33, 33, 3], dtype=np.uint8, fill_value=255)

for y in range(0, (maxQRIndex + 1)):
    for x in range(0, (maxQRIndex + 1)):
        if bestMask[y][x] == '1':
            outputQRCode[y][x] = [0, 0, 0]
        else:
            outputQRCode[y][x] = [255, 255, 255]

###############Generating QR Code###############

#Output array as png
QRCode = Image.fromarray(outputQRCode, "RGB")
QRCode.save("GeneratedQRCode.PNG")
