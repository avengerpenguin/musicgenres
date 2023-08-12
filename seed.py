import json
import urllib.error

import yaml
from typing import Generator, Iterator, Set
from pyld import jsonld
import graphviz
import rdflib
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, JSON, XML, N3, RDF
import pathlib
from laconia import ThingFactory
from rdflib import URIRef
from pelican.utils import slugify


def make_graph() -> rdflib.Graph:
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(
        f"""
    PREFIX ap: <http://avengerpenguin.com/vocab#>
    PREFIX wikidata: <http://www.wikidata.org/entity/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    CONSTRUCT {{
        ?g1 ap:influences ?g2 .
        ?g1 rdfs:label ?l1 .
        ?g2 rdfs:label ?l2 .
        ?g1 rdfs:comment ?c1 .
        ?g2 rdfs:comment ?c2 .
    }} WHERE {{
        {{?g1 rdf:type wikidata:Q188451 . ?g2 rdf:type wikidata:Q188451 . ?g1 dbo:derivative ?g2 . ?g1 rdfs:label ?l1 . ?g2 rdfs:label ?l2 . ?g1 rdfs:comment ?c1 . ?g2 rdfs:comment ?c2 .}}
        UNION
        {{?g1 rdf:type wikidata:Q188451 . ?g2 rdf:type wikidata:Q188451 . ?g1 dbp:derivatives ?g2 . ?g1 rdfs:label ?l1 . ?g2 rdfs:label ?l2 . ?g1 rdfs:comment ?c1 . ?g2 rdfs:comment ?c2 .}}
        UNION
        {{?g1 rdf:type wikidata:Q188451 . ?g2 rdf:type wikidata:Q188451 . ?g2 dbo:stylisticOrigin ?g1 . ?g1 rdfs:label ?l1 . ?g2 rdfs:label ?l2 . ?g1 rdfs:comment ?c1 . ?g2 rdfs:comment ?c2 .}}
        FILTER (langMatches( lang(?l1), "EN" ) &&  langMatches( lang(?l2), "EN" ) && langMatches( lang(?c1), "EN" ) &&  langMatches( lang(?c2), "EN" ))
    }}
    """
    )
    g = sparql.queryAndConvert()
    g.bind('ap', URIRef('http://avengerpenguin.com/vocab#'))
    for s, o in g.subject_objects(predicate=URIRef("http://avengerpenguin.com/vocab#influences")):
        g.add((o, URIRef("http://avengerpenguin.com/vocab#derives"), s))
    with open('genres.ttl', 'w') as f:
        f.write(g.serialize(format='turtle'))
    return g


def item_graphs() -> [rdflib.Graph]:
    visited: Set[str] = set()
    todo: Set[str] = {"http://dbpedia.org/resource/Acid_jazz"}
    rels = frozenset({
        "http://dbpedia.org/ontology/derivative",
        "http://dbpedia.org/property/derivatives",
        "http://dbpedia.org/ontology/stylisticOrigin",
    })

    while todo:
        uri: str = todo.pop()
        print(f"Making: {uri}")
        g = rdflib.Graph(identifier=uri)
        visited.add(uri)
        try:
            g.parse(uri)
        except urllib.error.HTTPError as e:
            continue

        for s, p, o in g:
            if type(o) == rdflib.URIRef and str(p) in rels:
                try:
                    g.parse(str(o))
                    if str(o) not in visited:
                        todo.add(str(o))
                except urllib.error.HTTPError as e:
                    continue

        for s, p, o in g:
            if type(o) == rdflib.Literal and o.language and o.language != 'en':
                g.remove((s, p, o))
                continue

        g.bind('dbo', URIRef('http://dbpedia.org/ontology/'))
        g.bind('dbp', URIRef('http://dbpedia.org/property/'))
        yield g


def make_items():
    g = make_graph()
    for s in set(g.subjects(predicate=URIRef("http://avengerpenguin.com/vocab#influences"))):
        i = ThingFactory(g)(URIRef(str(s)))
        yield g, i
    for s in set(g.subjects(predicate=URIRef("http://avengerpenguin.com/vocab#derives"))):
        i = ThingFactory(g)(URIRef(str(s)))
        yield g, i


