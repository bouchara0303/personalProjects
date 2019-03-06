import numpy as np
from PIL import Image
from reedSolomon import ReedSolomon

"""
Program for creating Version 4 QR Codes with error correction level M
"""
mode = ""
#Ask for encoding mode
while (mode != 'A') and (mode != 'B'):
    mode = input("Would you like to encode in Alphanumeric mode or Byte mode? A:(0-9 + A-Z) or B:(all ASCII characters) ")
    mode = mode.upper()

if mode == 'A':
    alphaNumericEncoding = {'0':'0', '1':'1', '2':'2',  '3':'3', '4':'4', '5':'5',
    '6':'6', '7':'7', '8':'8', '9':'9', 'A':'10', 'B':'11', 'C':'12', 'D':'13',
    'E':'14', 'F':'15', 'G':'16', 'H':'17', 'I':'18', 'J':'19', 'K':'20', 'L':'21',
    'M':'22', 'N':'23', 'O':'24', 'P':'25', 'Q':'26', 'R':'27', 'S':'28', 'T':'29',
    'U':'30', 'V':'31', 'W':'32', 'X':'33', 'Y':'34', 'Z':'35', ' ':'36', '$':'37',
    '%':'38', '*':'39', '+':'40', '-':'41', '.':'42', '/':'43', ':':'44'}

#Returns hexidecimal values
hexChart = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15}

#Create list of modules for encoded data
modules = []
data = ""

###############Encoding data###############

#User input
URL = input("Please enter the string you would like for encoding: ")
URLLength = len(URL)

#Ask to place image in center
image = input("Would you like to add an image to the center of your QR Code? (y/n): ")

#Image should be in same directory as this file
if((image == 'y') or (image == 'Y')):
    image = input("Please enter the image file name: ")
    try:
        image = Image.open(image).resize((297, 297))
        Image.composite(image, Image.new('RGB', image.size, 'white'), image)

    except IOError:
        print("Sorry but the file couldn't be found...")

#Ask for color of QR code
QRColor = "n/a"

while len(QRColor) != 6:
    QRColor = input("Please enter the hexidecimal color for the QR code: ")
    QRColor = QRColor.upper()
    isHex = True
    for i in range(0, len(QRColor)):
        if QRColor[i] not in hexChart:
            isHex = False
    if not isHex:
        QRColor = "n/a"

tempColor = []
for i in range(0, 6):
    if i % 2 == 0:
        temp = hexChart[QRColor[i]] * 16
        tempColor.append(temp)
    else:
        tempColor.append(hexChart[QRColor[i]])
QRColor = []
for i in range(0, 3):
    QRColor.append(tempColor[2 * i] + tempColor[(2 * i) + 1])

