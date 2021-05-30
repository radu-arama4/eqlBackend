import datetime
import sys

from .grammar.tokenDictionary import tokenTypes

def stringProcess(i, sourceCodeChars):
    temp = sourceCodeChars[i:]
    string = ""
    for index, char in enumerate(temp):
        if char == "\"":
            break
        string += char
    return string


def intProcess(i, sourceCodeChars):
    temp = sourceCodeChars[i:]
    string = ""
    type = "INT"
    for char in temp:
        if char.isnumeric() or char in "-.dy*":
            string += char
        else:
            break

    if string.__contains__("-") and not string.__contains__("*"):
        try:
            datetime.datetime.strptime(string, '%d-%m-%Y')
            type = "DATE"
        except ValueError:
            print('\033[93m'+"Incorrect date or date format, should be DD-MM-YYYY")
            sys.exit(1)

    if string.__contains__("y"):
        type = "YEAR"

    if string.__contains__("d"):
        type = "DAY"

    if string.__contains__("*"):
        type = "DATESTRING"

    if string.__contains__(".."):
        type = "INTERVAL"

    return type, string


def alphaProcess(i, sourceCodeChars):

    temp = sourceCodeChars[i:]
    type = "WORD"
    string = ""
    for index, char in enumerate(temp):

        if char in " {}()+\n" or (char == ":" and not tokenTypes.get(string + ":")):
            break

        if char not in "\n\t":
            string += char

        if (tokenTypes.get(string.lower()) and temp[index + 1] != ":") or \
                tokenTypes.get(string.lower()) and temp[index + 1] == "(":
            type = tokenTypes[string.lower()]
            break

    if string.__contains__("@"):
        type = "EMAIL"

    return type, string

def lexer(sourcecode):
    tokenList = list()

    # sourceCodeChars = open_file(sourcecode)
    sourceCodeChars = sourcecode

    i = 0

    while i < len(sourceCodeChars):
        char = sourceCodeChars[i]
        if char == "*" and (not sourceCodeChars[i + 1].isnumeric() and sourceCodeChars[i + 1] not in 'dy'):
            tokenList.append(("STAR", char))
            i += 1
        elif char in " \n\t\r":
            i += 1
        elif tokenTypes.get(char):
            tokenList.append((tokenTypes.get(char), char))
            i += 1
        elif char == "\"":
            char = stringProcess(i + 1, sourceCodeChars)
            tokenList.append(("STRING", char))
            i += len(char) + 2
        elif char.isnumeric() or (char == "*" and (sourceCodeChars[i + 1].isnumeric() or sourceCodeChars[i + 1] in 'dy')):
            type, char = intProcess(i, sourceCodeChars)
            tokenList.append((type, char))
            i += len(char)
            continue
        elif char.isalpha():
            type, char = alphaProcess(i, sourceCodeChars)
            tokenList.append((type, char))
            i += len(char)

    return tokenList
