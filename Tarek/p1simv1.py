from __future__ import print_function
import os

# array of the gate inputs for part 1
gateIn = [] 

# array of the fault input 
FaultList = [] 

# array of the fault list after cleaning for easier reading 
cleanFaultList = []

# array of the undetected fault 
undetectedList  = [] 

# array of the detected fault 
detectedList  = [] 

# array of the fault circuit
faultCircuit  = [] 

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: the actual simulation #
def basic_sim(circuit):
    # QUEUE and DEQUEUE
    # Creating a queue, using a list, containing all of the gates in the circuit
    queue = list(circuit["GATES"][1])
    i = 1

    while True:
        i -= 1
        # If there's no more things in queue, done
        if len(queue) == 0:
            break

        # Remove the first element of the queue and assign it to a variable for us to use
        curr = queue[0]
        queue.remove(curr)

        # initialize a flag, used to check if every terminal has been accessed
        term_has_value = True

        # Check if the terminals have been accessed
        for term in circuit[curr][1]:
            if not circuit[term][2]:
                term_has_value = False
                break

        if term_has_value:
            circuit[curr][2] = True
            circuit = gateCalc(circuit, curr)

            # ERROR Detection if LOGIC does not exist
            if isinstance(circuit, str):
                print(circuit)
                return circuit

            print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][0] + " for:")
            for term in circuit[curr][1]:
                print(term + " = " + circuit[term][3])
            print("\nPress Enter to Continue...")
            input()

        else:
            # If the terminals have not been accessed yet, append the current node at the end of the queue
            queue.append(curr)

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: the actual simulation #
def fault_sim(circuit):
    # QUEUE and DEQUEUE
    # Creating a queue, using a list, containing all of the gates in the circuit
    queue = list(circuit["GATES"][1])
    i = 1

    while True:
        i -= 1
        # If there's no more things in queue, done
        if len(queue) == 0:
            break

        # Remove the first element of the queue and assign it to a variable for us to use
        curr = queue[0]
        queue.remove(curr)

        # initialize a flag, used to check if every terminal has been accessed
        term_has_value = True

        # Check if the terminals have been accessed
        for term in circuit[curr][1]:
            if not circuit[term][2]:
                term_has_value = False
                break

        if term_has_value:
            circuit[curr][2] = True
            circuit = gateCalc(circuit, curr)

            # ERROR Detection if LOGIC does not exist
            if isinstance(circuit, str):
                print(circuit)
                return circuit

            print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][0] + " for:")
            for term in circuit[curr][1]:
                print(term + " = " + circuit[term][3])
            print("\nPress Enter to Continue...")
            input()

        else:
            # If the terminals have not been accessed yet, append the current node at the end of the queue
            queue.append(curr)

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the Circuit gate-level netlist file:
def netRead(netName):
    # Opening the netlist file:
    netFile = open(netName, "r")

    # temporary variables
    inputs = []  # array of the input wires
    outputs = []  # array of the output wires
    gates = []  # array of the gate list
    inputBits = 0  # the number of inputs needed in this given circuit

    # main variable to hold the circuit netlist, this is a dictionary in Python, where:
    # key = wire name; value = a list of attributes of the wire
    circuit = {}

    # Reading in the netlist file line by line
    for line in netFile:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue

        # @ Here it should just be in one of these formats:
        # INPUT(x)
        # OUTPUT(y)
        # z=LOGIC(a,b,c,...)

        # Read a INPUT wire and add to circuit:
        if (line[0:5] == "INPUT"):
            # Removing everything but the line variable name
            line = line.replace("INPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Format the variable name to wire_*VAR_NAME*
            line = "wire_" + line

            # Error detection: line being made already exists
            if line in circuit:
                msg = "NETLIST ERROR: INPUT LINE \"" + line + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
                print(msg + "\n")
                return msg

            # Appending to the inputs array and update the inputBits
            inputs.append(line)


            # add this wire as an entry to the circuit dictionary
            circuit[line] = ["INPUT", line, False, 'U']
            inputBits += 1
            print(line)
            print(circuit[line])
            continue

        # Read an OUTPUT wire and add to the output array list
        # Note that the same wire should also appear somewhere else as a GATE output
        if line[0:6] == "OUTPUT":
            # Removing everything but the numbers
            line = line.replace("OUTPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Appending to the output array
            outputs.append("wire_" + line)
            continue

        # Read a gate output wire, and add to the circuit dictionary
        lineSpliced = line.split("=")  # splicing the line at the equals sign to get the gate output wire
        gateOut = "wire_" + lineSpliced[0]
        # Error detection: line being made already exists
        if gateOut in circuit:
            msg = "NETLIST ERROR: GATE OUTPUT LINE \"" + gateOut + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
            print(msg + "\n")
            return msg

        # Appending the dest name to the gate list
        gates.append(gateOut)

        lineSpliced = lineSpliced[1].split("(")  # splicing the line again at the "("  to get the gate logic
        logic = lineSpliced[0].upper()
        lineSpliced[1] = lineSpliced[1].replace(")", "")
        terms = lineSpliced[1].split(",")  # Splicing the the line again at each comma to the get the gate terminals
        gateIn.append(terms)
        # Turning each term into an integer before putting it into the circuit dictionary
        terms = ["wire_" + x for x in terms]


        # add the gate output wire to the circuit dictionary with the dest as the key
        circuit[gateOut] = [logic, terms, False, 'U']
        print(gateOut)
        print(circuit[gateOut])

    # now after each wire is built into the circuit dictionary,
    # add a few more non-wire items: input width, input array, output array, gate list
    # for convenience

    circuit["INPUT_WIDTH"] = ["input width:", inputBits]
    circuit["INPUTS"] = ["Input list", inputs]
    circuit["OUTPUTS"] = ["Output list", outputs]
    circuit["GATES"] = ["Gate list", gates]


    print("\n bookkeeping items in circuit: \n")
    print(circuit["INPUT_WIDTH"])
    print(circuit["INPUTS"])
    print(circuit["OUTPUTS"])
    print(circuit["GATES"])

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Updating the circuit dictionary with the input line, and also resetting the gates and output lines
def inputRead(circuit, line):
    # Checking if input bits are enough for the circuit
    if len(line) < circuit["INPUT_WIDTH"][1]:
        return -1

    # Getting the proper number of bits:
    line = line[(len(line) - circuit["INPUT_WIDTH"][1]):(len(line))]

    # Adding the inputs to the dictionary
    # Since the for loop will start at the most significant bit, we start at input width N
    i = circuit["INPUT_WIDTH"][1] - 1
    inputs = list(circuit["INPUTS"][1])
    # dictionary item: [(bool) If accessed, (int) the value of each line, (int) layer number, (str) origin of U value]
    for bitVal in line:
        bitVal = bitVal.upper() # in the case user input lower-case u
        circuit[inputs[i]][3] = bitVal # put the bit value as the line value
        circuit[inputs[i]][2] = True  # and make it so that this line is accessed

        # In case the input has an invalid character (i.e. not "0", "1" or "U"), return an error flag
        if bitVal != "0" and bitVal != "1" and bitVal != "U":
            return -2
        i -= 1 # continuing the increments

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: to chech if there is any faults in inputs
def inputFaultsRead():
    global detectedList
    global undetectedList

    queue = list(faultCircuit["INPUTS"][1])

    for item in queue:
        for line in cleanFaultList:
            if item == line[0] and faultCircuit[item][3] != line[1]:
                   print("fault detected")
                   detectedList.append(FaultList[cleanFaultList.index(line)])
                   undetectedList.remove(FaultList[cleanFaultList.index(line)])


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the TV file
def tvRead(tvName):
    # Opening the tvName file:
    tvFile = open(tvName, "r")

    # temporary variables
    inputs = []  # array of the test vectors


    # Reading in the netlist file line by line
    for line in tvFile:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue
        
        inputs.append(line)

    return inputs


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the fault list file
def faultlistRead(faultName):
    # Opening the faultName file:
    faultFile = open(faultName, "r")

    # temporary variables
    inputs = []  # array of the faults


    # Reading in the netlist file line by line
    for line in faultFile:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue
        
        inputs.append(line)

    return inputs


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Generates full fault list, Part 1 from the project
def generateFullFaultList():

    i = 0 # counter used for fault generation (specifically generating the gate input faults)
    numFault = 0
    cktFile = SelectBenchFile()
    print("\n Reading " + cktFile + " ... \n")
    circuit = netRead(cktFile)

    outputFile = open("full_f_list.txt", "w")

    outputFile.write("# " + cktFile + "\n# Full SSA fault List" + "\n" + "\n")
    # Creating fault list for inputs
    for x in circuit["INPUTS"][1]:
        if (x[0:5] == "wire_"):
            x = x.replace("wire_", "")
            outputFile.write(x + "-SA-0" + "\n")
            outputFile.write(x + "-SA-1" + "\n")
        numFault += 1

    # Creating fault list for each input and outputs for all gates
    for x in circuit["GATES"][1]:
        z = 0
        # Getting rid part of string to leave only line variable
        if (x[0:5] == "wire_"):
            x = x.replace("wire_", "")
            outputFile.write(x + "-SA-0" + "\n")
            outputFile.write(x + "-SA-1" + "\n")
            # Changing Concatenate into str and getting rid of everything but wire variables
            y = str(gateIn[i])
            y = y.replace("['", "")
            y = y.replace("']", "")
            y = y.replace("', '", "")
            inputNum = (len(y))     # number of variables to consider when going through str
            numFault += 1
            numFault = numFault + inputNum

            # Taking each input variable and putting it into a SA-0 and SA-1 per gate
            if inputNum > 1:
                while inputNum >= 1:
                    gateVar = y[z]
                    inputNum -= 1
                    outputFile.write(x + "-in-" + gateVar + "-SA-0" + "\n")
                    outputFile.write(x + "-in-" + gateVar + "-SA-1" + "\n")
                    z += 1

            else:
                # If there is only 1 input for gate just put it in SA-1 and SA-0
                outputFile.write(y + "-in-" + x + "-SA-0" + "\n")
                outputFile.write(y + "-in-" + x + "-SA-1" + "\n")
            i += 1
    numFault = numFault*2 # multiply by 2 for 2 different fault states
    outputFile.write("\n" + "Total Fault: " + str(numFault))

    outputFile.close()
# -------------------------------------------------------------------------------------------------------------------- #




    print("\n Finished processing benchmark file and built netlist dictionary: \n")
    # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
    #printCkt(circuit)
    print(circuit)


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Fault Simulation, Part 2 from the project
def faultSimulation():

    global FaultList
    global detectedList
    global faultCircuit
    global cleanFaultList
    global undetectedList

    BenchFile = SelectBenchFile()
    FaultListFile = SelectFaultListFile()
    TestVectorFile = SelectTestVectorFile()

    print("\n Reading " + BenchFile + " ... \n")
    circuit = netRead(BenchFile)

    print("\n Reading " + FaultListFile + " ... \n")
    FaultList = faultlistRead(FaultListFile)


    print("\n Reading " + TestVectorFile + " ... \n")
    tests = tvRead(TestVectorFile)

    outputFile = open("fault_sim_result.txt", "w")
    outputFile.write("# fault sim result\n" + "# input: " + BenchFile + "\n# input: " + FaultListFile + "\n# input: " + TestVectorFile + "\n\n\n")

    for item in tests:
        undetectedList = FaultList.copy()
        cleanFaultList = CleanFaultList(FaultList)

        circuit = inputRead(circuit, item)
        faultCircuit = circuit.copy()
        inputFaultsRead()

        circuit = basic_sim(circuit)
        #faultCircuit = fault_sim(faultCircuit)
        

        for curr in circuit["OUTPUTS"][1]:
            output = circuit[curr][3]


        outputFile.write("tv" + str(tests.index(item) + 1) + " = " + item + "->  " + str(output) + "  (good)\n" + "detected:\n")

        for line in detectedList:
            outputFile.write(line + ": " + item + " -> " + "" + "\n")

        outputFile.write("\n")
        detectedList.clear()

    outputFile.write("total detected faults:  " + str(len(FaultList) - len(undetectedList))+ "\n\nundetected faults:  " +str(len(undetectedList)) + "\n\nfault coverage:  " +str(len(FaultList) - len(undetectedList))+ "/" +str(len(FaultList))+ " = " + str(int(((len(FaultList) - len(undetectedList))/len(FaultList))*100)) + "%\n")


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Test Vector Set Generation, Part 3 from the project
def testVectorSetGeneration():

     BenchFile = SelectBenchFile()
     FaultListFile = SelectFaultListFile()

     print("\n Reading " + BenchFile + " ... \n")
     circuit = netRead(BenchFile)

     print("\n Reading " + FaultListFile + " ... \n")
     FaultList = faultlistRead(FaultListFile)

     outputFile = open("tv_set.txt", "w")
     outputFile.write("# Test vector set that can cover > 90% of the faults\n" + "for " + BenchFile + "\n# " + FaultListFile + "\n\n")


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: read input bench file
def SelectBenchFile():

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    # Select circuit benchmark file, default is circuit.bench
    while True:
        cktFile = "circuit.bench"
        print("\n Read circuit benchmark file: use " + cktFile + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            userInput = "circuit.bench"
            return userInput
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist. \n")
            else:
                return userInput


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: input fault list file (default: f_list.txt)
def SelectFaultListFile():

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    # Select input file, default is input.txt
    while True:
        inputName = "f_list.txt"
        print("\n Read input fault list file: use " + inputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            userInput = "f_list.txt"
            return userInput
        else:
            inputName = os.path.join(script_dir, userInput)
            if not os.path.isfile(inputName):
                print("File does not exist. \n")
            else:
                return userInput


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION:  test vector input file (default: input.txt)
def SelectTestVectorFile():

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    # Select input file, default is input.txt
    while True:
        inputName = "input.txt"
        print("\n Read input test vector file: use " + inputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            userInput = "input.txt"
            return userInput
        else:
            inputName = os.path.join(script_dir, userInput)
            if not os.path.isfile(inputName):
                print("File does not exist. \n")
            else:
                return userInput


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: to orgnize the fault list
def CleanFaultList(fList):

    templist = []

    for temp in fList:

        curr = temp
        curr = temp.split("-")
        curr[0] = "wire_" + curr[0]
        curr.pop(1)

        if len(curr) > 2:
            curr[1] = "wire_" + curr[1]
            curr.pop(2)

        templist.append(curr)

    return templist


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: calculates the output value for each logic gate
def gateCalc(circuit, node):
    
    # terminal will contain all the input wires of this logic gate (node)
    terminals = list(circuit[node][1])  

    # If the node is an Inverter gate output, solve and return the output
    if circuit[node][0] == "NOT":
        if circuit[terminals[0]][3] == '0':
            circuit[node][3] = '1'
        elif circuit[terminals[0]][3] == '1':
            circuit[node][3] = '0'
        elif circuit[terminals[0]][3] == "U":
            circuit[node][3] = "U"
        else:  # Should not be able to come here
            return -1
        return circuit

    # If the node is an AND gate output, solve and return the output
    elif circuit[node][0] == "AND":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a flag that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 at any input terminal, AND output is 0. If there is an unknown terminal, mark the flag
        # Otherwise, keep it at 1
        for term in terminals:  
            if circuit[term][3] == '0':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is a NAND gate output, solve and return the output
    elif circuit[node][0] == "NAND":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 terminal, NAND changes the output to 1. If there is an unknown terminal, it
        # changes to "U" Otherwise, keep it at 0
        for term in terminals:
            if circuit[term][3] == '0':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
                break

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an OR gate output, solve and return the output
    elif circuit[node][0] == "OR":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, OR changes the output to 1. Otherwise, keep it at 0
        for term in terminals:
            if circuit[term][3] == '1':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an NOR gate output, solve and return the output
    if circuit[node][0] == "NOR":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, NOR changes the output to 0. Otherwise, keep it at 1
        for term in terminals:
            if circuit[term][3] == '1':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is an XOR gate output, solve and return the output
    if circuit[node][0] == "XOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there are an odd number of terminals, XOR outputs 1. Otherwise, it should output 0
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # If the node is an XNOR gate output, solve and return the output
    elif circuit[node][0] == "XNOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there is a single 1 terminal, XNOR outputs 0. Otherwise, it outputs 1
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # Error detection... should not be able to get at this point
    return circuit[node][0]


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Main Function
def main():
    # **************************************************************************************************************** #
    # NOTE: UI code; Does not contain anything about the actual simulation

    # Used for file access

    while True:
        print("Enter what do want to do: ", "1. Generate Full Fault List","2. Fault Simulation","3. Test Vector Set Generation","4. Exit", sep="\n")
        menu = int(input())

        if menu == 1:
            generateFullFaultList()
            break
        elif menu == 2:
            faultSimulation()
            break
        elif menu == 3:
            testVectorSetGeneration()
            break
        elif menu == 4:
            break
        else:
            print("Please Enter a Valid Input!!")


if __name__ == "__main__":
    main()
