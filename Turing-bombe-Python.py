"""
Simulation of three wheel Turing Bombe - a Python port of 
Simon Jansen's "turing-welchman-bombe-c-code" which he kindly 
shared with me.
See http://www.asciimation.co.nz/bb/2015/06/14/a-turingwelchman-bombe

31/12/2017 First complete Python version
"""
# 
# ENIGMA rotors.
#         ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ
rotor1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ UWYGADFPVZBECKMTHXSLRINQOJ"
rotor2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE AJPCZWRLFBDKOTYUQGENHXMIVS"
rotor3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO TAGBPCSDQEUFVNZHYIXJWLRKOM"
rotor4 = "ESOVPZJAYQUIRHXLNFTGKDCMWB HZWVARTNLGUPXQCEJMBSKDYOIF"
rotor5 = "VZBRGITYUPSDNHLXAWMJQOFECK QCYLXWENFTZOSMVJUDKGIARPHB"

# Enigma reflectors.
reflectorB = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
reflectorC = "FVPJIAOYEDRZXWGCTKUQSBNMHL"

# Set up Bombe drums.
drum1 = ' '
drum2 = ' '
drum3 = ' '
# Bombe drum offsets fomr Enigma rotors.
drum1CoreOffset = 0
drum2CoreOffset = 0
drum3CoreOffset = 0
ROTOR1COREOFFSET = 1
ROTOR2COREOFFSET = 1
ROTOR3COREOFFSET = 1
ROTOR4COREOFFSET = 2
ROTOR5COREOFFSET = 3

# Drums.
drums = [0 for i in range(3)]
# Menu connections.
MAXNUMBERCONNECTIONS = 6
menuConnections = [[0 for j in range(MAXNUMBERCONNECTIONS)] for i in range(36)]
# Scramblers.
numberOfScramblers = 0
#scramblerOffsets = ["" for i in range(36)]
scramblerOffsets = []
scramblerConnections = ["" for i in range(36)]
# Menu letters.
numberMenuLetters = 0
menuLetters = ""
# Test input voltage.
inputLetter = ' '
# Test register.
testMenuLetter = ' '

# Ring setting for all drums.
# 25 = Z.
RINGSETTING = 25

# Set up Bombe reflector.
reflector = ""

diagonalBoard = [[' ' for j in range(26)] for i in range(26)]
diagonalBoardLetter = ' '

# Initial indicator drum positions.
indicatorDrums = "ZZZ"

# Number of untraced voltages.
untraced = 0

# Number of stops.
numStops = 0

# Number of iterations.
numIterations = 0

# States.
allIterationsDone = False
stopFound = False
runComplete = False

# Debugging.
debugDiagonal = False
debugOther    = False
debugEnigma   = False

# ----------------------------------------------------------------------------
# Read rotors.
# ----------------------------------------------------------------------------
def ReadRotors(buffer):
    drums[0] = int(buffer[8])
    drums[1] = int(buffer[11])
    drums[2] = int(buffer[14])

# ----------------------------------------------------------------------------
# Read reflector.
# ----------------------------------------------------------------------------
def ReadReflector(buffer):
    global reflector
    if buffer[11] == 'B':
        reflector = reflectorB
    elif buffer[11] == 'C':
        reflector = reflectorC

# ----------------------------------------------------------------------------
# Read test register.
# ----------------------------------------------------------------------------
def ReadTestRegister(buffer):
    global testMenuLetter
    testMenuLetter = buffer[15]

# ----------------------------------------------------------------------------
# Read input voltage.
# ----------------------------------------------------------------------------
def ReadInputVoltage(buffer):
    global inputLetter
    inputLetter = buffer[15]

# ----------------------------------------------------------------------------
# Read scramblers.
# ----------------------------------------------------------------------------
def ReadScramblers(buffer):
    global numberOfScramblers
    # Work out how many scramblers are being used.
    breakout = buffer[7:].split(',')
    numberOfScramblers = len(breakout)

#    # Copy the scramblers.
#    for i in range(numberOfScramblers):
#        scramblerOffsets[i] = breakout[i].strip()
    # Copy the scramblers.
    for token in breakout:
        scramblerOffsets.append(token.strip())

