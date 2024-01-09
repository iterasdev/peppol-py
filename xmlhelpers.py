from lxml.builder import ElementMaker

def get_element_maker(nsmap):
    def ns(shorthand, tag):
        return "{%s}%s" % (nsmap[shorthand], tag)

    return ElementMaker(nsmap=nsmap), ns
