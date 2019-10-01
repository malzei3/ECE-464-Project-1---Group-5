from __future__ import print_function
import os
import copy

# Function List:
# 1. netRead: read the benchmark file and build circuit netlist (Added full fault generation to a list)
# 2. gateCalc: function that will work on the logic of each gate
# 3. inputRead: function that will update the circuit dictionary made in netRead to hold the line values
# 4. basic_sim: the actual simulation
# 5. main: The main function

# global variables (because I didn't want to make a class)
inputF = []
faultOutput = []
faultItem = []


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Neatly prints the Circuit Dictionary:
def printCkt(circuit):
    print("INPUT LIST:")
    for x in circuit["INPUTS"][1]:
        print(x + "= ", end='')
        print(circuit[x])

    print("\nOUTPUT LIST:")
    for x in circuit["OUTPUTS"][1]:
        print(x + "= ", end='')
        print(circuit[x])

    print("\nGATE list:")
    for x in circuit["GATES"][1]:
        print(x + "= ", end='')
        print(circuit[x])
    print()


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the Circuit gate-level netlist file:
def netRead(netName):
    # Opening the netlist file:
    netFile = open(netName, "r")

    # temporary variables
    inputs = []  # array of the input wires
    outputs = []  # array of the output wires
    gates = []  # array of the gate list
    gateIn = []  # array of the gate inputs
    inputBits = 0  # the number of inputs needed in this given circuit
    i = 0  # counter used for fault generation (specifically generating the gate input faults)
    numFault = 0
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

    # -------------------------------------------------------------------------------------------------------------------- #
    # FUNCTION: Generates full fault list (put this in its own function call?)
    # Still need ask user for a fault list output file
    outputFile = open("full_f_list.txt", "w")

    outputFile.write("#  Full SSA fault List" + "\n" + "\n")
    # Creating fault list for inputs
    for x in inputs:
        if (x[0:5] == "wire_"):
            x = x.replace("wire_", "")
            outputFile.write(x + "-SA-0" + "\n")
            outputFile.write(x + "-SA-1" + "\n")
        numFault += 1

    # Creating fault list for each input and outputs for all gates
    for x in gates:
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
            y = y.split("', '")
            inputNum = (len(y))  # number of variables to consider when going through str
            numFault += 1
            numFault = numFault + inputNum

            # Taking each input variable and putting it into a SA-0 and SA-1 per gate
            if inputNum > 1:
                while inputNum >= 1:
                    gateVar = y[inputNum-1]
                    inputNum -= 1
                    outputFile.write(x + "-IN-" + gateVar + "-SA-0" + "\n")
                    outputFile.write(x + "-IN-" + gateVar + "-SA-1" + "\n")
                    z += 1

            else:
                # If there is only 1 input for gate just put it in SA-1 and SA-0
                outputFile.write(y[0] + "-IN-" + x + "-SA-0" + "\n")
                outputFile.write(y[0] + "-IN-" + x + "-SA-1" + "\n")
            i += 1
    numFault = numFault * 2  # multiply by 2 for 2 different fault states
    outputFile.write("\n" + "# Total Fault: " + str(numFault))

    outputFile.close()
    # -------------------------------------------------------------------------------------------------------------------- #
    return circuit