# ----------------------------------------------------------------------------
# Read connections.
# ----------------------------------------------------------------------------
def ReadConnections(buffer, connectionCount):
    global numberMenuLetters, menuLetters
    tokenCount = 0

    # Set the menu letter.
    menuLetter = buffer[0]
    menuLetters += menuLetter
    numberMenuLetters += 1
    tokenInt = -1

    # Extract the tokens
    breakout = buffer[3:].split(',')
#    for i in range(len(breakout)):
#        breakout[i] = breakout[i].strip()

    # Loop through the tokens
    for token in breakout:
        token = token.strip()
        tokenCount += 1
        # Remove the 'i' or 'o'.
        token = token[:-1]
        tokenInt = int(token)
    		# Store the connection.
        menuConnections[connectionCount][tokenCount - 1] = tokenInt
    		# Store the menu letter against the correct scrambler.
        scramblerConnections[tokenInt - 1] += menuLetter
#
# ----------------------------------------------------------------------------
# Read the set up information from a file.
# ----------------------------------------------------------------------------
def ReadSetupFile(filename):
    buffer = ""
    lineCount = 0
    # Open the file for reading.
    menuFile = open(filename, 'r')
    print("Menu file opened.")
    # Read each line.
    for buffer in menuFile:
        buffer = buffer[:len(buffer)-1]
        lineCount += 1
        if lineCount == 1:
            ReadRotors(buffer)
        elif lineCount == 2:
            ReadReflector(buffer)
        elif lineCount == 3:
            ReadTestRegister(buffer)
        elif lineCount == 4:
            ReadInputVoltage(buffer)
        elif lineCount == 5:
            ReadScramblers(buffer)
        elif lineCount > 6:
            ReadConnections(buffer, lineCount - 7)

    # Close the file.
    menuFile.close()
    return True

# ----------------------------------------------------------------------------
# Setup the drums.
# ----------------------------------------------------------------------------
def SetupDrums():
    global drum1, drum2, drum3, drum1CoreOffset, drum2CoreOffset, drum3CoreOffset

    drum1, drum1CoreOffset = SetDrumAndOffset(drums[0])
    drum2, drum2CoreOffset = SetDrumAndOffset(drums[1])
    drum3, drum3CoreOffset = SetDrumAndOffset(drums[2])

# ----------------------------------------------------------------------------
# Set the correct drum and core wiring offset.
# ----------------------------------------------------------------------------
def SetDrumAndOffset(rotor):
    drum = ""
    offset = ""
    if rotor == 1:
        drum = rotor1
        offset = ROTOR1COREOFFSET
    elif rotor == 2:
        drum = rotor2
        offset = ROTOR2COREOFFSET
    elif rotor == 3:
        drum = rotor3;
        offset = ROTOR3COREOFFSET
    elif rotor == 4:
        drum = rotor4;
        offset = ROTOR4COREOFFSET
    elif rotor == 5:
        drum = rotor5;
        offset = ROTOR5COREOFFSET
    else:
    		print("Unknown rotor specified.")
    return drum, offset

# ----------------------------------------------------------------------------
# Print the setup data to the screen.
# ----------------------------------------------------------------------------
def PrintSetupData():
    print("Top drum: %i" % (drums[0]))
    print("Middle drum: %i" % (drums[1]))
    print("Bottom drum: %i" % (drums[2]))
    if reflector[0] == 'Y':
        print("Reflector: B")
    elif reflector[0] == 'F':
        print("Reflector: C")
    print("Test register: %c" % (testMenuLetter))
    print("Test voltage: %c" % (inputLetter))
    print("Number of scramblers: %i" % (numberOfScramblers))
    PrintScramblers()
    print("Number of menu letters: %i" % (numberMenuLetters))
    print("Menu connections:")
    for i in range(numberMenuLetters):
        print("%c:" % menuLetters[i], end = '')
        for j in range(MAXNUMBERCONNECTIONS):
            if menuConnections[i][j] != 0:
                print("%3i " % menuConnections[i][j], end = '')
        print()