if __name__ == "__main__":
    content_dir = pathlib.Path(__file__).parent.absolute() / "Music"
    for graph, item in make_items():
        print(f"Received: {item}")
        if not item.rdfs_label.any():
            continue
        item_path = content_dir / f"{item.rdfs_label.any().replace('/', '-')}.md"
        # if item_path.exists():
        #     pass
        # else:
        #     open(item_path, 'w') as item_file:
        #         item_file.write()
        # frame = {
        #     "@context": {
        #         "_base": "@base",
        #         "_container": "@container",
        #         "_direction": "@direction",
        #         "_graph": "@graph",
        #         "_id": "@id",
        #         "_import": "@import",
        #         "_included": "@included",
        #         "_index": "@index",
        #         "_json": "@json",
        #         "_language": "@language",
        #         "_list": "@list",
        #         "_nest": "@nest",
        #         "_none": "@none",
        #         "_prefix": "@prefix",
        #         "_propagate": "@propagate",
        #         "_protected": "@protected",
        #         "_reverse": "@reverse",
        #         "_set": "@set",
        #         "_type": "@type",
        #         "_value": "@value",
        #         "_version": "@version",
        #         "_vocab": "@vocab",
        #         "owl": str(rdflib.OWL),
        #         "dbr": "http://dbpedia.org/resource/",
        #         "foaf": "http://xmlns.com/foaf/0.1/",
        #         "dbo": "http://dbpedia.org/ontology/",
        #         "dbp": "http://dbpedia.org/property/",
        #         "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        #         "title": {
        #             "@id": "http://www.w3.org/2000/01/rdf-schema#label",
        #             "@language": "en",
        #         }
        #     },
        #     "@id": str(item),
        # }
        # json_ld_string = graph.serialize(format="application/ld+json")
        # framed = jsonld.frame(
        #     json.loads(json_ld_string),
        #     frame,
        #     {"expandContext": frame["@context"]},
        # )
        # print(framed)
        framed = {
            "_id": str(item),
            "title": str(item.rdfs_label.any()),
        }
        with open(item_path, 'w') as f:
            f.write('---\n')
            f.write(yaml.dump(framed))
            f.write('---\n')

            dot = graphviz.Digraph(
                graph_attr={'rankdir': 'LR', "bgcolor": "#F3DDB8"},
                node_attr={"penwidth": "3.0", "color": "#26242F"},
            )
            dot.node(item.rdfs_label.any(), shape="circle")
            for influence in item.ap_derives:
                href = slugify(
                    influence.rdfs_label.any(),
                    regex_subs=[
                        (
                            r"[^\w\s-]",
                            "",
                        ),  # remove non-alphabetical/whitespace/'-' chars
                        (r"(?u)\A\s*", ""),  # strip leading whitespace
                        (r"(?u)\s*\Z", ""),  # strip trailing whitespace
                        (
                            r"[-\s]+",
                            "-",
                        ),  # reduce multiple whitespace or '-' to single '-'
                    ],
                )
                dot.node(influence.rdfs_label.any(), href=f"/{href}/")
                dot.edge(
                    influence.rdfs_label.any(),
                    item.rdfs_label.any(),
                )
            for influenced in item.ap_influences:
                href = slugify(
                    influenced.rdfs_label.any(),
                    regex_subs=[
                        (
                            r"[^\w\s-]",
                            "",
                        ),  # remove non-alphabetical/whitespace/'-' chars
                        (r"(?u)\A\s*", ""),  # strip leading whitespace
                        (r"(?u)\s*\Z", ""),  # strip trailing whitespace
                        (
                            r"[-\s]+",
                            "-",
                        ),  # reduce multiple whitespace or '-' to single '-'
                    ],
                )
                dot.node(influenced.rdfs_label.any(), href=f"/{href}/")
                dot.edge(
                    item.rdfs_label.any(),
                    influenced.rdfs_label.any(),
                )
            f.write('\n```dot\n')
            f.write(dot.source)
            f.write('```\n')
            f.write('\n')
            f.write(item.rdfs_comment.any() or '')
            f.write('\n')
            if item.ap_derives:
                f.write('\n## Influences\n')
                for influence in item.ap_derives:
                    f.write(f"- [[{influence.rdfs_label.any()}]]\n")
            if item.ap_influences:
                f.write('\n## Derivatives\n')
                for influenced in item.ap_influences:
                    f.write(f"- [[{influenced.rdfs_label.any()}]]\n")
        # graph.serialize(format='application/ld+json')
