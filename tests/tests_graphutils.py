import sys
import unittest
import snap

sys.path.append('../')
import graphutils

class TestGraphUtilsFunctions(unittest.TestCase):
    
    def setUp(self):
        # create a graph which will be used for test add_nodes_and_edges
        self.graph = snap.TNEANet.New()
        self.graph.AddStrAttrN('date')
        self.graph.AddStrAttrN('type')
        self.graph.AddStrAttrE('date')

        idx = 0
        for year in range(2012,2015):
            for month in range(10,13):
                for day in range(10,30):                
                    date = '-'.join([str(year),str(month),str(day)])
                    self.graph.AddNode(idx)

                    if (idx > 0):
                        edge = self.graph.AddEdge(idx,idx-1)
                        self.graph.AddStrAttrDatE(edge,date,'date')

                    self.graph.AddStrAttrDatN(idx,date,'date')
                    if day % 2 == 0:
                        self.graph.AddStrAttrDatN(idx,'even','type')
                    else:
                         self.graph.AddStrAttrDatN(idx,'odd','type')
                    idx+=1

        # there will be a total of 3*3*20 = 180 nodes and 180-1 edges #
        self.partial_graph = snap.TNEANet.New()
        self.partial_graph.AddStrAttrN('date')
        self.partial_graph.AddStrAttrE('date')
        self.partial_graph.AddStrAttrN('type')

    def test_add_nodes_and_edges(self):
        # this criterion wont select any edge or nodes
        criterion0 = lambda x : x < '2000-01-01'
        graphutils.add_nodes_and_edges(self.graph,self.partial_graph,criterion0)
        self.assertEquals(self.partial_graph.GetNodes(),0)
        self.assertEquals(self.partial_graph.GetEdges(),0)

        # this criterion will only keep the first 60 nodes and 59 edges
        criterion60 = lambda x : x < '2013-01-01'
        graphutils.add_nodes_and_edges(self.graph,self.partial_graph,criterion60)
        self.assertEquals(self.partial_graph.GetNodes(),60)
        self.assertEquals(self.partial_graph.GetEdges(),59)

        # this criterion will only keep the first and last 60 nodes, and 119 edges in total
        criterion120 = lambda x : (x < '2014-01-01')
        graphutils.add_nodes_and_edges(self.graph,self.partial_graph,criterion120)
        self.assertEquals(self.partial_graph.GetNodes(),120)
        self.assertEquals(self.partial_graph.GetEdges(),119)
            
if __name__ == '__main__':
    unittest.main()