# ----------------------------------------------------------------------------
# Pass a value through the given scrambler.
# ----------------------------------------------------------------------------
def Scrambler(value, currentScrambler):
    currentDrum = ""
    currentDrumOffset = 0
    drumCoreOffset = 0

    # Through drum 3.
    currentDrum = drum3
    currentDrumOffset = ord(currentScrambler[2]) - ord('A')
    drumCoreOffset = drum3CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, 
                                    drumCoreOffset)

    # Through drum 2.
    currentDrum = drum2
    currentDrumOffset = ord(currentScrambler[1]) - ord('A')
    drumCoreOffset = drum2CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

    # Through drum 1.
    currentDrum = drum1
    currentDrumOffset = ord(currentScrambler[0]) - ord('A')
    drumCoreOffset = drum1CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

    # Through reflector.
    value = ord(reflector[value - 1]) - 64
    value = WrapScramblerOffset(value)
    if (debugEnigma == True):
        print("%c" % (value + 64), end = '')
    # Back through drum 1.
    currentDrum = drum1
    currentDrumOffset = ord(currentScrambler[0]) - ord('A')
    drumCoreOffset = drum1CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

    # Back through drum 2.
    currentDrum = drum2
    currentDrumOffset = ord(currentScrambler[1]) - ord('A')
    drumCoreOffset = drum2CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

    # Back through drum 3.
    currentDrum = drum3
    currentDrumOffset = ord(currentScrambler[2]) - ord('A')
    drumCoreOffset = drum3CoreOffset
    value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
    value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)
    
    return value

# ----------------------------------------------------------------------------
# Wrap the scrambler value so it is in the range 1-26.
# ----------------------------------------------------------------------------
def WrapScramblerOffset(value):
    while (value < 1):
        value = value + 26
    while (value > 26):
        value = value - 26
    return value

# ----------------------------------------------------------------------------
# Calculate the current scrambler offset.
# We take the current drum offset, the ring value (Z) and the Bombe core
# wiring offset into account.
# ----------------------------------------------------------------------------
def CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset):
    returnValue = -1
    
    returnValue = value + currentDrumOffset - RINGSETTING - drumCoreOffset
    returnValue = WrapScramblerOffset(returnValue)
    return returnValue

# ----------------------------------------------------------------------------
# Pass the value forwards through the given scrambler.
# ----------------------------------------------------------------------------
def ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset):
    currentValue = -1
    
    currentValue = ord(currentDrum[(value - 1)]) - 64
    currentValue = currentValue - currentDrumOffset + RINGSETTING + drumCoreOffset
    currentValue = WrapScramblerOffset(currentValue)
    if (debugEnigma == True):
        print("%c" % (currentValue + 64), end = '')
    return currentValue

# ----------------------------------------------------------------------------
# Pass the value backwards through the given scrambler.
# ----------------------------------------------------------------------------
def BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset):
    currentValue = -1
    
    currentValue = ord(currentDrum[(value - 1) + 27]) - 64
    currentValue = currentValue - currentDrumOffset + RINGSETTING + drumCoreOffset
    currentValue = WrapScramblerOffset(currentValue)
    if (debugEnigma == True):
        print("%c" % (currentValue + 64), end = '')
    return currentValue

# ----------------------------------------------------------------------------
# Increment all the scramblers.
# ----------------------------------------------------------------------------
def IncrementScramblers():
    for i in range(numberOfScramblers):
        IncrementScrambler(i)

# ----------------------------------------------------------------------------
# Increment the scrambler.
# ----------------------------------------------------------------------------
def IncrementScrambler(i):

    # Always increment the top drum.
    # Top drum.
    letter1 = chr(ord(scramblerOffsets[i][0])+1)
    if letter1 > 'Z':
        letter1 = 'A'
    
    # The middle one increments after the top one has done 1 and a half turns
    # or 39 steps (26 + 13).
    if (numIterations % 39) == 0:
        # Middle drum.
        letter2 = chr(ord(scramblerOffsets[i][1])+1)
        if letter2 > 'Z':
            letter2 = 'A'
    else:
        letter2 = scramblerOffsets[i][1]

    # Bottom drum increments when the second drum has done one whole turn.
    if (numIterations % (39 * 26)) == 0:
        letter3 = chr(ord(scramblerOffsets[i][2])+1)
        if letter3 > 'Z':
            letter3 = 'A'
    else:
        letter3 = scramblerOffsets[i][2]
    scramblerOffsets[i] = letter1 + letter2 + letter3

