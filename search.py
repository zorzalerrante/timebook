import settings
from whoosh.qparser import QueryParser
from whoosh.index import open_dir

def perform_search(query, limit=None, include_surrogates=False):
    ix = open_dir(settings.WHOOSH_INDEX_DIR)

    results = []
    
    if not limit:
        limit = 10
    
    with ix.searcher() as searcher:
        query = QueryParser("description", ix.schema).parse(unicode(query))
        print query
        hits = searcher.search(query, limit=limit)
        for h in hits:
            try:
                avatar = h['avatar']
            except KeyError:
                avatar = ''
                
            fields = {'id': h['id'], 'name': h['title'], 'uri': '', 'type': h['type'], 'score': h['score'], 'avatar': avatar, 'job_title': 'Function @ Industry'}
            if include_surrogates:
                fields['surrogate'] = h.highlights('description')
            results.append(fields)

    return results


if __name__ == '__main__':
    import sys

    results = perform_search(sys.argv[1] + '*')
    for r in results:
        print r

            
