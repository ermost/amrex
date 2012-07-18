#!/usr/bin/env python

import sys
import string
import getopt

Header="""\
! DO NOT EDIT THIS FILE!!!
!
! This file is automatically generated by write_probin.py at
! compile-time.
!
! To add a runtime parameter, do so by editting the appropriate _parameters
! file.

"""


#=============================================================================
# the parameter object will hold the runtime parameters
#=============================================================================
class parameter:

    def __init__(self):
        self.var = ""
        self.type = ""
        self.value = ""


#=============================================================================
# getNextLine returns the next, non-blank line, with comments stripped
#=============================================================================
def getNextLine(fin):

    line = fin.readline()

    pos = str.find(line, "#")

    while ((pos == 0) or (str.strip(line) == "") and line):

        line = fin.readline()
        pos = str.find(line, "#")

    line = line[:pos]

    return line



#=============================================================================
# getParamIndex looks through the list and returns the index corresponding to
# the parameter specified by var
#=============================================================================
def getParamIndex(paramList, var):

    index = -1

    n = 0
    while (n < len(paramList)):
        
        if (paramList[n].var == var):
            index = n
            break

        n += 1

    return index



#=============================================================================
# parseParamFile read all the parameters in a given parameter file and adds
# valid parameters to the params list.
#=============================================================================
def parseParamFile(paramsList, paramFile, otherList=None):

    # if otherList is present, we will search through it to make sure
    # we don't add a duplicate parameter.
    if (otherList==None):
        otherList = []

    err = 0

    try: f = open(paramFile, "r")
    except IOError:
        print("write_probin.py: ERROR: file "+str(paramFile)+" does not exist")
        sys.exit(2)
    else:
        f.close()
        
    f = open(paramFile, "r")

    print("write_probin.py: working on parameter file "+str(paramFile)+"...")

    line = getNextLine(f)

    while (line and not err):

        fields = line.split()

        if (not (len(fields) == 3)):
            print(line)
            print("write_probin.py: ERROR: missing one or more fields in parameter definition.")
            err = 1
            continue

        currentParam = parameter()
            
        currentParam.var   = fields[0]
        currentParam.type  = fields[1]
        currentParam.value = fields[2]

        # check to see if this parameter is defined in the current list
        # or otherList
        index = getParamIndex(paramsList, currentParam.var)
        index2 = getParamIndex(otherList, currentParam.var)

        if (index >= 0 or index2 > 0):
            print("write_probin.py: ERROR: parameter %s already defined." % (currentParam.var))
            err = 1                


            
        paramsList.append(currentParam)

        line = getNextLine(f)

    return err


#=============================================================================
# abort exits when there is an error.  A dummy stub file is written
# out, which will cause a compilation failure
# =============================================================================
def abort(outfile):

    fout = open(outfile, "w")
    fout.write("There was an error parsing the parameter files")
    fout.close()
    sys.exit(1)

    

