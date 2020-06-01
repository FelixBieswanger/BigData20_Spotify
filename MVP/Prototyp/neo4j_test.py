from neo4j import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost/system", auth=basic_auth("admin","root"), encrypted=False)


def get_all(tx):
    return tx.run("MATCH (p:Person) RETURN p")


with driver.session() as session:
    result = session.read_transaction(get_all)

    for person in result:
        for item in person.items():
            print(item)
    