#Alphanumeric encoding mode
if mode == 'A':

    URL = URL.upper()

    #Encoding input string
    i = 1
    valueBuffer = []

    #Add alphanumeric values to list
    for char in URL:
        modules.append(int(alphaNumericEncoding[char]))

    #Pair alphanumeric values
    for i in range(0, len(modules) // 2):
        valueBuffer.append(modules[(2 * i): (2 * (i + 1))])

    #Check if number of pairs is even or odd
    if len(modules) % 2 == 1:

        #Append final value for odd length
        valueBuffer.append(modules[-1])
        modules.clear()

        #Convert base 45 number to binary and add to modules list
        for i in range(0, len(valueBuffer) - 1):
            temp = bin((valueBuffer[i][0] * 45) + valueBuffer[i][1])[2:]

            #Pad value pairs
            while len(temp) < 11:
                temp = '0' + temp
            modules.append(temp)

        #Pad lone value
        temp = bin(valueBuffer[-1])[2:]
        while len(temp) < 6:
            temp = '0' + temp
        modules.append(temp)

    #If even number of values
    else:
        modules.clear()

        #Convert base 45 number to binary and add to modules list
        for pair in valueBuffer:
            temp = bin((pair[0] * 45) + pair[1])[2:]
            while len(temp) < 11:
                temp = '0' + temp
            modules.append(temp)

    #Identify string length and format it to fit 9 bit block
    if URLLength > 90:
        print("""The desired link is too long for QR Code version 4.
         Please consider using a link shortener...""")
        quit()
    else:
        URLLength = bin(URLLength)[2:]
        while len(URLLength) < 9:
            URLLength = '0' + URLLength

    #Identify encoding mode for QR Code
    encodingMode = "0010"

#Byte encoding mode
elif mode == 'B':
    for char in URL:
        temp = bin(ord(char))[2:]
        while len(temp) < 8:
            temp = '0' + temp
        modules.append(temp)

    #Identify encoding mode for QR Code
    encodingMode = "0100"

    #Identify string length and format it to fit 9 bit block
    if URLLength > 62:
        print("""The desired link is too long for QR Code version 4.
         Please consider using a link shortener...""")
        quit()
    else:
        URLLength = bin(URLLength)[2:]
        while len(URLLength) < 8:
            URLLength = '0' + URLLength


#Required number of bits for Version 4-M QR Code
requiredBits = 512

#Add encoded data from array to form single string
data = encodingMode + URLLength
for block in modules:
    data += block

#Add terminating indicator if encoded string is less than maximum capacity
i = 1
while (len(data) < requiredBits) and (i < 5):
    data += "0"
    i += 1

#Add zeros to encoded string until it can be split into bytes
while (len(data) % 8) != 0:
    data += "0"

#Add padding bits if encoded string is too short
i = 1
while len(data) < requiredBits:
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

    #Add bytes to coefficients and convert from binary to decimal equivalent
    coefficients.append(int(codeword, 2))

#Reed solomon error correction codewords
ecBlock1 = ReedSolomon().RSEncode(coefficients[0:32], 18)[32:50]
ecBlock2 = ReedSolomon().RSEncode(coefficients[32:64], 18)[32:50]

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
darkModule = np.array(QRColor)

#Fill finder pattern arrays
for i in range(0, 7):
    for j in range(0, 7):
        if (i == 0) or (i == 6) or (j == 0) or (j == 6):
            orientBlock[j][i] = QRColor
        elif (i > 1) and (i < 5) and (j > 1) and (j < 5):
            orientBlock[j][i] = QRColor

#Fill alignment pattern arrays
for i in range(0, 5):
    for j in range(0, 5):
        if (i == 0) or (i == 4) or (j == 0) or (j == 4):
            alignmentBlock[j, i] = QRColor
alignmentBlock[2, 2] = QRColor

#Insert blocks
QRCode[0:7, 26:33] = orientBlock
QRCode[0:7, 0:7] = orientBlock
QRCode[26:33, 0:7] = orientBlock
QRCode[24:29, 24:29] = alignmentBlock
QRCode[25, 8] = darkModule

#Fill timing patterns
for i in range(7, 26):
    if (i % 2) == 0:
        QRCode[6, i] = QRColor
        QRCode[i, 6] = QRColor

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

    #Convert data to colored blocks
    if finalDataString[x] == '1':
        colorFill = QRColor
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
    subColumn += 1 #Should be working

###############Masking data pattern###############

#Create list describing full QR code rows and columns
totalQRString = ""
for y in range(0, maxQRIndex + 1):
    for x in range(0, maxQRIndex + 1):
        if (QRColor in QRCode[y, x]):
            totalQRString += "1"
        else:
            totalQRString += "0"

#Rows of all modules in QR Code
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

    #Patterns very similar to finder pattern in qr code
    pattern1 = "10111010000"
    pattern2 = "00001011101"

    #Scan over QR code for 2x2 blocks
    for x in range(0, (maxQRIndex)):
        for y in range(0, (maxQRIndex)):
            if(QRList[y][x] == QRList[y+1][x] == QRList[y][x+1] == QRList[y+1][x+1]):
                score += 3

            #Check for pattern to right
            if(x < (maxQRIndex - 10)):
                checkPatX = ""
                for i in range(0, 11):
                    checkPatX += QRList[y][x + i]
                if((checkPatX == pattern1) or (checkPatX == pattern2)):
                    score += 40

            #Check for pattern below
            if(y < (maxQRIndex - 10)):
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

#Create all 8 masks
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

#Split into coefficients for reed solomon polynomial
errAndMask = [int(x) for x in errAndMask]
formatList = errAndMask.copy()

#Pad Version info with 10 zeros for error correction calculation
for i in range(0, 10):
    errAndMask.append(0)

#Get error correction bits for format info using reed solomon error correction
while(len(errAndMask) > 10):

    #If mask type 0
    if(([0] * 15) == errAndMask):
        errAndMask = errAndMask[5:]
        break

    #Generator polynomial for error correction
    genPoly = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]

    #Match length of Generator polynomial with length of data polynomial
    while len(genPoly) < len(errAndMask):
        genPoly.append(0)

    #Bitwise XOR result with Generator polynomial
    for i in range(0, len(errAndMask)):
        errAndMask[i] ^= genPoly[i]

    #Remove leading zeros
    while (errAndMask[0] == 0):
        errAndMask = errAndMask[1:]

