class EventFilter(object):
    def __init__(self, name, num):
        self.field_name = name
        self.num = num

    def match(self, value):
        return value == self.num

    def equal(self, filter_):
        return ((type(filter_)==type(self))
                and (filter_.field_name == self.field_name)
                and (filter_.num == self.num))


class EventFilterRange(object):
    def __init__(self, name, n, m):
        self.field_name = name
        self.valueLow = n
        self.valueHigh = m

    def match(self, low, high=None):
        if high:
            return ((low in range(self.valueLow, self.valueHigh))
                    and (high in range(self.valueLow, self.valueHigh))
                    and (low >= self.valueLow) and (high<= self.valueHigh)
                    and (low < high))
        else:
            return (low >= self.valueLow) and (low < self.valueHigh)

    def equal(self, filter_):
        return ((type(filter_)==type(self))
                and (filter_.field_name == self.field_name)
                and (filter_.valueLow == self.valueLow)
                and (filter_.valueHigh == self.valueHigh))


class EventFilterBelow(object):
    def __init__(self, name, num):
        self.field_name = name
        self.num = num

    def match(self, value):
        return not(value >= self.num)

    def equal(self, filter_):
        return ((type(filter_)==type(self))
                and (filter_.field_name == self.field_name)
                and (filter_.num == self.num))

class EventFilterOver(object):
    def __init__(self, name, num):
        self.field_name = name
        self.num = num

    def match(self, value):
        return not(value <= self.num)

    def equal(self, filter_):
        return ((type(filter_)==type(self))
                and (filter_.field_name == self.field_name)
                and (filter_.num == self.num))