# ----------------------------------------------------------------------------
# Decrement the indicator.
# ----------------------------------------------------------------------------
def DecrementIndicator():
    global allIterationsDone, indicatorDrums

    letter2 = indicatorDrums[1]
    letter3 = indicatorDrums[2]
    
    # Top indicator drum always decrements.
    letter1 = chr(ord(indicatorDrums[0]) - 1)
    if letter1 < 'A':
        letter1 = 'Z'

    # The middle one decrements after the top one has done 1 and a half turns
    # or 39 steps (26 + 13).
    if (numIterations % 39) == 0:
        letter2 = chr(ord(indicatorDrums[1]) - 1)
        if letter2 < 'A':
            letter2 = 'Z'

            # The bottom one decrements if the middle one has just finished one turn.
            letter3 = chr(ord(indicatorDrums[2]) - 1)
            if letter3 < 'A':
                letter3 = 'Z'
        				# When this happens we are done.
                allIterationsDone = True
                print
                print("All stops found.")

    indicatorDrums = letter1 + letter2 + letter3

# ----------------------------------------------------------------------------
# Reset the diagonal board to all zero.
# ----------------------------------------------------------------------------
def ResetDiagonalBoard():
    global untraced
    
    if debugDiagonal == True:
        print("Resetting diagonal board.")
    
    # Set all voltages to 0.
    for i in range(26):
        for j in range(26):
            diagonalBoard[i][j] = 0
    # Set the untraced count to 0.
    untraced = 0

# ----------------------------------------------------------------------------
# Set voltages on the diagonal board.
# ----------------------------------------------------------------------------
def SetDiagonalBoard(menuLetter, letter):
    global untraced
    if (debugOther == True):
        print("Setting diagonal: %c:%c" % (menuLetter, letter))
    if (diagonalBoard[ord(menuLetter) - ord('A')][ord(letter) - ord('A')] == 0):
        # Always update the menu letter.
        diagonalBoard[ord(menuLetter) - ord('A')][ord(letter) - ord('A')] = -1
        # Update the count of untraced voltages.
        untraced += 1

    # If it's not the same letter in the pair set the diagonal.
    if (menuLetter != letter):
        if (diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] == 0):
            # Update the untraced count if this is a menu letter.
            if menuLetters.find(letter) != -1:
                diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] = -1
                untraced += 1
            else:
                diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] = 2

# ----------------------------------------------------------------------------
# Print out the scramblers.
# ----------------------------------------------------------------------------
def PrintScramblers():
    scramblerNumber = 0

    print("Scramblers:")
    for i in range(numberOfScramblers):
        print("%2i:%s-%s " % (i + 1, scramblerOffsets[i], 
                              scramblerConnections[i]), end = '')
        scramblerNumber += 1
        if scramblerNumber % 6 == 0:
                print()
    print()

# ----------------------------------------------------------------------------
# Print out a scrambler corrected to match Enigma.
# ----------------------------------------------------------------------------
def PrintCorrectedScrambler(scrambler):
    drum = ''
    drumValue = -1
    
    drum = scrambler[0];
#    drumValue = (int)drum - 64 - drum1CoreOffset;
    drumValue = ord(drum) - 64 - drum1CoreOffset
    drumValue = WrapScramblerOffset(drumValue)
    print("%c" % (drumValue + 64), end = '')
    drum = scrambler[1]
#    drumValue = (int)drum - 64 - drum2CoreOffset;
    drumValue = ord(drum) - 64 - drum2CoreOffset
    drumValue = WrapScramblerOffset(drumValue)
    print("%c" % (drumValue + 64), end = '')
    drum = scrambler[2]
