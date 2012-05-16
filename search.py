import settings
from whoosh.qparser import QueryParser
from whoosh.index import open_dir

def perform_search(query):
    ix = open_dir(settings.WHOOSH_INDEX_DIR)

    results = []
    
    with ix.searcher() as searcher:
        query = QueryParser("names", ix.schema).parse(unicode(query))
        print query
        hits = searcher.search(query)
        for h in hits:
            results.append(h.fields())

    return results


if __name__ == '__main__':
    import sys

    results = perform_search(sys.argv[1] + '*')
    for r in results:
        print r

            
