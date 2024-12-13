import random
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from grapher import Grapher, BlockTransformer


def _graph(entity_code):
    try:
        start = time.time()
        graph = BlockTransformer(entity_code)
        graph.randomize_graph()
        graph.export()
        end = time.time()
        print(f"Graph exported successfully! Time taken: {end - start:.2f} seconds")
    except Exception as e:
        print(f"Error generating graph: {e}")


def fetch_random_entity_codes(sparql_query, limit=50):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    # Generate a random offset for retrieval
    offset = random.randint(0, 1000)  # Adjust the range as needed
    sparql_query = sparql_query.replace("{offset}", str(offset))  # Insert random offset
    sparql.setQuery(sparql_query.format(limit=limit))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    entity_codes = []
    for result in results["results"]["bindings"]:
        entity_url = result["entity"]["value"]
        entity_code = entity_url.split("/")[-1]
        entity_codes.append(entity_code)

    return entity_codes


human_query_with_offset = """
SELECT ?entity
WHERE {{
  ?entity wdt:P31 wd:Q5.  # Instances of humans
}}
LIMIT {limit}
OFFSET {offset}
"""

entity_codes = fetch_random_entity_codes(human_query_with_offset, limit=10)

for entity_code in entity_codes:
    _graph(entity_code)