#    drumValue = (int)drum - 64 - drum3CoreOffset;
    drumValue = ord(drum) - 64 - drum3CoreOffset
    drumValue = WrapScramblerOffset(drumValue)
    print("%c" % (drumValue + 64), end = '')

# ----------------------------------------------------------------------------
# Print out the diagonal board.
# ----------------------------------------------------------------------------
def PrintDiagonalBoard():
    print()
    print(" ", end = '')
    for i in range(26):
        print("%2c" % (chr(ord('A') + i)), end = '')
    print()
    for i in range(26):
        for j in range(26):
            # Print the rows.
            if j == 0:
                # If this is the test register print a ?
                if (chr(i + ord('A')) == testMenuLetter):
                    print("?", end = '')
                else:
                    print("%c" % (chr(i + ord('A'))), end = '')
            # Print the board.
            if (diagonalBoard[i][j] == -1):
                print(" x", end = '')
            elif (diagonalBoard[i][j] == 1):
                print(" |", end = '')
            elif (diagonalBoard[i][j] == 2):
                print(" o", end = '')
            else:
                print("  ", end = '')
        print()
    print()

# ----------------------------------------------------------------------------
# Print out the test register.
#----------------------------------------------------------------------------
def PrintTestRegister():

    for i in range(26):
        print("%c" % (chr(ord('A') + i)), end = '')
    print()
    for i in range(26):
        if (diagonalBoard[ord(testMenuLetter) - ord('A')][i] == 1):
            print("%c" % (' '), end = '')
        else:
            print("%c" % ('|'), end = '')
    print()

# ----------------------------------------------------------------------------
# Check position function.
# ----------------------------------------------------------------------------
def CheckDrumPosition(iteration):
    global stopFound, numStops
    
    numberVoltages = 0
    potentialStecker = ' '
    
    # Clear the diagonal board.
    ResetDiagonalBoard()
    

    # Set up the initial letters.
    SetDiagonalBoard(testMenuLetter, inputLetter)

    # Trace all voltages.
    Trace()

    # If we've traced all voltages check if we have a stop.
    numberVoltages, potentialStecker = CheckRegister(testMenuLetter)
    
    # If not all letters have a voltage we have a stop.
    if numberVoltages < 26:
        stopFound = True
        numStops += 1
        print("Stop %i found." % (numStops))
        print("Indicator: %s Iteration: %i" % (indicatorDrums, iteration))
        PrintTestRegister()

# ----------------------------------------------------------------------------
# Check a register to see if we have traced all voltages.
# ----------------------------------------------------------------------------
def CheckRegister(letter):
    traceCount = 0
    potentialStecker1 = ''
    potentialStecker25 = ''
    stecker = ''
    
    # If we've traced all voltages check for a stop.
    # Check each voltage.
#    PrintDiagonalBoard()
    for i in range(26):
        # Decrement count for each set voltage.
        if (diagonalBoard[ord(letter) - ord('A')][i] != 0):
            traceCount += 1

        # Store the potential stecker.
        if (diagonalBoard[ord(letter) - ord('A')][i] == 1):
            # Either the single voltage set.
            potentialStecker1 = i + ord('A')
        elif (diagonalBoard[ord(letter) - ord('A')][i] == 0):
            # Or the single voltage unset.
            potentialStecker25 = i + ord('A')

    # Return the correct stecker.
    if (traceCount == 1):
        # If one set return that one.
        stecker = potentialStecker1
    elif (traceCount == 25):
        # If 25 set return the one unset.
        stecker = potentialStecker25
    else:
        # Else return null.
        stecker = ''

    return traceCount, stecker