#=============================================================================
# write_probin will read through the list of parameter files and output 
# the new outFile
#=============================================================================
def write_probin(probinTemplate, paramAFiles, paramBFiles, 
                 namelistName, outFile):

    paramsA = []
    paramsB = []

    print(" ")
    print("write_probin.py: creating %s" % (outFile))

    #-------------------------------------------------------------------------
    # read the parameters defined in the parameter files
    #-------------------------------------------------------------------------
    for f in paramAFiles:
        err = parseParamFile(paramsA, f)
        
        if (err):
            abort(outFile)


    for f in paramBFiles:
        err = parseParamFile(paramsB, f, otherList=paramsA)
        
        if (err):
            abort(outFile)


    # params will hold all the parameters (from both lists A and B)
    params = paramsA + paramsB
            

    #-------------------------------------------------------------------------
    # open up the template
    #-------------------------------------------------------------------------
    try: ftemplate = open(probinTemplate, "r")
    except IOError:
        print("write_probin.py: ERROR: file "+str(probinTemplate)+" does not exist")
        sys.exit(2)
    else:
        ftemplate.close()

    ftemplate = open(probinTemplate, "r")

    templateLines = []
    line = ftemplate.readline()
    while (line):
        templateLines.append(line)
        line = ftemplate.readline()


    #-------------------------------------------------------------------------
    # output the template, inserting the parameter info in between the @@...@@
    #-------------------------------------------------------------------------
    fout = open(outFile, "w")

    fout.write(Header)

    for line in templateLines:

        index = line.find("@@")

        if (index >= 0):
            index2 = line.rfind("@@")

            keyword = line[index+len("@@"):index2]
            indent = index*" "

            if (keyword == "declarationsA"):

                # declaraction statements
                n = 0
                while (n < len(paramsA)):

                    type = paramsA[n].type

                    if (type == "real"):
                        fout.write("%sreal (kind=dp_t), save, public :: %s = %s\n" % 
                                   (indent, paramsA[n].var, paramsA[n].value))

                    elif (type == "character"):
                        fout.write("%scharacter (len=256), save, public :: %s = %s\n" % 
                                   (indent, paramsA[n].var, paramsA[n].value))

                    elif (type == "integer"):
                        fout.write("%sinteger, save, public :: %s = %s\n" % 
                                   (indent, paramsA[n].var, paramsA[n].value))

                    elif (type == "logical"):
                        fout.write("%slogical, save, public :: %s = %s\n" % 
                                   (indent, paramsA[n].var, paramsA[n].value))

                    else:
                        print("write_probin.py: invalid datatype for variable "+paramsA[n].var)

                    n += 1

                if (len(paramsA) == 0):
                    fout.write("%sinteger, save, public :: a_dummy_var = 0\n" % (indent))

            elif (keyword == "declarationsB"):

                if (len(paramsB) > 0):

                    # declaraction statements
                    n = 0
                    while (n < len(paramsB)):

                        type = paramsB[n].type

                        if (type == "real"):
                            fout.write("%sreal (kind=dp_t), save, public :: %s = %s\n" % 
                                       (indent, paramsB[n].var, paramsB[n].value))

                        elif (type == "character"):
                            fout.write("%scharacter (len=256), save, public :: %s = %s\n" % 
                                       (indent, paramsB[n].var, paramsB[n].value))

                        elif (type == "integer"):
                            fout.write("%sinteger, save, public :: %s = %s\n" % 
                                       (indent, paramsB[n].var, paramsB[n].value))

                        elif (type == "logical"):
                            fout.write("%slogical, save, public :: %s = %s\n" % 
                                       (indent, paramsB[n].var, paramsB[n].value))

                        else:
                            print("write_probin.py: invalid datatype for variable "+paramsB[n].var)

                        n += 1

                else:
                    fout.write("\n")
                    

            elif (keyword == "namelist"):
                                       
                # namelist
                n = 0
                while (n < len(params)):

                    fout.write("%snamelist /%s/ %s\n" % 
                               (indent, namelistName, params[n].var))

                    n += 1


                if (len(params) == 0):
                    fout.write("%snamelist /%s/ a_dummy_var\n" %
                               (indent, namelistName))

            elif (keyword == "defaults"):

                # defaults
                n = 0
                while (n < len(params)):

                    fout.write("%s%s = %s\n" % 
                               (indent, params[n].var, params[n].value))

                    n += 1


            elif (keyword == "commandline"):

                n = 0
                while (n < len(params)):

                    fout.write("%scase (\'--%s\')\n" % (indent, params[n].var))
                    fout.write("%s   farg = farg + 1\n" % (indent))

                    if (params[n].type == "character"):
                        fout.write("%s   call get_command_argument(farg, value = %s)\n\n" % 
                                   (indent, params[n].var))

                    else:
                        fout.write("%s   call get_command_argument(farg, value = fname)\n" % 
                                   (indent))
                        fout.write("%s   read(fname, *) %s\n\n" % 
                                   (indent, params[n].var))
                        
                    n += 1
                                   


            #else:
                

        else:
            fout.write(line)


    
    print(" ")
    fout.close()




if __name__ == "__main__":

    try: opts, next = getopt.getopt(sys.argv[1:], "t:o:n:", ["pa=","pb="])

    except getopt.GetoptError:
        print("write_probin.py: invalid calling sequence")
        sys.exit(2)

    probinTemplate = ""
    outFile = ""
    namelistName = ""
    paramAFilesStr = ""
    paramBFilesStr = ""

    for o, a in opts:

        if o == "-t":
            probinTemplate = a

        if o == "-o":
            outFile = a

        if o == "-n":
            namelistName = a

        if o == "--pa":
            paramAFilesStr = a

        if o == "--pb":
            paramBFilesStr = a


    if (probinTemplate == "" or outFile == "" or namelistName == ""):
        print("write_probin.py: ERROR: invalid calling sequence")
        sys.exit(2)

    paramAFiles = paramAFilesStr.split()
    paramBFiles = paramBFilesStr.split()

    write_probin(probinTemplate, paramAFiles, paramBFiles, 
                 namelistName, outFile)



