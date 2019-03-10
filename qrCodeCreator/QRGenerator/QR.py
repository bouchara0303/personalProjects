import numpy as np
from PIL import Image
from reedSolomon import ReedSolomon

class QR:
    requiredBits = 512

    def __init__(self):

        #Initialize alphanumeric dictionary
        self.alphaNumeric = {'0':'0', '1':'1', '2':'2',  '3':'3', '4':'4', '5':'5',
        '6':'6', '7':'7', '8':'8', '9':'9', 'A':'10', 'B':'11', 'C':'12', 'D':'13',
        'E':'14', 'F':'15', 'G':'16', 'H':'17', 'I':'18', 'J':'19', 'K':'20', 'L':'21',
        'M':'22', 'N':'23', 'O':'24', 'P':'25', 'Q':'26', 'R':'27', 'S':'28', 'T':'29',
        'U':'30', 'V':'31', 'W':'32', 'X':'33', 'Y':'34', 'Z':'35', ' ':'36', '$':'37',
        '%':'38', '*':'39', '+':'40', '-':'41', '.':'42', '/':'43', ':':'44'}

        #Initialize hexidecimal dictionary
        self.hex = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15}

        #Initialize QR variables
        self.color = "000000"
        self.encodingMode = "B"
        self.image = ""
        self.imagePrompt = "N"
        self.info = ""

    def alphaEncode(self, info):

        #Capitalize input string and initialize variables
        info = info.upper()
        tempInfo = ""
        infoLen = len(info)
        encodingMode = "0010"

        #Converts pairs of characters to their binary values in lengths of 11 bits
        for i in range(0, len(info) // 2):
            temp = bin((self.alphaNumeric[info[2 * i]] * 45) + (self.alphaNumeric[info[(2 * i) + 1]]))[2:]
            while len(temp) < 11:
                temp = "0" + temp
            tempInfo += temp

        #Encodes last character if string length is odd
        if len(info) % 2 == 1:
            temp = bin(self.alphaNumeric[info[-1]])[2:]
            while len(temp) < 6:
                temp = "0" + temp
            tempInfo += temp

        #Info now converted to binary string
        infoLen = bin(infoLen)[2:]
        while len(infoLen) < 9:
            infoLen = "0" + infoLen

        #Concatenate to form single info string
        info = encodingMode + infoLen + tempInfo

        return info

    def byteEncode(self, info):

        #Initialize variables
        tempInfo = ""
        encodingMode = "0100"
        infoLen = bin(len(info))[2:]
        while len(infoLen) < 8:
            infoLen = "0" + infoLen

        #Convert characters to binary Unicode representation
        for char in info:
            temp = bin(ord(char))[2:]
            while len(temp) < 8:
                temp = "0" + temp
            tempInfo += temp

        #Concatenate to form single info string
        info = encodingMode + infoLen + tempInfo

        return info
    def charChange(word, pos, rep):
        return word[:pos] + rep + word[pos + 1:]

    #Generate QR Code
    def generate(self, encodingMode, info, imagePrompt = "N", image = "", color = "0F0F0F"):

        #Checks to make sure of valid hexidecimal value
        isHex = True
        for i in range(0, len(color)):
            if color[i].upper() not in self.hex:
                isHex = False

        #Error flags
        if (len(color) != 6) or (not isHex):
            raise ValueError("Color must be in hexidecimal format.")
        elif ((len(info) > 90) and encodingMode == 'A') or ((len(info) > 62) and encodingMode == 'B'):
            raise ValueError("The given string is too long for the desired encoding mode.")

        if encodingMode not in ('A', 'a', 'B', 'b'):
            encodingMode = 'B'
        if imagePrompt not in  ('Y', 'y', 'N', 'n'):
            imagePrompt = 'N'

        if imagePrompt in ('Y', 'y'):
            image = Image.open(image).resize((297, 297))
            Image.composite(image, Image.new('RGB', image.size, 'white'), image)

        #Update instance variables
        self.encodingMode = encodingMode
        self.info = info
        self.image = image
        self.color = color.upper()
        self.imagePrompt = imagePrompt

        #Format hex values
        tempColor = self.color
        self.color = []
        for i in range(0, 3):
            self.color.append((self.hex[tempColor[2 * i]] * 16) + self.hex[tempColor[(2 * i) + 1]])

        if self.encodingMode in ('A', 'a'):
            info = alphaEncode(self.info)
        elif self.encodingMode in ('B', 'b'):
            info = self.byteEncode(self.info)

        #Add terminating indicator to string
        i = 0
        while (len(info) < self.requiredBits) and (i < 4):
            info += "0"
            i += 1

        #Format string to be parsed to form 8 bit blocks
        while len(info) % 8 != 0:
            info += "0"

        #Add padding bits to fill remaining space in QR Code
        i = 1
        while len(info) < self.requiredBits:
            if i % 2 == 1:
                info += "11101100"
            elif i % 2 == 0:
                info += "00010001"

        #Split string into 8 bit blocks
        info = [info[i:(i + 8)] for i in range(0, len(info), 8)]

        #List of coefficients for Reed Solomon error correction
        coefficients = []
        for block in info:
            coefficients.append(int(block, 2))

        #Data blocks
        block1 = info[0:32]
        block2 = info[32:64]

        #Error correction blocks
        ecBlock1 = ReedSolomon().RSEncode(coefficients[0:32], 18)[32:50]
        ecBlock2 = ReedSolomon().RSEncode(coefficients[32:64], 18)[32:50]

        #Convert decimal integers to binary
        for i in range(0, 18):

            #First block
            temp = bin(ecBlock1[i])[2:]
            while len(temp) < 8:
                temp = "0" + temp
            ecBlock1[i] = temp

            #Second block
            temp = bin(ecBlock2[i])[2:]
            while len(temp) < 8:
                temp = "0" + temp
            ecBlock2[i] = temp

        #Organize data blocks and error correction blocks together
        info = ""
        for i in range(0,32):
            info += block1[i]
            info += block2[i]
        for i in range(0, 18):
            info += ecBlock1[i]
            info += ecBlock2[i]

        #Add remainder bits to end of string
        info += "0000000"

        #White QR image array
        QRCode = np.full([33,33,3], dtype=np.uint8, fill_value=255)

        #Empty finder pattern array
        orientBlock = np.full([7, 7, 3], dtype=np.uint8, fill_value=255)

        #Empty alignment pattern array
        alignmentBlock = np.full([5, 5, 3], dtype=np.uint8, fill_value=255)

        #Always placed besides lower left orientation block
        darkModule = np.array(self.color)

        #Fill finder pattern arrays
        for i in range(0, 7):
            for j in range(0, 7):
                if (i == 0) or (i == 6) or (j == 0) or (j == 6):
                    orientBlock[j][i] = self.color
                elif (i > 1) and (i < 5) and (j > 1) and (j < 5):
                    orientBlock[j][i] = self.color

        #Fill alignment pattern arrays
        for i in range(0, 5):
            for j in range(0, 5):
                if (i == 0) or (i == 4) or (j == 0) or (j == 4):
                    alignmentBlock[j, i] = self.color
        alignmentBlock[2, 2] = self.color

        #Insert blocks
        QRCode[0:7, 26:33] = orientBlock
        QRCode[0:7, 0:7] = orientBlock
        QRCode[26:33, 0:7] = orientBlock
        QRCode[24:29, 24:29] = alignmentBlock
        QRCode[25, 8] = darkModule

        #Fill timing patterns
        for i in range(7, 26):
            if (i % 2) == 0:
                QRCode[6, i] = self.color
                QRCode[i, 6] = self.color

        #Location of data coordinates
        dataCoordinates = []

        #Placing error correction and data modules
        i = 32
        j = 32
        deltaI = 0
        deltaJ = 0
        column = 1
        subColumn = 1
        direction = 1
        maxQRIndex = 32
        for x in range(0, len(info)):

            #Convert data to colored blocks
            if info[x] == '1':
                colorFill = self.color
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
            if QR.isBetween(i, maxQRIndex-7, maxQRIndex) and (j == 9) and leftSubColumn and up:
                column += 1
                deltaJ = 0
                deltaI = -1

            #Reverse once reaching bottom of QRCode
            elif(QR.isBetween(i, 9, maxQRIndex) and (j == maxQRIndex) and leftSubColumn and down):
                column += 1
                deltaJ = 0
                deltaI = -1

            #Jump over alignment pattern moving up
            elif(QR.isBetween(i, 25, 28) and (j == 29) and leftSubColumn and up):
                deltaJ = -6
                deltaI = 1

            #Jump over alignment pattern moving down
            elif(QR.isBetween(i, 25, 28) and (j == 23) and leftSubColumn and down):
                deltaJ = 6
                deltaI = 1

            # Shift left once reaching alignment pattern
            elif (QR.isBetween(j, 25, 29) and leftSubColumn and (i == maxQRIndex - 9)):
                deltaJ = -1
                deltaI = 0
                subColumn -= 1

            #Skip over timing pattern moving up
            elif(QR.isBetween(i, 9, 24) and (j == 7) and leftSubColumn and up):
                deltaJ = -2
                deltaI = 1

            #Reverse once reaching the top
            elif(QR.isBetween(i, 9, 24) and (j == 0) and leftSubColumn and up):
                column += 1
                deltaJ = 0
                deltaI = -1

            #Skip over timing pattern moving down
            elif(QR.isBetween(i, 9, 24) and (j == 5) and leftSubColumn and down):
                deltaJ = 2
                deltaI = 1

            #Shift over vertical timing pattern
            elif((i == 7) and (j == 9)):
                column += 1
                deltaJ = 0
                deltaI = -2

            #Change directions between high and low finder patterns while moving up
            elif(QR.isBetween(i, 0, 5) and (j == 9) and up and leftSubColumn):
                column += 1
                deltaJ = 0
                deltaI = -1

            #Change directions between high and low finder patterns while moving down
            elif(QR.isBetween(i, 0, 5) and (j == maxQRIndex - 8) and down and leftSubColumn):
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

        #Create list describing full QR code rows and columns
        totalQRString = ""
        for y in range(0, maxQRIndex + 1):
            for x in range(0, maxQRIndex + 1):
                if (self.color in QRCode[y, x]):
                    totalQRString += "1"
                else:
                    totalQRString += "0"

        #Rows of all modules in QR Code
        totalQRList = [totalQRString[x: x + maxQRIndex + 1] for x in range(0, len(totalQRString), (maxQRIndex + 1))]

        #List of all 8 masks and their evaluation scores
        masks = [[]] * 8
        for i in range(0, 8):
            masks[i] = totalQRList.copy()
        maskScores = [0] * 8

        #Create all 8 masks
        for x,y in dataCoordinates:
            if((y + x) % 2) == 0:
                if totalQRList[y][x] == '1':
                    masks[0][y] = QR.charChange(masks[0][y], x, '0')
                else:
                    masks[0][y] = QR.charChange(masks[0][y], x, '1')
            if((y % 2) == 0):
                if totalQRList[y][x] == '1':
                    masks[1][y] = QR.charChange(masks[1][y], x, '0')
                else:
                    masks[1][y] = QR.charChange(masks[1][y], x, '1')
            if((x % 3) == 0):
                if totalQRList[y][x] == '1':
                    masks[2][y] = QR.charChange(masks[2][y], x, '0')
                else:
                    masks[2][y] = QR.charChange(masks[2][y], x, '1')
            if((y + x) % 3 == 0):
                if totalQRList[y][x] == '1':
                    masks[3][y] = QR.charChange(masks[3][y], x, '0')
                else:
                    masks[3][y] = QR.charChange(masks[3][y], x, '1')
            if((((y // 2) + (x // 3)) % 2) == 0):
                if totalQRList[y][x] == '1':
                    masks[4][y] = QR.charChange(masks[4][y], x, '0')
                else:
                    masks[4][y] = QR.charChange(masks[4][y], x, '1')
            if(((y * x) % 2) + ((y * x) % 3)) == 0:
                if totalQRList[y][x] == '1':
                    masks[5][y] = QR.charChange(masks[5][y], x, '0')
                else:
                    masks[5][y] = QR.charChange(masks[5][y], x, '1')
            if((((y * x) % 2) + ((y * x) % 3)) % 2) == 0:
                if totalQRList[y][x] == '1':
                    masks[6][y] = QR.charChange(masks[6][y], x, '0')
                else:
                    masks[6][y] = QR.charChange(masks[6][y], x, '1')
            if ((((x + y) % 2) + ((y * x) % 3)) % 2) == 0:
                if totalQRList[y][x] == '1':
                    masks[7][y] = QR.charChange(masks[7][y], x, '0')
                else:
                    masks[7][y] = QR.charChange(masks[7][y], x, '1')

        #Evaluate scores for each mask
        for i in range(0, 8):
            maskScores[i] = QR.maskEval(masks[i])

        #Find mask with smallest penalty
        min = maskScores[0]
        bestMask = i
        for i in range(0, 8):
            if maskScores[i] < min:
                min = maskScores[i]
                bestMask = i

        #Info about error correction level and the mask type
        ecLevel = "00"
        maskType = bin(bestMask)[2:]
        while len(maskType) < 3:
            maskType = "0" + maskType
        formatVersionInfo = ecLevel + maskType
        formatVersionInfo = [int(x) for x in formatVersionInfo]
        tempVersionInfo = formatVersionInfo.copy()

        #Pad format and version info for Reed Solomon error correction
        for i in range(0, 10):
            formatVersionInfo.append(0)

        #Getting error correction bits for format and version info
        while(len(formatVersionInfo) > 10):

            #If mask type 0
            if(([0] * 15) == formatVersionInfo):
                formatVersionInfo = formatVersionInfo[5:]
                break

            #Generator polynomial for error correction
            genPoly = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]

            #Match length of Generator polynomial with length of data polynomial
            while len(genPoly) < len(formatVersionInfo):
                genPoly.append(0)

            #Bitwise XOR result with Generator polynomial
            for i in range(0, len(formatVersionInfo)):
                formatVersionInfo[i] ^= genPoly[i]

            #Remove leading zeros
            while (formatVersionInfo[0] == 0):
                formatVersionInfo = formatVersionInfo[1:]

        #Pad final result
        while(len(formatVersionInfo) < 10):
            formatVersionInfo = [0] + formatVersionInfo

        #Result after error correction
        formatVersionInfo = tempVersionInfo + formatVersionInfo

        #XOR result with mask string to get final result
        maskString = [int(x) for x in "101010000010010"]
        for i in range(0, len(formatVersionInfo)):
            formatVersionInfo[i] ^= maskString[i]

        #Select best mask
        bestMask = masks[bestMask]

        #Placing version info around upper left finder pattern
        for i in range(0, 6):
            if formatVersionInfo[i] == 1:
                bestMask[8] = QR.charChange(bestMask[8], i, '1')
            else:
                bestMask[8] = QR.charChange(bestMask[8], i, '0')
            if formatVersionInfo[-(i + 1)] == 1:
                bestMask[i] = QR.charChange(bestMask[i], 8, '1')
            else:
                bestMask[i] = QR.charChange(bestMask[i], 8, '0')

        #Placing version info around corner of upper left qr code
        if formatVersionInfo[6] == 1:
            bestMask[8] = QR.charChange(bestMask[8], 7, '1')
        else:
            bestMask[8] = QR.charChange(bestMask[8], 7, '0')
        if formatVersionInfo[7] == 1:
            bestMask[8] = QR.charChange(bestMask[8], 8, '1')
        else:
            bestMask[8] = QR.charChange(bestMask[8], 8, '0')
        if formatVersionInfo[8] == 1:
            bestMask[7] = QR.charChange(bestMask[7], 8, '1')
        else:
            bestMask[7] = QR.charChange(bestMask[7], 8, '0')

        #Place version info besides lower left finder pattern
        for i in range(0, 7):
            if formatVersionInfo[i] == 1:
                bestMask[maxQRIndex - i] = QR.charChange(bestMask[maxQRIndex - i], 8, '1')
            else:
                bestMask[maxQRIndex - i] = QR.charChange(bestMask[maxQRIndex - i], 8, '0')

        #Place version info below upper right finder pattern
        count = 7
        for i in range(7, 15):
            if formatVersionInfo[i] == 1:
                bestMask[8] = QR.charChange(bestMask[8], maxQRIndex - count, '1')
            else:
                bestMask[8] = QR.charChange(bestMask[8], maxQRIndex - count, '0')
            count -= 1

        #Add padding to QR code
        outputQRCode = np.full([37, 37, 3], dtype=np.uint8, fill_value=255)

        #Create QR Code
        for y in range(0, (maxQRIndex + 1)):
            for x in range(0, (maxQRIndex + 1)):
                if bestMask[y][x] == '1':
                    QRCode[y][x] = self.color
                else:
                    QRCode[y][x] = [255, 255, 255]

        #Place QR code in padded block
        for x in range(2, 35):
            for y in range(2, 35):
                outputQRCode[y, x] = QRCode[y - 2][x - 2]
                
        #Cut out middle of QR Code to insert image
        if self.imagePrompt in ('Y', 'y'):
            for x in range(0, 11):
                for y in range(0, 11):
                    if (x != 0) and (x != 10) and (y != 0) and (y != 10):
                        outputQRCode[y + 13, x + 13] = [255, 255, 255]

        #Output array as png
        QRCode = Image.fromarray(outputQRCode, "RGB")
        QRCode = QRCode.resize((1221, 1221))
        if self.imagePrompt in ('Y', 'y'):
            QRCode.paste(image, (462, 462, 759, 759), image)
        QRCode.save("generatedQRCode.png")

    def isBetween(num, x1, x2):
        return ((num >= x1) and (num <= x2))

    def maskEval(QRList):
        score = 0
        i = 0
        maxQRIndex = 32

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
