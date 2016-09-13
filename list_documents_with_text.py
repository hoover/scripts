from django.conf import settings
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(settings.SNOOP_ELASTICSEARCH_URL)

results = helpers.scan(
    es,
    index=settings.SNOOP_ELASTICSEARCH_INDEX,
    query={
        'query': {
            'bool': {
                'must': [
                    {'exists': {
                        'field': 'text',
                    }},
                ],
            },
        },
    },
    size=1000,
)

with open('../notes/with_text.tsv', 'w', encoding='utf-8') as f:
    for doc in results:
        print(doc['_id'], file=f)