# -------------------------------------------------------------------------------------------------------------------- #


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
        bitVal = bitVal.upper()  # in the case user input lower-case u
        circuit[inputs[i]][3] = bitVal  # put the bit value as the line value
        circuit[inputs[i]][2] = True  # and make it so that this line is accessed

        # In case the input has an invalid character (i.e. not "0", "1" or "U"), return an error flag
        if bitVal != "0" and bitVal != "1" and bitVal != "U":
            return -2
        i -= 1  # continuing the increments

    return circuit


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

            #print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][
            #    0] + " for:")
            #for term in circuit[curr][1]:
            #    print(term + " = " + circuit[term][3])
            #print("\nPress Enter to Continue...")
            #input()

        else:
            # If the terminals have not been accessed yet, append the current node at the end of the queue
            queue.append(curr)

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: reads the input faults that need to be tested
def faultRead(faultFile):
    # opening list of faults to check
    faultHere = []
    faultsList = open(faultFile, "r")
    faultExist = open("full_f_list.txt", "r")
    for line in faultsList:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue
        faultItem.append(line)
        if "-SA-" in line:
            if "-IN-" not in line:
                line = line.replace("-SA-", "/")
                inputF.append(line)

        if "-IN-" in line:
            line = line.replace("-IN-", "/")
            line = line.replace("-SA-", "/")
            inputF.append(line)

    # -------------------------------------------------------------------------------------------------------------------- #
    # FUNCTION: Detects if the f_list faults actually exist in the possible full fault list (if not EXIT)
    for line in faultExist:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")

        # NOT Reading any comments
        if (line[0] == "#"):
            continue
        faultHere.append(line)
    for x in faultItem:
        if x not in faultHere:
            print(x)
            print("FAULT INPUT DOES NOT EXIST IN POSSIBLE FAULT LIST: EXITING")
            exit()
    return


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: The Fault Simulator runs the circuit with SA-1/0 faults runs through ALL FAULTS
def fault_sim(circuit):
    # QUEUE and DEQUEUE
    # Creating a queue, using a list, containing all of the gates in the circuit
    faultCirc = copy.deepcopy(circuit)

    foutput = ""
    for x in inputF:
        x = x.split("/")

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

                for term in circuit[curr][1]:
                    wireName = x[0]
                    faultWire = "wire_" + wireName
                    inputs = list(circuit["INPUTS"][1])

                    #RUNS through faults (first section does input faults and output faults)
                    for w in inputs:
                        if w == faultWire:
                            if len(x) == 2:
                                circuit[w][3] = x[1]

                    #Faults that are gate inputs
                    if curr == faultWire:
                        if len(x) == 2:
                            circuit[curr][3] = x[1]
                        elif term == "wire_" + x[1]:
                            circuit[term][3] = x[2]
                            circuit = gateCalc(circuit, curr)
                    else:
                        circuit = gateCalc(circuit, curr)

                # ERROR Detection if LOGIC does not exist
                if isinstance(circuit, str):
                    print(circuit)
                    return circuit

                #Uncomment for debugging purposes (step by step)
                #print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][
                #    0] + " for:")
                #for term in circuit[curr][1]:
                #   print(term + " = " + circuit[term][3])
                #   print("\nPress Enter to Continue...")
                #   input()

            else:
                # If the terminals have not been accessed yet, append the current node at the end of the queue
                queue.append(curr)
        for y in circuit["OUTPUTS"][1]:
            if not circuit[y][2]:
                foutput = "NETLIST ERROR: OUTPUT LINE \"" + y + "\" NOT ACCESSED"
                break
            foutput = str(circuit[y][3]) + foutput
        faultOutput.append(foutput)
        foutput = ""
        circuit = copy.deepcopy(faultCirc)
    # Uncomment to see fault sim results for each fault input (Match arrays together)
    # print(faultItem)
    # print(faultOutput)

    return circuit


