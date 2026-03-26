"""Flask application for graph query system."""
import os
import json
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import networkx as nx

from data_loader import DataLoader
from graph_builder import GraphBuilder
from query_engine import QueryEngine
from llm_service import LLMService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global instances
data_loader = None
graph_builder = None
query_engine = None
llm_service = None
graph_summary = None


def initialize_system():
    """Initialize the graph system on startup."""
    global data_loader, graph_builder, query_engine, llm_service, graph_summary
    
    print("Initializing graph system...")
    
    # Get data directory
    data_dir = r'h:\Dodge AI\sap-o2c-data'
    if not Path(data_dir).exists():
        print(f"Data directory not found: {data_dir}")
        return False
    
    try:
        # Load data
        data_loader = DataLoader(data_dir)
        data_loader.load_all_entities()
        
        # Build graph
        graph_builder = GraphBuilder(data_loader)
        graph_builder.build_graph()
        
        # Initialize query engine
        query_engine = QueryEngine(graph_builder, data_loader)
        graph_summary = query_engine.get_summary_statistics()
        
        # Initialize LLM service
        try:
            llm_service = LLMService()
        except Exception as e:
            print(f"Warning: LLM service failed to initialize: {e}")
            llm_service = LLMService()  # This will set available=False
        
        print("System initialized successfully!")
        print(f"Summary: {graph_summary}")
        return True
    except Exception as e:
        print(f"Error initializing system: {e}")
        import traceback
        traceback.print_exc()
        return False


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'system_ready': graph_builder is not None
    })


# Graph statistics
@app.route('/api/graph/summary', methods=['GET'])
def get_graph_summary():
    """Get summary statistics about the graph."""
    if not graph_builder:
        return jsonify({'error': 'System not initialized'}), 500
    
    return jsonify(graph_summary)


# Get node details
@app.route('/api/graph/node/<node_id>', methods=['GET'])
def get_node(node_id):
    """Get detailed information about a node."""
    if not graph_builder:
        return jsonify({'error': 'System not initialized'}), 500
    
    node_info = graph_builder.get_node_info(node_id)
    if node_info is None:
        return jsonify({'error': f'Node {node_id} not found'}), 404
    
    return jsonify(node_info)


# Get node neighbors (subgraph)
@app.route('/api/graph/subgraph/<node_id>', methods=['GET'])
def get_subgraph(node_id):
    """Get subgraph centered on a node."""
    if not graph_builder:
        return jsonify({'error': 'System not initialized'}), 500
    
    depth = request.args.get('depth', 2, type=int)
    subgraph = graph_builder.export_subgraph(node_id, depth=depth)
    
    if not subgraph['nodes']:
        return jsonify({'error': f'Node {node_id} not found'}), 404
    
    return jsonify(subgraph)


# Get full graph data (limited to avoid overwhelming browser)
@app.route('/api/graph/all', methods=['GET'])
def get_full_graph():
    """Get full graph data with optional filtering."""
    if not graph_builder:
        return jsonify({'error': 'System not initialized'}), 500
    
    limit = request.args.get('limit', graph_builder.graph.number_of_nodes(), type=int)
    max_edges = request.args.get('max_edges', 2500, type=int)
    node_type = request.args.get('type', None, type=str)  # Filter by type if specified
    connected = request.args.get('connected', 'true', type=str).lower() != 'false'
    
    nodes = list(graph_builder.graph.nodes())
    graph_for_edges = graph_builder.graph
    
    # Filter nodes if type specified
    if node_type:
        nodes = [n for n in nodes if graph_builder.graph.nodes[n].get('type') == node_type]

    # Force a connected sample by selecting nodes from a single component and expanding by BFS.
    if connected and nodes:
        undirected = graph_builder.graph.to_undirected()
        sub_undirected = undirected.subgraph(nodes)
        components = list(nx.connected_components(sub_undirected))
        if components:
            largest_component = max(components, key=len)
            seed = next(iter(largest_component))
            bfs_nodes = []
            for node in nx.bfs_tree(sub_undirected, seed):
                bfs_nodes.append(node)
                if len(bfs_nodes) >= limit:
                    break
            nodes = bfs_nodes
    
    # Apply limit
    nodes = list(nodes)[:limit]
    
    # Get edges for these nodes
    node_set = set(nodes)
    filtered_edges = [
        (u, v, d) for u, v, d in graph_for_edges.edges(data=True) if u in node_set and v in node_set
    ]

    # Deduplicate multi-edges to keep visualization responsive.
    dedup_edges = []
    seen = set()
    for u, v, d in filtered_edges:
        rel = str(d.get('relationship', 'related_to'))
        key = (str(u), str(v), rel)
        if key in seen:
            continue
        seen.add(key)
        dedup_edges.append((u, v, d))

    if max_edges > 0:
        dedup_edges = dedup_edges[:max_edges]
    
    # Build lightweight, JSON-safe payload for browser rendering.
    vis_nodes = []
    for n in nodes:
        attrs = dict(graph_builder.graph.nodes[n])
        vis_nodes.append({
            'id': str(n),
            'type': str(attrs.get('type', 'unknown')),
            'entity_id': str(attrs.get('id', n)),
            'status': str(attrs.get('status', ''))
        })

    vis_edges = []
    for u, v, d in dedup_edges:
        vis_edges.append({
            'from': str(u),
            'to': str(v),
            'relationship': str(d.get('relationship', 'related_to'))
        })

    return jsonify({
        'nodes': vis_nodes,
        'edges': vis_edges,
        'meta': {
            'connected': connected,
            'returned_nodes': len(vis_nodes),
            'returned_edges': len(vis_edges),
            'max_edges': max_edges
        }
    })


