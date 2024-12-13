import concurrent.futures
import random
import time
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
from grapher import Grapher, BlockTransformer


def _graph(entity_code):
    try:
        start = time.time()
        graph = BlockTransformer(entity_code)
        root_entity_code = graph.randomize_graph()
        graph.export()
        end = time.time()
        print(f"Graph exported successfully! Time taken: {end - start:.2f} seconds")
    except Exception as e:
        image_path = Path.cwd() / "output" / "images" / f"{root_entity_code}.png"
        Path.unlink(image_path, missing_ok=True)
        print(f"Failed to generate graph for {entity_code}: {e}")


def fetch_random_entity_codes(sparql_query, limit=50):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
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

org_query_with_offset = """
SELECT ?entity
WHERE {{
  ?entity wdt:P31 wd:Q43229.  # Instances of organizations
}}
LIMIT {limit}
OFFSET {offset}
"""

planet_query_with_offset = """
SELECT ?entity
WHERE {{
  ?entity wdt:P31 wd:Q634.  # Instances of planets
}}
LIMIT {limit}
OFFSET {offset}
"""

animal_query_with_offset = """
SELECT ?entity
WHERE {{
  ?entity wdt:P31 wd:Q16521.  # Instances of animals
}}
LIMIT {limit}
OFFSET {offset}        
"""

human_entity_codes = fetch_random_entity_codes(human_query_with_offset, limit=100)
org_entity_codes = fetch_random_entity_codes(org_query_with_offset, limit=100)
planet_entity_codes = fetch_random_entity_codes(planet_query_with_offset, limit=100)
animal_entity_codes = fetch_random_entity_codes(animal_query_with_offset, limit=100)


# Parallel execution with ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(_graph, human_entity_codes)
    executor.map(_graph, org_entity_codes)
    executor.map(_graph, human_entity_codes)
    executor.map(_graph, animal_entity_codes)
