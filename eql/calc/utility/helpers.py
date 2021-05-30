# from utility.dataTypes import NonTerminalNode,Filter,Print,Expression

from .dataTypes import NonTerminalNode, Filter, Print, Expression

def open_file(path):
    sourceCode = open(path, "r")
    data = sourceCode.read()
    sourceCode.close()
    return data

def stringTree(node, level):
    res = ""
    if not isinstance(node, NonTerminalNode):
        return "\t" * level + str(node) + "\n"
    if node.nodeList[0].name == "@":
        return ""

    for child in node.nodeList:
        res = "\t" * level + str(node) + "\n"
        for child in node.nodeList:
            res += stringTree(child, level + 1)
        return res

def printStatements(statements):
    for statement in statements:
        if (isinstance(statement, Filter)):
            print("Filter")
            print("\t Identifier:",statement.name)
            print("\t Rules:",statement.values)
        elif (isinstance(statement, Expression)):
            print("Expression")
            print("\t Identifier:",statement.assigned)
            print("\t Terms:",statement.terms)
        elif (isinstance(statement, Print)):
            print("Print")
            print("\t Identifier(s) to print",statement.words)