# Query endpoints
@app.route('/api/query/products-by-billing', methods=['GET'])
def products_by_billing():
    """Get products by billing document count."""
    if not query_engine:
        return jsonify({'error': 'System not initialized'}), 500
    
    limit = request.args.get('limit', 10, type=int)
    results = query_engine.query_products_by_billing_count(limit=limit)
    
    return jsonify({
        'query': 'products_by_billing_count',
        'results': results
    })


@app.route('/api/query/trace-flow/<document_id>', methods=['GET'])
def trace_flow(document_id):
    """Trace the flow of a document."""
    if not query_engine:
        return jsonify({'error': 'System not initialized'}), 500
    
    doc_type = request.args.get('type', 'order', type=str)
    result = query_engine.trace_document_flow(document_id, doc_type)
    
    return jsonify(result)


@app.route('/api/query/incomplete-flows', methods=['GET'])
def incomplete_flows():
    """Get incomplete document flows."""
    if not query_engine:
        return jsonify({'error': 'System not initialized'}), 500
    
    results = query_engine.find_incomplete_flows()
    
    return jsonify({
        'query': 'incomplete_flows',
        'results': results
    })


@app.route('/api/query/customer/<customer_id>', methods=['GET'])
def get_customer_data(customer_id):
    """Get all data for a customer."""
    if not query_engine:
        return jsonify({'error': 'System not initialized'}), 500
    
    result = query_engine.search_by_customer(customer_id)
    
    return jsonify(result)


# LLM-powered query endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    """Process natural language query and return response."""
    if not llm_service or not query_engine:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message']
    
    # Validate query safety
    is_safe, safety_msg = query_engine.validate_query_safety(message)
    if not is_safe:
        return jsonify({
            'message': message,
            'response': 'This system is designed to answer questions related to the provided dataset only. Please ask about orders, deliveries, invoices, payments, customers, or products.',
            'valid': False,
            'reason': safety_msg
        })
    
    try:
        # Convert natural language to structured query
        query_instruction = llm_service.generate_query_from_natural_language(
            message,
            graph_summary
        )
        
        query_result = None
        
        # Execute the appropriate query
        if query_instruction['query_type'] == 'products_by_billing_count':
            query_result = query_engine.query_products_by_billing_count(limit=10)
        
        elif query_instruction['query_type'] == 'trace_document_flow':
            doc_id = query_instruction['parameters'].get('document_id', '740506')
            doc_type = query_instruction['parameters'].get('document_type', 'order')
            query_result = query_engine.trace_document_flow(doc_id, doc_type)
        
        elif query_instruction['query_type'] == 'incomplete_flows':
            query_result = query_engine.find_incomplete_flows()
        
        elif query_instruction['query_type'] == 'customer_search':
            customer_id = query_instruction['parameters'].get('customer_id', '310000108')
            query_result = query_engine.search_by_customer(customer_id)
        
        elif query_instruction['query_type'] == 'summary_statistics':
            query_result = graph_summary
        
        elif query_instruction['query_type'] == 'INVALID':
            return jsonify({
                'message': message,
                'response': 'This system is designed to answer questions related to the provided dataset only.',
                'valid': False,
                'reason': query_instruction.get('explanation', 'Off-topic question')
            })
        
        # Generate natural language response
        natural_response = llm_service.generate_natural_language_response(
            message,
            query_result
        )
        
        return jsonify({
            'message': message,
            'response': natural_response,
            'query_type': query_instruction['query_type'],
            'query_explanation': query_instruction.get('explanation'),
            'valid': True
        })
    
    except Exception as e:
        print(f"Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error processing query: {str(e)}'
        }), 500


# Catch-all endpoint for documentation
@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation."""
    return jsonify({
        'title': 'Graph Query System API',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/graph/summary': 'Get graph statistics',
            'GET /api/graph/node/<node_id>': 'Get node details',
            'GET /api/graph/subgraph/<node_id>': 'Get subgraph around node',
            'GET /api/graph/all?connected=true&limit=<n>': 'Get connected graph payload for visualization',
            'GET /api/query/products-by-billing': 'Get products by billing count',
            'GET /api/query/trace-flow/<document_id>': 'Trace document flow',
            'GET /api/query/incomplete-flows': 'Find incomplete flows',
            'GET /api/query/customer/<customer_id>': 'Get customer data',
            'POST /api/chat': 'Natural language query (send JSON with "message" key)'
        }
    })


if __name__ == '__main__':
    # Initialize system
    if not initialize_system():
        print("Failed to initialize system. Exiting.")
        exit(1)
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
