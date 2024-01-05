from lxml.builder import ElementMaker

# FIXME: remove
def ns(namespace, tagname):
    return '{%s}%s' % (namespace, tagname)

def get_element_maker(nsmap):
    def ns(shorthand, tag):
        return "{%s}%s" % (nsmap[shorthand], tag)

    return ElementMaker(nsmap=nsmap), ns
