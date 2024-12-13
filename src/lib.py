from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

entity_code_to_label_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX wd: <http://www.wikidata.org/entity/> 
SELECT  *
WHERE {{
        wd:{entity_code} rdfs:label ?label .
        FILTER (langMatches( lang(?label), "EN" ) )
      }}
LIMIT 1
"""

label_to_entity_code_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX wd: <http://www.wikidata.org/entity/> 
SELECT  ?qid
WHERE {{
        ?wd rdfs:label "{label}"@en .
        BIND(STRAFTER(STR(?wd), STR(wd:)) AS ?qid) .
      }}
LIMIT 1
"""

direct_descendents_query = """
SELECT ?qid ?valueLabel ?propLabel  WHERE {{
  VALUES ?item {{
    wd:{entity_code}
  }}
  ?item ?a ?value.
  # remove wikimedia items
  MINUS {{
    ?item wdt:P31 wd:Q4167836
  }}
  MINUS {{
    ?item wdt:P31 wd:Q26884324
  }}
  MINUS {{
    ?item wdt:P31 wd:Q4167410 # wikimedia disambiguation page
  }}
  BIND(STRAFTER(STR(?value), STR(wd:)) AS ?qid) .
  ?prop wikibase:directClaim ?a.
  MINUS {{
    ?prop wikibase:propertyType wikibase:ExternalId. 
  }}
  
  FILTER (?prop != wd:P1424) # topic's main template
  FILTER (?prop != wd:P1482) # stack exchange tag
  FILTER (?prop != wd:P1855) # wikidata property example
  FILTER (?prop != wd:P5008) # on focus list of wikimedia project 
  FILTER (?prop != wd:P6104) # maintained by wikiproject
  FILTER (?prop != wd:P1963) # properties for this type
  FILTER (?prop != wd:P2559) # wikidata usage instructions 
  FILTER (?prop != wd:P373) # commons category 
  FILTER (?prop != wd:P1472) # commons creator page
  FILTER (?prop != wd:P1612) # commons institution template
  FILTER (?prop != wd:P3722) # commons maps category
  FILTER (?prop != wd:P910) # topic's main category
  FILTER (?prop != wd:P301) # category's main topic
  FILTER (?prop != wd:P5125) # category's main topic
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
  }}
"""


def query_wd(query):
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()
    except EndPointInternalError as e:
        raise RuntimeError("SPARQL endpoint returned an internal error.") from e
    except Exception as e:
        raise RuntimeError("Failed to query SPARQL endpoint.") from e


def verify_label(label):
    try:
        return get_entity_code(label)
    except IndexError:
        return None


def verify_entity_code(entity_code):
    try:
        return get_label(entity_code)
    except IndexError:
        return None


def get_label(entity_code):
    try:
        result = query_wd(entity_code_to_label_query.format(entity_code=entity_code))
        if result["results"]["bindings"] != []:
            return result["results"]["bindings"][0]["label"]["value"]
        else:
            return None
    except IndexError as e:
        raise e


def get_entity_code(label):
    result = query_wd(label_to_entity_code_query.format(label=label))
    try:
        return result["results"]["bindings"][0]["qid"]["value"]
    except IndexError as e:
        raise e


def get_direct_descendents(identifier, by_label=False) -> dict:
    if by_label:
        entity_code = get_entity_code(identifier)
    else:
        entity_code = identifier

    result = query_wd(direct_descendents_query.format(entity_code=entity_code))

    children = {}
    columns = result["head"]["vars"]
    for idx, binding in enumerate(result["results"]["bindings"]):
        children[idx] = {
            "qid": binding[columns[0]]["value"],
            "value": binding[columns[1]]["value"],
            "property": binding[columns[2]]["value"],
        }
    return children