# FUNCTION: Main Function
def main():
    # **************************************************************************************************************** #
    # NOTE: UI code; Does not contain anything about the actual simulation
    # Used for file access
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    print("Circuit Simulator:")

    # Select circuit benchmark file, default is circuit.bench
    while True:
        cktFile = "circuit.bench"
        print("\n Read circuit benchmark file: use " + cktFile + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist. \n")
            else:
                break
    # Select input fault file, default is f_list.txt
    while True:
        faultyCkt = "f_list.txt"
        print("\n Read circuit fault list file: use " + faultyCkt + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            faultyCkt = os.path.join(script_dir, userInput)
            if not os.path.isfile(faultyCkt):
                print("File does not exist. \n")
            else:
                break

    print("\n Reading " + cktFile + " ... \n")
    circuit = netRead(cktFile)
    faultRead(faultyCkt)
    print("\n Finished processing benchmark file and built netlist dictionary: \n")
    # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
    # printCkt(circuit)
    print(circuit)

    # keep an initial (unassigned any value) copy of the circuit for an easy reset (DOESN'T WORK is a pointer)
    newCircuit = circuit

    # Select input file, default is input.txt
    while True:
        inputName = "input.txt"
        print("\n Read input vector file: use " + inputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            inputName = os.path.join(script_dir, userInput)
            if not os.path.isfile(inputName):
                print("File does not exist. \n")
            else:
                break

    # Select output file, default is output.txt
    while True:
        outputName = "output.txt"
        print("\n Write output file: use " + outputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            outputName = os.path.join(script_dir, userInput)
            break

    # Note: UI code;
    # **************************************************************************************************************** #

    print("\n *** Simulating the" + inputName + " file and will output in" + outputName + "*** \n")
    inputFile = open(inputName, "r")
    outputFile = open(outputName, "w")

    faultFound = []
    faultDetected = []
    faultUndetected = []

    outputFile.write("# fault sim result" + "\n")
    outputFile.write("# input: " + cktFile + "\n")
    outputFile.write("# input: " + inputName + "\n")
    outputFile.write("# input: " + faultyCkt + "\n" + "\n")
    i = 1

    # Runs the simulator for each line of the input file
    for line in inputFile:
        # Initializing output variable each input line
        output = ""
        faultNum = 0
        # Do nothing else if empty lines, ...
        if (line == "\n"):
            continue
        # ... or any comments
        if (line[0] == "#"):
            continue

        # Removing the the newlines at the end and then output it to the txt file
        line = line.replace("\n", "")
        outputFile.write("tv" + str(i) + " = " + line)

        # Removing spaces
        line = line.replace(" ", "")

        print("\n before processing circuit dictionary...")
        # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
        # printCkt(circuit)
        print(circuit)
        print("\n ---> Now ready to simulate INPUT = " + line)
        circuit = inputRead(circuit, line)
        # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
        # printCkt(circuit)
        print(circuit)

        if circuit == -1:
            print("INPUT ERROR: INSUFFICIENT BITS")
            outputFile.write(" -> INPUT ERROR: INSUFFICIENT BITS" + "\n")
            # After each input line is finished, reset the netList
            circuit = newCircuit
            print("...move on to next input\n")
            continue
        elif circuit == -2:
            print("INPUT ERROR: INVALID INPUT VALUE/S")
            outputFile.write(" -> INPUT ERROR: INVALID INPUT VALUE/S" + "\n")
            # After each input line is finished, reset the netList
            circuit = newCircuit
            print("...move on to next input\n")
            continue
        circuit = fault_sim(circuit)
        circuit = basic_sim(circuit)
        print("\n *** Finished simulation - resulting circuit: \n")
        # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
        # printCkt(circuit)
        print(circuit)

        for y in circuit["OUTPUTS"][1]:
            if not circuit[y][2]:
                output = "NETLIST ERROR: OUTPUT LINE \"" + y + "\" NOT ACCESSED"
                break
            output = str(circuit[y][3]) + output
        print("\n *** Summary of simulation: ")
        print(line + " -> " + output + " written into output file. \n")
        outputFile.write(" -> " + output + " (good)" + "\n")
        outputFile.write("detected:" + "\n")

        for x in faultOutput:
            if x != output:
                outputFile.write(faultItem[faultNum] + ": " + line + " -> " + x + "\n")
                faultFound.append(faultItem[faultNum])
            faultNum += 1
        outputFile.write("\n")

        faultOutput.clear()
        # After each input line is finished, reset the circuit
        print("\n *** Now resetting circuit back to unknowns... \n")

        for key in circuit:
            if (key[0:5] == "wire_"):
                circuit[key][2] = False
                circuit[key][3] = 'U'

        print("\n circuit after resetting: \n")
        # Uncomment the following line, for the neater display of the function and then comment out print(circuit)
        # printCkt(circuit)
        print(circuit)

        print("\n*******************\n")

    # Creates total faults detected and undetected
    for x in faultItem:
        if x not in faultFound:
            faultUndetected.append(x)
    for x in faultItem:
        if x not in faultUndetected:
            faultDetected.append(x)

    outputFile.write("Total detected faults: " + str(len(faultDetected)) + "\n")
    for x in faultDetected:
        outputFile.write(x + "\n")

    outputFile.write("\n" + "Total undetected faults: " + str(len(faultUndetected)) + "\n")
    for x in faultUndetected:
        outputFile.write(x + "\n")

    outputFile.write("\n" + "Fault Coverage: " + str(len(faultDetected)) + "/" + str(len(faultItem)) + " = " +
                     str(len(faultDetected) / len(faultItem) * 100) + "%")

    outputFile.close
    # exit()


if __name__ == "__main__":
    main()
