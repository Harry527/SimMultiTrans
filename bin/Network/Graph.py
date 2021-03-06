#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bin.Network.Node import Node

import numpy as np
import matplotlib.pyplot as plt
import plotly as pt
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

from urllib.request import urlopen

import itertools as itt
import json


class Graph(object):
    def __init__(self):
        self.graph_top = {}

        # all edges
        self.edges_set = []

        # path ram
        self.graph_path = {}

    def import_graph(self, file_name):
        with open(f'{file_name}') as file_data:
            self.graph_top = json.load(file_data)
        self.generate_nodes()
 
    def generate_node(self, nid):
        n = Node( nid, self.graph_top )
        # print(n.id)
        self.graph_top[nid].update({'node': n})
        

    def generate_nodes(self):
        for node in self.graph_top:
            # print(node, (self.graph_top[node]['lat'], self.graph_top[node]['lon']), self.graph_top[node]['mode'].split(','))
            n = Node( node, self.graph_top )
            # print(n.id)
            self.graph_top[node].update({'node': n})

    def export_graph(self, file_name):
        with open(f'{file_name}', 'w') as file_data:
            json.dump(self.graph_top, file_data)

    def add_node(self, nid, lat, lon, mode):
        if ( nid not in self.graph_top ):
            self.graph_top[nid] = {}
            self.graph_top[nid]['lat'] = lat
            self.graph_top[nid]['lon'] = lon
            self.graph_top[nid]['mode'] = mode
            self.graph_top[nid]['nei'] = {}
            

    def add_edge(self, ori, dest, mode, dist):
        if ( ori in self.graph_top and dest in self.graph_top and ori != dest ):
            self.graph_top[ori]['nei'][dest] = {'mode': mode, 'dist': dist}
            

    def get_allnodes(self):
        return list(self.graph_top.keys())
    
    def get_size(self):
        return len( self.graph_top )

    def get_edge(self, ori, dest):
        '''return (ori, dest) edges'''
        if (ori in self.graph_top and dest in self.graph_top and ori != dest):
            if dest in self.graph_top[ori]['nei'].keys():
                return (ori, dest, self.graph_top[ori]['nei'][dest])

    def get_all_edges(self):
        '''return all edges'''
        if ( not self.edges_set ):
            for ori in self.graph_top:
                self.edges_set.append( [ (ori ,dest) for dest in self.graph_top[ori]['nei'] ] )
        return self.edges_set
        

    def node_exists(self, node):
        return (node in self.graph_top)

    def edge_exists(self, ori, dest):
        if ( self.node_exists(ori) and self.node_exists(dest) ):
            return ( dest in self.graph_top[ori]['nei'] )
        else:
            return False

    
    def get_L1dist(self, ori, dest):
        if ( self.node_exists(ori) and self.node_exists(dest) ):
            return np.abs(self.graph_top[ori]['lat']-self.graph_top[dest]['lat']) + np.abs(self.graph_top[ori]['lon']-self.graph_top[dest]['lon'])
        else:
            return 0
    '''
    def get_path(self, ori, dest): 
        # print('routing...')
        if (ori not in self.graph_top and dest not in self.graph_top):
            return {}

        if (ori in self.graph_path) and (dest in self.graph_path[ori]):
            # print('path exists')
            return self.graph_path[ori][dest]
        else:
            route = Routing(self, ori, dest)
            path = route.get_path('bus_simplex')
            # print(path)
            self.save_path(ori, dest, path)
            return path

        
    def save_path(self, ori, dest, path):
        if (ori not in self.graph_path):
            self.graph_path[ori] = {dest: []}
            self.graph_path[ori][dest].append(path)
        elif (dest not in self.graph_path):
            self.graph_path[ori][dest] = []
            self.graph_path[ori][dest].append(path)
        else:
            return
    '''

    def randomize_graph(self, seed, msize, modeset, max_localnodes, mapscale):
        np.random.seed(seed)
        # top_matrix = np.random.randint(2, size=(msize, msize))
        self.graph_top = {}
        self.graph_path = {}
        
        transfer_mode = ','.join(modeset)

        loc_set = np.random.randint(low=0, high=mapscale*msize, size=(msize, 2))
        
        # generage transfer nodes and edges
        for ori in range(msize):
            self.add_node(nid=chr(65+ori), lat=loc_set[ori][0], lon=loc_set[ori][1], mode=transfer_mode)
            '''
            for dest in self.get_allnodes():
                if (ori == dest):
                    break
                else:
                    dist = self.get_L1dist(ori, dest)
                    # symmetric edge
                    self.add_edge(ori=ori, dest=dest, mode=modeset[0], dist=dist)
                    self.add_edge(ori=dest, dest=ori, mode=modeset[0], dist=dist)
            '''
        nodeperm = itt.permutations(self.get_allnodes(), 2)
        for odpair in nodeperm:
            dist = self.get_L1dist(odpair[0], odpair[1])
            self.add_edge(ori=odpair[0], dest=odpair[1], mode=modeset[0], dist=dist)
            self.add_edge(ori=odpair[1], dest=odpair[0], mode=modeset[0], dist=dist)
        
        self.generate_nodes()

        print(self.get_allnodes())
        # generate local nodes
        for t_node in self.get_allnodes():
            top_matrix = int(np.random.randint(max_localnodes, size=1))
            x = self.graph_top[t_node]['lat']
            y = self.graph_top[t_node]['lon']

            for l_node in range(top_matrix):
                x = x + round(mapscale/np.sqrt(msize) * np.random.normal(1) ,2)
                y = y + round(mapscale/np.sqrt(msize) * np.random.normal(1) ,2)
                nid = t_node+chr(49+l_node)
                self.add_node(nid=nid, lat=x, lon=y, mode=modeset[1])
                
                dist = self.get_L1dist(t_node, nid)
                self.add_edge(ori=t_node, dest=nid, mode=modeset[1], dist=dist)
                self.add_edge(ori=nid, dest=t_node, mode=modeset[1], dist=dist)
