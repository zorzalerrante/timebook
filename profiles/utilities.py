import unicodedata

def remove_accents(string):
    nkfd_form = unicodedata.normalize('NFKD', unicode(string))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])