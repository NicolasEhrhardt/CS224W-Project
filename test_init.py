import workspace
import stats
import graphutils
import snap
from graphutils import delete_node_type, get_subgraph_by_date, copy_graph
from projection import projection

graph_file = 'computed/graph.bin'

f = snap.TFIn(graph_file)
full_graph = snap.TNEANet.Load(f)

dates = []

for year in range(2004,2014):
    for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        date = str(year) + '-' + month + '-' + '01'
        dates.append(date)

dates = dates[10::]
nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,dates)

## Compute 