# ----------------------------------------------------------------------------
# Trace voltages.
# ----------------------------------------------------------------------------
def Trace():
    # Loop until we've finished tracing every voltage.
    while (untraced > 0):
        # For each menu letter.
        for j in range(numberMenuLetters):
            if (debugDiagonal == True):
                PrintDiagonalBoard()
            if (debugOther == True):
                print("Indicator: %s" % (indicatorDrums))
                print("Checking letter: %c" % (menuLetters[j]))
                print("Total untraced: %i" % (untraced))
            
            # Trace the voltage through the menu.
            # For each input voltage on this menu letter.
            for k in range(26):
                if (diagonalBoard[ord(menuLetters[j]) - ord('A')][k] == -1):
                    # If there is a -1 we trace it through.
                    TraceMenuLetterVoltages(j, k)
            if (untraced == 0):
                break;

# ----------------------------------------------------------------------------
# Trace voltages for this menu letter.
# ----------------------------------------------------------------------------
def TraceMenuLetterVoltages(menuLetterIndex, voltage):
    global untraced
    
    currentScrambler = 0
#    currentConnections = 0
    currentScramblerLetters = 0
    output = 0
    connectionCount = 0
    
    #Set this voltage as traced.
    diagonalBoard[ord(menuLetters[menuLetterIndex]) - ord('A')][voltage] = 1
    untraced -= 1
    
    if (debugOther == True):
        print("Tracing voltage on letter %c" % (voltage + ord('A')))
    # For each connected scrambler.
    for i in range(MAXNUMBERCONNECTIONS):
        # If we checked all scramblers we are done tracing.
        if (menuConnections[menuLetterIndex][i] == 0):
            break
        # Else send the voltage through this scrambler.
#        currentScrambler = scramblerOffsets[(menuConnections[menuLetterIndex][i]) - 1][0]
        currentScrambler = scramblerOffsets[(menuConnections[menuLetterIndex][i]) - 1]
        currentScramblerLetters = scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][0]
        if (debugOther == True):
            print("%2i:" % (menuConnections[menuLetterIndex][i]), end = '')
            PrintCorrectedScrambler(currentScrambler)
            print(" %c>" % (voltage + 65), end = '')
        output = Scrambler(voltage + 1, currentScrambler)
        if (debugOther == True):
            print("%c" % (output + 64))
        
        # Set a -1 on the other end of each connected scrambler.
        letter = chr(output + 64)
        for j in range(2):
            # Each scrambler is between two letters.
            if (scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][j] != menuLetters[menuLetterIndex]):
                # If its not this menu letter it's the opposite end.
                SetDiagonalBoard(scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][j], letter)

# ----------------------------------------------------------------------------
# Main program.
# ----------------------------------------------------------------------------
fileRead = False
menuFile = "menu_PV.txt"
# Read the menu file.
print("Reading menu file...")
fileRead = ReadSetupFile(menuFile)
if fileRead == False:
    print("Could not open input menu file.")
    print("Press STOP to shutdown.")
    runComplete = True

# Set up the drums and print out the configuration.
SetupDrums()
PrintSetupData()

print("Bombe finding next stop...")
print("Menu loaded. Press START to run.")

#	main loop.
while True:
    # If we are still calculating.
    if ((allIterationsDone == False) and (stopFound == False)):
        # Next iteration.
        numIterations += 1
        # Increment all the scramblers.	
        IncrementScramblers()
        # Decrement the indicator drums.
        DecrementIndicator()
        # Don't check the half cycles.
        if (numIterations % 39) >= 13:
            # Check this position.
            CheckDrumPosition(numIterations)
            if debugOther == True:
                print("Iteration: %i\tIndicator: %s\t%i *" % (numIterations, indicatorDrums, numIterations % 39))
                PrintScramblers()
        elif debugOther == True:
            print("Iteration: %i\tIndicator: %s\t%i" % (numIterations, indicatorDrums, numIterations % 39))
            PrintScramblers();
#
#		# If a stop was found and the Arduino is running wait for it
#		# to catch up.
    if ((allIterationsDone == False) and (stopFound == True)):
        stopFound = False
#
#    # If we've found all stops and the Arduino is running wait for it
#    # to finish.
    if ((allIterationsDone == True) and (runComplete == False)):
        runComplete = True  
        # Complete.
        print("Bombe run complete.")
        print("Press STOP to shutdown.")
        print("Iterations:", numIterations)
#        break