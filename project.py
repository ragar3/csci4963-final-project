import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import operator


################################################################################
# Calculate values for common neighbors, nearby neighbors, jaccard, and random
################################################################################
def compute_link_prediction(link_prediction_type, G):

	# sort edges in temporal order
	edges = sorted(G.edges(data=True), key=lambda t: t[2].get('weight', 1))

	# Generate a new graph containing the first 25% of the links in the graph
	t_0 = G.size()/4
	G1 = nx.MultiGraph()
	counter = 0
	for e in edges:
		if (counter < t_0):
			G1.add_edge(e[0],e[1])
		counter += 1

	dmax = sorted([d for n, d in G1.degree()], reverse=True)[0]

	prediction_values = {}
	for v in G1.nodes():
			for u in G1.nodes():
				Nu = set(G1.neighbors(u))
				Nv = set(G1.neighbors(v))
				k = 0
				if v > u and G1.has_edge(v, u) == False:

						# random links
						if (link_prediction_type == "random_links"):
							k = random.randint(0, 1)

						# common neighbors
						if (link_prediction_type == "common_neighbors"):
						#if (link_prediction_type == "foo"):
							k = len(Nu.intersection(Nv))

						# jaccard
						if (link_prediction_type == "jaccard"):
						#if (link_prediction_type == "foo"):
							k = len(Nv.intersection(Nu))
							k /= len(Nv.union(Nu))
							k *= dmax

						# nearby neighbors
						if (link_prediction_type == "nearby_neighbors"):
							for v1 in G1.neighbors(u):
								for u1 in G1.neighbors(v):
									# these are the neighbors of the neighbors
									Nu2 = set(G1.neighbors(u1))
									Nv2 = set(G1.neighbors(v1))
									if v1 > u1 and G1.has_edge(v1, u1) == False:
											k = len(Nu.intersection(Nv)) + 0.25*len(Nu2.intersection(Nv2)) 

						if k > 0:
							prediction_values[(v,u)] = int(k)
						
	return prediction_values


#################################################################################
# Calculate precision for common neighbors, nearby neighbors, jaccard, and random
#################################################################################
def calc_link_prediction(G, dataset_type, testing_size):
	# get testing_size number of random predictions
	randompredict = compute_link_prediction("random_links", G)
	# sampling from a set deprecated since Python 3.9 - (so need to convert to a list)
	sortedrandom = dict(random.sample(list(randompredict.items()), testing_size))
	#print(sortedrandom)

	commons = compute_link_prediction("common_neighbors", G)
	# take largest values 
	sortedcommons =  dict(sorted(commons.items(), key=lambda x:x[1], reverse = True)[:testing_size])
	#print(sortedcommons)

	jaccard_attachment = compute_link_prediction("jaccard", G)
	# take largest values 
	sortedjaccard =  dict(sorted(jaccard_attachment.items(), key=lambda x:x[1], reverse = True)[:testing_size])
	#print(sortedcommons)

	nearby = compute_link_prediction("nearby_neighbors", G)
	# take largest values 
	sortednearby =  dict(sorted(nearby.items(), key=lambda x:x[1], reverse = True)[:testing_size])

	precision_random = 0.0
	precision_common_neighbors = 0.0
	precision_jaccard = 0.0
	precision_nearby_neighbors = 0.0

	random_edge_counts = 0
	common_edge_counts = 0 
	jaccard_edge_counts = 0 
	nearby_edge_counts = 0

	for c in sortedrandom:
		#print("in sortedrandom")
		if G.has_edge(c[0], c[1]):
				random_edge_counts += 1
				#print("adding a random edge count")

	for c in sortedcommons:
		if G.has_edge(c[0], c[1]):
				common_edge_counts += 1

	for c in sortedjaccard:
		if G.has_edge(c[0], c[1]):
				jaccard_edge_counts += 1

	for c in sortednearby:
		if G.has_edge(c[0], c[1]):
			nearby_edge_counts += 1

	precision_random = random_edge_counts/float(testing_size)
	precision_common_neighbors = common_edge_counts/float(testing_size)
	precision_jaccard_neighbors = jaccard_edge_counts/float(testing_size)
	precision_nearby_neighbors = nearby_edge_counts/float(testing_size)

	print(dataset_type)
	print("Precision random:", round(precision_random, 4))
	print("Precision common neighbors:", round(precision_common_neighbors, 4))
	print("Precision jaccard neighbors:", round(precision_jaccard_neighbors, 4))
	print("Precision nearby neighbors:", round(precision_nearby_neighbors, 4))


################################################################################
# Construct graphs from datasets
################################################################################
def create_graph(filename, typeofmovie):
	# create a graph from the idmb database
	# filename is the comma separated list of edges (i.e. directors, writers)
	# typeofmovie is set of ids of all the movies we care about (i.e horror movies)
	G = nx.Graph()
	file = open(filename, 'r')
	lines = file.readlines()
	for line in lines: # add edges to the Graph
		(title, ldirectors) = line.split()
		if (title in typeofmovie):
			directors = ldirectors.split(",")
			for d in directors:
				for d2 in directors:
					# do not count self edges
					if (d != d2):
						G.add_edge(d,d2)
	file.close()
	return G

def create_set(filename):
	# read in a specific titles from the idmb database
	# and create a set of their ids
	file = open(filename, 'r')
	lines = file.readlines()
	# create a set of horror titles
	s = set()
	for line in lines:
		movieid = line.strip()
		s.add(movieid)
	return s

def get_total_degrees(G):
	total_degrees = 0
	for node in G.nodes():
			total_degrees = total_degrees + G.degree(node)
	return total_degrees


################################################################################
# Define input files and datasets
################################################################################

# do cond-mat authors
G = nx.read_gml("cond-mat.gml")
testing_size = int(get_total_degrees(G)/3)
calc_link_prediction(G,"AUTHOR DATASET",testing_size)

# the other input files were too big to upload to submitty :(
genre = create_set("horrortitles.txt")
# genre = create_set("biographytitles.txt")
# genre = create_set("scifititles.txt")
# genre = create_set("westerntitles.txt")

# do imdb directors
G_directors = create_graph("directors.txt",genre)
testing_size = int(get_total_degrees(G_directors)/3)
calc_link_prediction(G_directors,"DIRECTOR DATASET", testing_size)

# do imdb writers
G_writers = create_graph("writers.txt",genre )
testing_size = int(get_total_degrees(G_writers)/3)
calc_link_prediction(G_writers,"WRITER DATASET", testing_size)






'''
Information courtesy of
IMDb
(https://www.imdb.com).
Used with permission.
'''