#Pad final result
while(len(errAndMask) < 10):
    errAndMask = [0] + errAndMask

#Result after error correction
result = formatList + errAndMask

#XOR result with mask string to get final result
maskString = [int(x) for x in "101010000010010"]
for i in range(0, len(result)):
    result[i] ^= maskString[i]

#Final result
errAndMask = result

#Select best mask
bestMask = masks[bestMask]

#Placing version info around upper left finder pattern
for i in range(0, 6):
    if errAndMask[i] == 1:
        bestMask[8] = charChange(bestMask[8], i, '1')
    else:
        bestMask[8] = charChange(bestMask[8], i, '0')
    if errAndMask[-(i + 1)] == 1:
        bestMask[i] = charChange(bestMask[i], 8, '1')
    else:
        bestMask[i] = charChange(bestMask[i], 8, '0')

#Placing version info around corner of upper left qr code
if errAndMask[6] == 1:
    bestMask[8] = charChange(bestMask[8], 7, '1')
else:
    bestMask[8] = charChange(bestMask[8], 7, '0')
if errAndMask[7] == 1:
    bestMask[8] = charChange(bestMask[8], 8, '1')
else:
    bestMask[8] = charChange(bestMask[8], 8, '0')
if errAndMask[8] == 1:
    bestMask[7] = charChange(bestMask[7], 8, '1')
else:
    bestMask[7] = charChange(bestMask[7], 8, '0')

#Place version info besides lower left finder pattern
for i in range(0, 7):
    if errAndMask[i] == 1:
        bestMask[maxQRIndex - i] = charChange(bestMask[maxQRIndex - i], 8, '1')
    else:
        bestMask[maxQRIndex - i] = charChange(bestMask[maxQRIndex - i], 8, '0')

#Place version info below upper right finder pattern
count = 7
for i in range(7, 15):
    if errAndMask[i] == 1:
        bestMask[8] = charChange(bestMask[8], maxQRIndex - count, '1')
    else:
        bestMask[8] = charChange(bestMask[8], maxQRIndex - count, '0')
    count -= 1

#Create empty output block
QRCode = np.full([33, 33, 3], dtype=np.uint8, fill_value=255)

#Add padding to QR Code
outputQRCode = np.full([37, 37, 3], dtype=np.uint8, fill_value=255)

#Create QR Code
for y in range(0, (maxQRIndex + 1)):
    for x in range(0, (maxQRIndex + 1)):
        if bestMask[y][x] == '1':
            QRCode[y][x] = QRColor
        else:
            QRCode[y][x] = [255, 255, 255]

#Place QR code in padded block
for x in range(2, 35):
    for y in range(2, 35):
        outputQRCode[y, x] = QRCode[y - 2][x - 2]

###############Generating QR Code###############

#Cut out middle of QR Code to insert image
if type(image) != type('n'):
    for x in range(0, 11):
        for y in range(0, 11):
            if (x != 0) and (x != 10) and (y != 0) and (y != 10):
                outputQRCode[y + 13, x + 13] = [255, 255, 255]

#Output array as png
QRCode = Image.fromarray(outputQRCode, "RGB")
QRCode = QRCode.resize((1221, 1221))
if type(image) != type('n'):
    QRCode.paste(image, (462, 462, 759, 759), image)
QRCode.save("generatedQRCode.png")
