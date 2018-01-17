import re, struct
import EventFilters as Evt
import deserialize as Des

formats = {'char': 'c', 'signed char' : 'b', 'unsigned char': 'B',
           'bool': '?', 'short': 'h', 'unsigned short' : 'H', 'int': 'i',
           'unsigned int': 'I', 'long': 'q', 'unsigned long': 'L',
           'long long': 'q', 'unsigned long long': 'Q', 'float': 'f',
           'double': 'd', 'string': 's', 'byte': 'x'}

class InputStream:

    def __init__(self, data):
        self.data = data
        self.index = 0

    def readBool(self):
        retval = bool(self.data[self.index])
        self.index += 1
        return retval

    def readString(self):
        size = ord(self.data[self.index])
        self.index += 1

        retval = self.data[self.index:self.index+size]
        self.index += size
        return retval


def checkedTypeCode(typecode):
    for variable in typecode:
        if not variable.variableType in formats.keys():
            raise Exception('Incorrect type of variable')


def checkedFields(filters, typecode):
    if not DataDissector(filters, typecode).checkedFields():
        raise Exception("Data don't match with typecode")
        # raise Exception("This topic doesn't accept data with typecode" +
        #                                 "of topic")

def validateTypeCodeAndFilter(filtersData, typecode):
    pass
    # checkedTypeCode(typecode)
    # checkedFields(filtersData, typecode)

def validateExpressions(filters):

    for filter_ in filters:
        if not(re.match("[xyz]", filter_.split()[0]) and
               re.match("(==|in|<|>)", filter_.split()[1])):
            throwFilterException()

        # checked values
        else:
            operator = filter_.split()[1]
            if ((operator=="in") and
                (len(filter_.split()[2].split(","))==2)):

                valueLow = filter_.split()[2].split(",")[0].split("(")[1]
                valueHigh = filter_.split()[2].split(",")[1][:-1]

                if not(re.match("[-]?\d+", valueLow) and
                       re.match("[-]?\d+", valueHigh)):
                    throwFilterException()

            else:
                if not(re.match("[-]?\d+", filter_.split()[2])):
                    throwFilterException()


def throwFilterException():
    raise Exception('Invalid expression for filter\n'+
                    '-----> Correct expresion : variableName + ' +
                    'operator + values\n'+
                    '-----> Example: "x == 2"\n'+
                    '-----> Possible Variables: x, y\n'+
                    '-----> Possible Operators: ==, <, >, in range( , )')



def getFilter(topicFilter):
    # Checked if there is two variables: variable + operator
    # Checked if filter is = , <, > or between
    # Checked if the variables are x or y

    filters = []
    for filterDef in topicFilter:
        variableName = filterDef.split()[0]
        operator = filterDef.split()[1]
        if operator == "in":
            valueLow = filterDef.split()[2].split(",")[0].split("(")[1]
            valueHigh = filterDef.split()[2].split(",")[1][:-1]
            filters.append(Evt.EventFilterRange(variableName,
                                                int(valueLow),
                                                int(valueHigh)))
        else:
            value = filterDef.split()[2]
            if operator == '==':
                filters.append(Evt.EventFilter(variableName, int(value)))

            if operator == '<':
                filters.append(Evt.EventFilterBelow(variableName,
                                                    int(value)))

            if operator == '>':
                filters.append(Evt.EventFilterOver(variableName,
                                                   int(value)))

    return filters


class DataDissector:
    def __init__(self, filterSeq, typecode):
        self.methodName = ''
        self.filterSeq = filterSeq
        self.typecode = typecode
        self.fmt = ''
        self.get_format()

    def setMethodName(self, name):
        self.methodName = name

    def getMethodName(self):
        return self.methodName

    def checkedFields(self):
        names = [x.variableName for x in self.typecode]
        checked = True
        for filter_ in self.filterSeq:
            # checked = checked and filter_.field_name in names
            checked = checked and filter_.split()[0] in names

        return checked

    def checkedFields_with_filter_classes(self):
        names = [x.variableName for x in self.typecode]
        checked = True
        for filter_ in self.filterSeq:
                checked = checked and filter_.field_name in names
        return checked

    def get_format(self):
        for tupla in self.typecode:
            if tupla.variableType.split()[0] == "sequence":
                variableType = tupla.variableType.split()[2]
                variableType = variableType.replace("{", "")
                variableType = variableType.replace("}", "")

                variableTypeList = variableType.split(",")

                for index in range(int(tupla.variableType.split()[1])):
                    for i in range(len(variableTypeList)):
                        self.fmt += formats[variableTypeList[i]]

            else:
                self.fmt = self.fmt + formats[tupla.variableType]


    def get_field(self, data):
        names = [x.variableName for x in self.typecode]
        return struct.unpack(self.fmt, data)
        # index = names.index(filter_.field_name)
        # try:
        #         return struct.unpack(self.fmt, data)[index]
        # except struct.error:
        #         raise ValueError('Data unexpected')


    def dissector_match(self, data):
        names = [x.variableName for x in self.typecode]
        matched = True

        dt = Des.deserialize(data, self.fmt)

        for filter_ in self.filterSeq:
            filteraux = filter_
            for name in names:
                if (name in filter_):
                    index = names.index(name)
                    if self.typecode[index].variableType == "string":
                        if filteraux[0] == "(":
                            filterlist = filteraux[1:].split()
                            filterlist.insert(0, "(")
                        else:
                            filterlist = filteraux.split()
                        for f in filterlist:
                            if f == name:
                                filterlist[filterlist.index(f)] = "'" \
                                    + dt[index] + "'"

                        filteraux = " ".join(filterlist)

                    else:
                        filteraux = filteraux.replace(name, str(dt[index]))

            matched = matched and eval(filteraux)

        return matched

    # def dissector_match_with_filter_classes(self, data):
    #     if not self.filterSeq:
    #         return True

    #     names = [x.variableName for x in self.typecode]
    #     matched = False

    #     for filter_ in self.filterSeq:
    #         index = names.index(filter_.field_name)
    #         try:
    #             value = struct.unpack(self.fmt, data)[index]
    #         except struct.error:
    #             raise ValueError('Data unexpected')

    #         matched = matched or filter_.match(value)

    #     return matched

    def dissector_match_with_filter_classes(self, data):

        if not self.filterSeq:
            return True

        names = [x.variableName for x in self.typecode]
        matched = False

        filtersPerVariables = [[] for i in range(len(names))]

        for filter_ in self.filterSeq:
            index = names.index(filter_.field_name)
            filtersPerVariables[index].append(filter_)


        for filters in filtersPerVariables:
            if filters:
                matched = False

            for filter_ in filters:
                index = names.index(filter_.field_name)
                try:
                    value = struct.unpack(self.fmt, data)[index]
                except struct.error:
                    raise ValueError('Data unexpected')

                matched = matched or filter_.match(value)

        return matched
