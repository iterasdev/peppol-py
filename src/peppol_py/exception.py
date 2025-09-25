class SendPeppolError(Exception):
    pass


def make_sendpeppol_error(output, code, temporary=False, **kwargs):
    e = SendPeppolError(output)
    e.code = code
    e.temporary = temporary
    for k, v in kwargs.items():
        setattr(e, k, v)
    return e
