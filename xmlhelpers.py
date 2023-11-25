from uuid import uuid4

from constants import WSU_NS

def ns(namespace, tagname):
    return '{%s}%s' % (namespace, tagname)

ID_ATTR = ns(WSU_NS, 'Id')

# FIXME: allow one to pass in id
def get_unique_id():
    return 'id-{0}'.format(uuid4())

def ensure_id(node):
    id_val = node.get(ID_ATTR)
    if not id_val:
        id_val = get_unique_id()
        node.set(ID_ATTR, id_val)
    return id_val
