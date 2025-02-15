## TODO - make more efficient + elegant
import os
from collections import defaultdict
import csv

'''Data was obtained from https://www.fec.gov/data/browse-data/?tab=bulk-data
we assume that data has been downloaded and this file is run in the directory of the
unzipped files'''


path = r'C:\Users\Omar\Desktop\Election Finance Data'
os.chdir(path)

files = list(filter(lambda x:x.startswith('oth') or x.startswith('pas'),os.listdir()))
nfiles= len(files)

for fileNum,path in enumerate(files):
    print('working on file '+ str(fileNum+1) + ' of ' + str(nfiles))
    os.chdir(path)
    
    #storing data as weighted directed and unweighted un directed graph since edges fit in memory
    nodes = set() 
    undirEdges = set() #this is inefficient #TODO clean this up
    edges = defaultdict(int) # (src,dst): net weight
    
    if path.startswith('oth'):
        fileID = 'itoth.txt'
    elif path.startswith('pas'):
        fileID = 'itpas2.txt'
        
    
    with open(fileID) as fptr: 
        for line in fptr:
            data = (line).split('|')
            
            #this type of info comes from data description from source website 
            dst = data[0]
            src = data[15]
            weight = int(data[14])
            
            if len(dst)>=2 and len(src)>=2 and weight!=0:##IDs are usually 9 chars 
                nodes.add(src)
                nodes.add(dst)
            
                edges[(src,dst)] += weight #directed + weighted
                
                #undir + unweighted
                undirEdges.add((src,dst))
                undirEdges.add((dst,src))
    
    #putting all files in main directory
    os.chdir('..')
    
    nodes = sorted(nodes)
    nnodes = len(nodes)
    
    #throwing out bad edges 
    badEdges = []
    for e in edges:
        if edges[e]==0:
            badEdges.append(e)
    
    for e in badEdges:
        edges.pop(e)
    
    nedges = len(edges)
    
    nodeMap = {node:i for i,node in enumerate(nodes)}
    
    
    #making files for directed + undirected graphs + node labels for each graph
    with open(path + '.labels','w') as fptr:
        for commID in nodes:
            fptr.write('%s\n' %commID)
    
    #                
    with open(path + '-directed.smat','w') as fptr:
        fptr.write('{0:d}\t{1:d}\t{2:d}\n'.format(nnodes,nnodes,nedges))    
        for e in sorted(map(lambda x:(nodeMap[x[0][0]],nodeMap[x[0][1]],x[1]),edges.items())):
            fptr.write('{0:d}\t{1:d}\t{2:d}\n'.format(e[0],e[1],e[2]))
    
    #undirected edges
    with open(path + '.smat','w') as fptr:
        fptr.write('{0:d}\t{1:d}\t{2:d}\n'.format(nnodes,nnodes,len(undirEdges)))    
        for e in sorted(map(lambda x:(nodeMap[x[0]],nodeMap[x[1]]),undirEdges)):
            fptr.write('{0:d}\t{1:d}\t{2:d}\n'.format(e[0],e[1],1))

# MASTER FILE for committee names
file = r'committees-2019-10-09T11_19_02.csv'
commNames = []
with open(file,'r') as csv_file:
    csv_reader = csv.reader(csv_file,delimiter = ',')
    header = next(csv_reader)
    
    nameInd = header.index('name')
    commInd = header.index('committee_id')
    
    for line in csv_reader:
        commNames.append((line[commInd],line[nameInd]))
        
#writing to file 
with open('committee-names.labels','w') as fptr:
    #fptr.write('{0:s}\t{1:s}\n'.format('committee_id','committee_name'))#no header for now
    for comm in sorted(commNames):
        fptr.write('{0:s}\t{1:s}\n'.format(comm[0],comm[1]))
    
#### TODO: consider hashing committee IDs to have consistent labeling across all files
