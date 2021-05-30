# from utility.dataTypes import Filter, Print, Expression
from .dataTypes import Print, Expression, Filter

Objects = []
prevAssignWord = ""
Content = []
resultWordList = []
fieldsFilter = []
valuesFilter = []
termsExpression = []
assignedExpression = 0
words = []
destinations = []

sort_dict = {
    "PARAMETER": [],
    "SORTVALUE": []
}


def find_word_list(node):
    global resultWordList
    for element in node.nodeList:
        if element.name == "WORD":
            resultWordList.append(element.value)
            words.append(element.value)
        elif element.name == "wordlist":
            find_word_list(element)
        else:
            return resultWordList


def find_destination_list(node):
    global destinations
    for element in node.nodeList:
        if element.name in "WORD EMAIL STAR":
            destinations.append(element.value)
        elif element.name == "destinationvalue":
            find_destination_list(element)
        else:
            return destinations


def find_sort_values(node):
    for element in node.nodeList:
        if element.name in "SORTBY":
            continue
        else:
            sort_dict[element.name] = element.value


def find_filter(node):
    global fieldsFilter
    global valuesFilter
    global words
    for element in node.nodeList:
        if element.name == "LEFTBRACE" or element.name == "RIGHTBRACE":
            continue
        elif element.name in "SORTBY":
            fieldsFilter.append(element.value)
            find_sort_values(node)
            valuesFilter.append(sort_dict.copy())
            sort_dict.clear()
        elif element.name in "TO FROM CC FORWARDED READ BODY ATTACHMENTS TIME SUBJECT SORTBY FOLDER":
            fieldsFilter.append(element.value)
        elif element.name in "wordlist":
            find_word_list(element)
            valuesFilter.append(words.copy())
            words.clear()
        elif element.name in "destinationvalue":
            find_destination_list(element)
            valuesFilter.append(destinations.copy())
            destinations.clear()
        elif element.name in "WORD BOOLVALUE DATE DATESTRING INTERVAL DAY YEAR DATE EMAIL INT STAR STRING":
            valuesFilter.append(element.value)
        elif element.name in "filter queryvalue attachementsvalue textvalue assignvalue datevalue ":
            find_filter(element)
        else:
            return fieldsFilter


def find_expression_elements(node):
    global termsExpression
    for element in node.nodeList:
        if element.name == "WORD" or element.name == "OPERAND":
            termsExpression.append(element.value)
        elif element.name == "expressionterm" \
                or element.name == "expression2":
            find_expression_elements(element)
        else:
            return termsExpression


def traverse(node):
    global prevAssignWord
    global resultWordList
    if hasattr(node, 'nodeList'):
        elements = node.nodeList

        if node.name == "print":
            for el in elements:
                if el.name == "wordlist":
                    resultWordList.clear()
                    find_word_list(el)
                    break
            new_print = Print(resultWordList.copy())
            Objects.append(new_print)

        if node.name == "expression":
            termsExpression.clear()
            find_expression_elements(node)
            new_expression = Expression(prevAssignWord, termsExpression)
            Objects.append(new_expression)

        if node.name == "query":
            fieldsFilter.clear()
            valuesFilter.clear()
            find_filter(node)
            filter_values = dict(zip(fieldsFilter, valuesFilter))
            new_filter = Filter(prevAssignWord, filter_values.copy())
            filter_values.clear()
            Objects.append(new_filter)

        elif node.name == "assignment":
            for el in elements:
                if el.name == "WORD":
                    prevAssignWord = el.value

        for el in elements:
            traverse(el)

        return Objects
