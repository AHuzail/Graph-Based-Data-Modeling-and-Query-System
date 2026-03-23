"""Quick test script to validate graph construction."""
import sys
sys.path.insert(0, '.')

from data_loader import DataLoader
from graph_builder import GraphBuilder
import os
from pathlib import Path

def main():
    # Verify data directory
    data_dir = r'h:\Dodge AI\sap-o2c-data'
    if not Path(data_dir).exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        return False
    
    print(f"✓ Data directory found: {data_dir}")
    
    # Load data
    print("\nLoading data...")
    loader = DataLoader(data_dir)
    entities = loader.load_all_entities()
    
    print(f"✓ Loaded {len(entities)} entity types")
    for entity_type, info in entities.items():
        print(f"  - {entity_type}: {info['count']} records")
    
    # Build graph
    print("\nBuilding graph...")
    builder = GraphBuilder(loader)
    builder.build_graph()
    
    print(f"✓ Graph built successfully")
    print(f"  - Total nodes: {builder.graph.number_of_nodes()}")
    print(f"  - Total edges: {builder.graph.number_of_edges()}")
    
    # Test a query
    print("\nTesting query engine...")
    from query_engine import QueryEngine
    qe = QueryEngine(builder, loader)
    
    # Test products by billing
    products = qe.query_products_by_billing_count(limit=5)
    print(f"✓ Top products query: {len(products)} results")
    if products:
        print(f"  - Top product: {products[0]['product_id']} ({products[0]['billing_document_count']} invoices)")
    
    # Test incomplete flows
    incomplete = qe.find_incomplete_flows()
    print(f"✓ Incomplete flows query: {len(incomplete['no_delivery'])} incomplete orders")
    
    print("\n✅ All tests passed! System is ready.")
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
