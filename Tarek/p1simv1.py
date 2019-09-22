from __future__ import print_function
import os

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the Circuit gate-level netlist file:
def netRead(netName):
    # Opening the netlist file:
    netFile = open(netName, "r")

    # temporary variables
    inputs = []  # array of the input wires
    outputs = []  # array of the output wires
    gates = []  # array of the gate list
    gateIn = [] # array of the gate inputs
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
# FUNCTION: Part 1 from the project
def generateFullFaultList():

    i = 0 # counter used for fault generation (specifically generating the gate input faults)
    numFault = 0
    cktFile = SelectBenchFile()
    print("\n Reading " + cktFile + " ... \n")
    circuit = netRead(cktFile)

    # -------------------------------------------------------------------------------------------------------------------- #
    # FUNCTION: Generates full fault list (put this in its own function call?)
    # Still need ask user for a fault list output file
    outputFile = open("full_f_list.txt", "w")

    outputFile.write("Full SSA fault List" + "\n" + "\n")
    # Creating fault list for inputs
    for x in circuit["INPUTS"]:
        if (x[0:5] == "wire_"):
            x = x.replace("wire_", "")
            outputFile.write(x + "-SA-0" + "\n")
            outputFile.write(x + "-SA-1" + "\n")
        numFault += 1

    # Creating fault list for each input and outputs for all gates
    for x in circuit["GATES"]:
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
# FUNCTION: Part 2 from the project
def faultSimulation():
    print(hi)

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Part 3 from the project
def testVectorSetGeneration():
    print(hi)

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
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist. \n")
            else:
                return userInput

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
