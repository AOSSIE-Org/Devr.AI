
#####ONLY USE FOR TESTING NO NEED IN PRODUCTION#####
# Sometimes while testing falkorDB doesnt remove the graph when we stop the server. 
# So this script is used to remove the temp graph

from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)

graphs_to_delete = ['AutoPDFCleaner_tmp', 'AutoPDFCleaner']

for graph_id in graphs_to_delete:
    try:
        g = db.select_graph(graph_id)
        g.delete()
        print(f"✅ Successfully deleted graph: {graph_id}")
    except Exception as e:
        print(f"⚠️  Could not delete {graph_id} (it might not exist): {e}")