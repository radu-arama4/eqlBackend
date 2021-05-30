import datetime
import json
from pathlib import Path
from pprint import pprint

from .dataTypes import Filter, Expression, Print

emailDataBase = Path("calc/utility/emailsdb.json").read_text()
filterDataBase = Path("calc/utility/filtersdb.json").read_text()
emails = json.loads(emailDataBase)
filters = json.loads(filterDataBase)


def get_filters():
    return filters


def delete_filter(filter_name):
    filters.pop(filter_name, None)
    Path("calc/utility/filtersdb.json").write_text(json.dumps(filters))


def processStrFields(emailField, field, filter):
    ismatch = False

    fieldvalue = filter[field]

    if fieldvalue[0] == "*":
        return True

    if isinstance(fieldvalue, list):
        flag = False
        for word in fieldvalue:
            flag |= word in emailField or word == emailField
        ismatch |= flag
    else:
        ismatch = fieldvalue in emailField or fieldvalue == emailField

    return ismatch


def processAttachments(emailField, filterValue):
    attachmentsCount = len(emailField)

    ismatch = False

    if isinstance(filterValue, list):
        flag = False

        for word in filterValue:
            for attachment in emailField:
                flag |= word in attachment
        ismatch |= flag
        return ismatch

    if filterValue in "yes no":
        if filterValue == "yes" and attachmentsCount != 0:
            return True
        elif filterValue == "no" and attachmentsCount == 0:
            return True
    elif filterValue.__contains__(".."):
        filterValue = filterValue.split("..")
        if int(filterValue[0]) <= attachmentsCount <= int(filterValue[1]):
            return True
    elif filterValue.isnumeric():
        if int(filterValue) == attachmentsCount:
            return True
    elif filterValue.isalpha():
        pass

    return False


def processSingleStr(emailField, filterValue):
    if emailField == "true" and filterValue.lower() == "yes":
        return True
    elif emailField == "false" and filterValue.lower() == "no":
        return True
    elif filterValue.lower() not in "yes no":
        if emailField == filterValue:
            return True
    return False


def get_date_from_string_dy(stringdate, day=False, year=False):
    date_now = datetime.datetime.now()

    if day:
        days = stringdate.replace("d", "")
        date = date_now - datetime.timedelta(days=int(days))

    elif year:
        years = stringdate.replace("y", "")
        date = date_now - datetime.timedelta(days=int(years) * 365)

    return date


def process_date_with_star(emailDate, filterValue):
    dates = filterValue.split("*")

    if dates.__contains__(""):

        starIndex = dates.index("")
        if starIndex == 0:

            lower = datetime.datetime.min
            if "d" in dates[1]:
                upper = get_date_from_string_dy(dates[1], day=True)
            elif "y" in dates[1]:
                upper = get_date_from_string_dy(dates[1], year=True)
            else:
                upper = datetime.datetime.strptime(dates[1], '%d-%m-%Y')
        elif starIndex == 1:

            upper = datetime.datetime.max
            if "d" in dates[0]:
                lower = get_date_from_string_dy(dates[0], day=True)
            elif "y" in dates[0]:
                lower = get_date_from_string_dy(dates[0], year=True)
            else:
                lower = datetime.datetime.strptime(dates[0], '%d-%m-%Y')

    else:
        lower = datetime.datetime.strptime(dates[0], '%d-%m-%Y')
        upper = datetime.datetime.strptime(dates[1], '%d-%m-%Y')

    if lower <= emailDate <= upper:
        return True


def process_date_with_dy(emailDate, filterValue):
    if "d" in filterValue:
        date = get_date_from_string_dy(filterValue, day=True)
        if date.date() == emailDate.date():
            return True

    elif "y" in filterValue:
        date = get_date_from_string_dy(filterValue, year=True)
        if date.year == emailDate.year:
            return True


def processTime(emailField, filterValue):
    emailDate = datetime.datetime.strptime(emailField, '%Y-%m-%dT%H:%M:%S.%fZ')

    if filterValue.__contains__("*"):
        return process_date_with_star(emailDate, filterValue)

    elif "d" or "y" in filterValue and "*" not in filterValue:
        return process_date_with_dy(emailDate, filterValue)

    elif datetime.datetime.strptime(filterValue, '%d-%m-%Y').date() == emailDate.date():
        return True


def filterEmails(filter):
    res = list()

    print(filter)

    for email in emails:
        ismatch = False
        for field in filter:
            temp = field.replace(":", "")

            if field in "to: from: cc: subject:":
                if email["header"][temp] == "":
                    ismatch = False
                    break
                ismatch = processStrFields(email["header"][temp], field, filter)

            elif field in "body:":
                ismatch = processStrFields(email["body"]["content"], field, filter)
            elif field in "attachments:":
                ismatch = processAttachments(email["body"]["attachments"], filter[field])
            elif field in "read: forwarded: folder:":
                ismatch = processSingleStr(email["metadata"][temp], filter[field])
            elif field in "time:":
                ismatch = processTime(email["metadata"]["date"], filter[field])

            if not ismatch:
                break

        if ismatch:
            res.append(email)

    return res


def applyFilter(filter):
    res = list()

    if ("to:" in filter) and ("from:" in filter):
        raise ValueError("Filter could contain only to or only from rules!")
    else:
        res.extend(filterEmails(filter))
        print(res)

    return res


def add_dict(d1, d2):
    d = {}
    for key in set(list(d1.keys()) + list(d2.keys())):
        d.setdefault(key, [])
        try:
            first = d1[key]
        except KeyError:
            d[key] = d2[key]
            continue

        try:
            second = d2[key]
        except KeyError:
            d[key] = d1[key]
            continue

        if key in "read: attachments: forwarded:":
            if first == 'yes' or second == 'yes':
                d[key] = 'yes'
            else:
                d[key] = 'no'
        elif key in "folder: subject: time:":
            if isinstance(d1[key], list):
                words = d1[key]
                words.append(d2[key])
            elif isinstance(d2[key], list):
                words = d2[key]
                words.append(d1[key])
            else:
                words = [d1[key], d2[key]]
            d[key] = words
        else:
            d[key] = first + second

    return d


def div_dict(d1, d2):
    d = d1.copy()
    return d


def check_term(term):
    for element in filters:
        if element == term:
            return True
    return False


def interpretCode(statements):
    res = list()
    for statement in statements:
        if isinstance(statement, Filter):
            filters[statement.name] = statement.values  # example of adding Filter object to dictionary filters
        elif isinstance(statement, Expression):

            # pprint(filters)
            terms = statement.terms

            i = 1
            prev = filters[terms[0]]
            while i < len(terms) - 1:
                if not check_term(terms[i + 1]):
                    print("Not existing element")
                    return
                if terms[i] == '+':
                    prev = add_dict(prev, filters[terms[i + 1]])
                elif terms[i] == '-':
                    print("-")
                    prev = div_dict(prev, filters[terms[i + 1]])
                    # prev = divide
                i = i + 2

            pprint(prev)

            # prev - resulting filter

            # print(filters[statement.terms[0]])
            # expression processing -> procesExpr()

            # input -> expression (statement)

            # output - > Filter object
            # + add new filter to filters dictionary filters[newfiltername] = output.values

            pass
        elif isinstance(statement, Print):
            for filter in statement.words:
                res.extend(applyFilter(filters[filter]))

    return res


Path("calc/utility/filtersdb.json").write_text(json.dumps(filters))
