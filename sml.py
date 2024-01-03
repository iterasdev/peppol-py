import hashlib

# SML: receiver -> domain (DNS)

def get_domain_using_http(receiver, test):
    smp_id = 'B-' + hashlib.md5((receiver.lower()).encode("utf-8")).hexdigest()
    return f'{smp_id}.iso6523-actorid-upis.{get_server(test)}'

def get_server(test):
    if test:
        return 'acc.edelivery.tech.ec.europa.eu'
    else:
        return 'edelivery.tech.ec.europa.eu'
