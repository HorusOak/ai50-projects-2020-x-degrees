import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    #Keep track of number of degree of separation and iterations
    sep_path = []
    max_iter = 6
    
    #Initializes an empty explored nodes list
    explored_nodes=[]
    
    #Initialize the nodes and the frontier
    current = Node(state = source, parent = None, action = None)
    goal = Node(state = target, parent = None, action = None)
    frontier = QueueFrontier()
    neighbors_per_degree = len(neighbors_for_person(source))
    
    while max_iter > 0:
        cont = 0
        sum_neighbors_per_degree = 0
        while cont < neighbors_per_degree:
            neighbors=list(neighbors_for_person(current.state))
            #Check for target before adding nodes to the frontier
            for i in range(len(neighbors)):
                if goal.state == neighbors[i][1]:
                    sep_path.append(neighbors[i])
                    #Trace back the path
                    while current.state != source:
                        sep_path.append((current.action,current.state))
                        for j in range(len(explored_nodes)):
                            if current.parent == explored_nodes[j].state:
                                current = explored_nodes[j]
                                break
                    sep_path.reverse()
                    return sep_path
                #Add nodes to the frontier except the ones with the same source actor
                elif current.state != neighbors[i][1]:
                    frontier.add(Node(state = neighbors[i][1], \
                    parent = current.state, action = neighbors[i][0]))
                    #Find the number of neighbors per degree
                    sum_neighbors_per_degree += len(neighbors_for_person(current.state))
                cont+=1
            #Add analyzed nodes to explored and go to the next node
            explored_nodes.append(current)
            current = frontier.remove()        
            
        neighbors_per_degree = sum_neighbors_per_degree  
        max_iter -= 1
        
    return None    


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
