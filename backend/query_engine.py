"""Query engine for the graph system."""
from typing import Dict, List, Any, Tuple
from graph_builder import GraphBuilder
import json


class QueryEngine:
    def __init__(self, graph_builder: GraphBuilder, data_loader):
        self.graph = graph_builder.graph
        self.graph_builder = graph_builder
        self.data_loader = data_loader

    def query_products_by_billing_count(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find products with highest number of billing documents."""
        product_billing_count = {}
        
        # Count invoices connected to each product
        for invoice_node in self.graph.nodes():
            if not invoice_node.startswith('invoice_'):
                continue
            
            # Find connected products
            for successor in self.graph.successors(invoice_node):
                if successor.startswith('product_'):
                    product_id = self.graph.nodes[successor].get('id')
                    product_billing_count[product_id] = product_billing_count.get(product_id, 0) + 1
            
            # Also find products through orders
            for predecessor in self.graph.predecessors(invoice_node):
                if predecessor.startswith('order_'):
                    for successor in self.graph.successors(predecessor):
                        if successor.startswith('product_'):
                            product_id = self.graph.nodes[successor].get('id')
                            product_billing_count[product_id] = product_billing_count.get(product_id, 0) + 1
        
        # Sort and return top results
        sorted_products = sorted(product_billing_count.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for product_id, count in sorted_products[:limit]:
            product_node = f"product_{product_id}"
            if product_node in self.graph.nodes():
                node_data = dict(self.graph.nodes[product_node])
                results.append({
                    'product_id': product_id,
                    'product_name': node_data.get('name', ''),
                    'billing_document_count': count,
                    'metadata': node_data
                })
        
        return results

    def trace_document_flow(self, document_id: str, document_type: str = 'order') -> Dict[str, Any]:
        """Trace the complete flow of a document through the system."""
        
        # Map document type to node prefix
        type_prefix = {
            'order': 'order',
            'sales_order': 'order',
            'delivery': 'delivery',
            'invoice': 'invoice',
            'billing': 'invoice',
            'payment': 'payment'
        }
        
        node_prefix = type_prefix.get(document_type.lower(), document_type)
        node_id = f"{node_prefix}_{document_id}"
        
        if node_id not in self.graph.nodes():
            return {'error': f'Document {document_id} not found'}
        
        flow = {
            'document_id': document_id,
            'document_type': document_type,
            'path': [],
            'details': dict(self.graph.nodes[node_id])
        }
        
        # Trace forward (successors)
        visited = set()
        to_visit = [node_id]
        
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            flow['path'].append({
                'node_id': current,
                'type': self.graph.nodes[current].get('type'),
                'data': dict(self.graph.nodes[current])
            })
            
            for successor in self.graph.successors(current):
                if successor not in visited:
                    to_visit.append(successor)
        
        return flow

    def find_incomplete_flows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify sales orders with incomplete flows."""
        issues = {
            'no_delivery': [],
            'no_billing': [],
            'no_payment': []
        }
        
        orders = [n for n in self.graph.nodes() if n.startswith('order_')]
        
        for order_node in orders[:100]:  # Limit for performance
            order_id = self.graph.nodes[order_node].get('id')
            order_data = dict(self.graph.nodes[order_node])
            
            # Check for delivery
            has_delivery = False
            for successor in self.graph.successors(order_node):
                if successor.startswith('delivery_'):
                    has_delivery = True
                    break
            
            # Check for billing
            has_billing = False
            for successor in self.graph.successors(order_node):
                if successor.startswith('invoice_'):
                    has_billing = True
                    break
            
            # Check for payment
            has_payment = False
            for node in self.graph.nodes():
                if node.startswith('payment_'):
                    # Simple heuristic: check if in same time period
                    has_payment = True
                    break
            
            # Record issues
            if not has_delivery:
                issues['no_delivery'].append({
                    'order_id': order_id,
                    'amount': order_data.get('amount', 0),
                    'date': order_data.get('date')
                })
            
            if not has_billing and has_delivery:
                issues['no_billing'].append({
                    'order_id': order_id,
                    'amount': order_data.get('amount', 0),
                    'date': order_data.get('date')
                })
            
            if not has_payment and has_billing:
                issues['no_payment'].append({
                    'order_id': order_id,
                    'amount': order_data.get('amount', 0),
                    'date': order_data.get('date')
                })
        
        return issues

    def search_by_customer(self, customer_id: str) -> Dict[str, Any]:
        """Find all orders, deliveries, and invoices for a customer."""
        customer_node = f"customer_{customer_id}"
        
        if customer_node not in self.graph.nodes():
            return {'error': f'Customer {customer_id} not found'}
        
        result = {
            'customer_id': customer_id,
            'customer_data': dict(self.graph.nodes[customer_node]),
            'orders': [],
            'deliveries': [],
            'invoices': [],
            'total_amount': 0
        }
        
        # Find connected documents
        for predecessor in self.graph.predecessors(customer_node):
            if predecessor.startswith('order_'):
                order_data = dict(self.graph.nodes[predecessor])
                result['orders'].append(order_data)
                result['total_amount'] += order_data.get('amount', 0)
            elif predecessor.startswith('invoice_'):
                invoice_data = dict(self.graph.nodes[predecessor])
                result['invoices'].append(invoice_data)
        
        return result

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the graph."""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': {},
            'entity_counts': self.data_loader.get_entity_count()
        }
        
        # Count nodes by type
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
        
        return stats

    def validate_query_safety(self, query: str) -> Tuple[bool, str]:
        """Check if query is safe and domain-relevant."""
        
        # Whitelist of allowed query terms
        allowed_terms = [
            'order', 'delivery', 'invoice', 'billing', 'payment',
            'customer', 'product', 'sales', 'amount', 'date',
            'flow', 'trace', 'relationship', 'connected', 'incomplete',
            'broken', 'missing', 'count', 'top', 'highest', 'most',
            'billed', 'delivered', 'paid', 'journal', 'accounting'
        ]
        
        # Blacklist for queries we should reject
        blacklist_terms = [
            'delete', 'drop', 'truncate', 'update', 'insert', 'modify',
            'hack', 'exploit', 'password', 'sql', 'script', 'code'
        ]
        
        query_lower = query.lower()
        
        # Check for blacklisted terms
        for term in blacklist_terms:
            if term in query_lower:
                return False, f"Query contains unsafe term: {term}"
        
        # Check if query has at least one allowed term or is asking for analysis
        analysis_keywords = ['analyze', 'analyze', 'show', 'find', 'list', 'what', 'which', 'how']
        
        has_allowed_term = False
        for term in allowed_terms:
            if term in query_lower:
                has_allowed_term = True
                break
        
        for term in analysis_keywords:
            if term in query_lower:
                has_allowed_term = True
                break
        
        if not has_allowed_term:
            return False, "Query does not appear to be about the dataset"
        
        return True, "Query is valid"
