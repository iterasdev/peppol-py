from uuid import uuid4

from constants import WSU_NS

def ns(namespace, tagname):
    return '{%s}%s' % (namespace, tagname)

ID_ATTR = ns(WSU_NS, 'Id')

def get_unique_id(id_type=None):
    if id_type:
        return '{}-{}'.format(id_type, uuid4())
    else:
        return '_{}'.format(uuid4())

def ensure_id(node, id_type=None):
    id_val = node.get(ID_ATTR)
    if not id_val:
        id_val = get_unique_id(id_type)
        node.set(ID_ATTR, id_val)
    return id_val
