import hashlib
import dns.resolver

sml_server = 'edelivery.tech.ec.europa.eu'
#sml_server = 'acc.edelivery.tech.ec.europa.eu' # test

# SML: receiver -> domain (DNS)

def get_domain_using_http(receiver):
    smp_id = 'B-' + hashlib.md5((receiver.lower()).encode("utf-8")).hexdigest()
    return smp_id + '.iso6523-actorid-upis.' + sml_server

def get_domain_using_sml(receiver):
    smp_id = 'B-' + hashlib.md5((receiver.lower()).encode("utf-8")).hexdigest()
    name = smp_id + '.iso6523-actorid-upis.' + sml_server
    answers = dns.resolver.resolve(name, 'CNAME')
    domain = str(answers[0])
    if domain[-1] == '.':
        return domain[0:-1]
    else:
        return domain
