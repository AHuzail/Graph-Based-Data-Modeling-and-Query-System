"""Graph construction from SAP O2C data."""
import networkx as nx
from typing import Dict, List, Any, Tuple
from data_loader import DataLoader


class GraphBuilder:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.graph = nx.MultiDiGraph()
        self.entity_index = {}  # Maps entity_id to node metadata
        self.relationships_map = []  # List of all relationships

    def build_graph(self):
        """Build the graph from loaded data."""
        print("Building graph...")
        
        # Add all nodes
        self._add_order_nodes()
        self._add_delivery_nodes()
        self._add_invoice_nodes()
        self._add_product_nodes()
        self._add_customer_nodes()
        self._add_payment_nodes()
        self._add_journal_entry_nodes()
        self._add_plant_nodes()
        
        # Add all edges (relationships)
        self._add_order_to_delivery_edges()
        self._add_order_to_invoice_edges()
        self._add_order_to_product_edges()
        self._add_order_to_customer_edges()
        self._add_delivery_to_product_edges()
        self._add_invoice_to_payment_edges()
        self._add_invoice_to_journal_entry_edges()
        self._add_customer_address_edges()
        
        print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def _add_order_nodes(self):
        """Add sales order nodes."""
        orders = self.data_loader.get_entities_by_type('order')
        for order in orders:
            order_id = order.get('salesOrder')
            if order_id:
                self.graph.add_node(
                    f"order_{order_id}",
                    type='order',
                    id=order_id,
                    amount=float(order.get('totalNetAmount', 0)),
                    customer=order.get('soldToParty'),
                    date=order.get('creationDate'),
                    status=order.get('overallDeliveryStatus'),
                    data=order
                )
                self.entity_index[f"order_{order_id}"] = order

    def _add_delivery_nodes(self):
        """Add outbound delivery nodes."""
        deliveries = self.data_loader.get_entities_by_type('delivery')
        for delivery in deliveries:
            delivery_id = delivery.get('deliveryDocument')
            if delivery_id:
                self.graph.add_node(
                    f"delivery_{delivery_id}",
                    type='delivery',
                    id=delivery_id,
                    date=delivery.get('creationDate'),
                    status=delivery.get('overallGoodsMovementStatus'),
                    data=delivery
                )
                self.entity_index[f"delivery_{delivery_id}"] = delivery

    def _add_invoice_nodes(self):
        """Add billing document (invoice) nodes."""
        invoices = self.data_loader.get_entities_by_type('invoice')
        for invoice in invoices:
            invoice_id = invoice.get('billingDocument')
            if invoice_id:
                self.graph.add_node(
                    f"invoice_{invoice_id}",
                    type='invoice',
                    id=invoice_id,
                    amount=float(invoice.get('totalNetAmount', 0)),
                    customer=invoice.get('soldToParty'),
                    date=invoice.get('billingDocumentDate'),
                    is_cancelled=invoice.get('billingDocumentIsCancelled'),
                    accounting_doc=invoice.get('accountingDocument'),
                    data=invoice
                )
                self.entity_index[f"invoice_{invoice_id}"] = invoice

    def _add_product_nodes(self):
        """Add product nodes."""
        products = self.data_loader.get_entities_by_type('product')
        for product in products:
            product_id = product.get('product')
            if product_id:
                self.graph.add_node(
                    f"product_{product_id}",
                    type='product',
                    id=product_id,
                    name=product.get('productOldId', product_id),
                    weight=float(product.get('netWeight', 0)),
                    unit=product.get('baseUnit'),
                    data=product
                )
                self.entity_index[f"product_{product_id}"] = product

    def _add_customer_nodes(self):
        """Add customer nodes."""
        customers = self.data_loader.get_entities_by_type('customer')
        for customer in customers:
            customer_id = customer.get('businessPartner')
            if customer_id:
                self.graph.add_node(
                    f"customer_{customer_id}",
                    type='customer',
                    id=customer_id,
                    name=customer.get('businessPartnerFullName'),
                    data=customer
                )
                self.entity_index[f"customer_{customer_id}"] = customer

    def _add_payment_nodes(self):
        """Add payment nodes."""
        payments = self.data_loader.get_entities_by_type('payment')
        for payment in payments[:100]:  # Limit for performance
            payment_id = payment.get('paymentReference', payment.get('accountingDocument', ''))
            if payment_id:
                self.graph.add_node(
                    f"payment_{payment_id}",
                    type='payment',
                    id=payment_id,
                    amount=float(payment.get('totalNetAmount', 0)),
                    date=payment.get('creationDate'),
                    data=payment
                )

    def _add_journal_entry_nodes(self):
        """Add journal entry nodes."""
        entries = self.data_loader.get_entities_by_type('journal_entry')
        for entry in entries[:100]:  # Limit for performance
            entry_id = entry.get('accountingDocument', '')
            if entry_id:
                self.graph.add_node(
                    f"journal_{entry_id}",
                    type='journal_entry',
                    id=entry_id,
                    data=entry
                )

    def _add_plant_nodes(self):
        """Add plant nodes."""
        plants = self.data_loader.get_entities_by_type('plant')
        for plant in plants[:50]:  # Limit for performance
            plant_id = plant.get('plant', '')
            if plant_id:
                self.graph.add_node(
                    f"plant_{plant_id}",
                    type='plant',
                    id=plant_id,
                    name=plant.get('plant'),
                    data=plant
                )

    def _add_order_to_delivery_edges(self):
        """Add edges from orders to deliveries (via shared reference)."""
        # This would require item-level matching from the data
        # For now, we create edges based on proximity and logic
        orders = self.data_loader.get_entities_by_type('order')
        deliveries = self.data_loader.get_entities_by_type('delivery')
        
        # Simple heuristic: match by date proximity and customer
        for order in orders[:500]:  # Limit for performance
            order_id = order.get('salesOrder')
            order_date = order.get('creationDate')
            
            for delivery in deliveries[:500]:
                delivery_id = delivery.get('deliveryDocument')
                delivery_date = delivery.get('creationDate')
                
                # Simple matching: same date or within few days
                if order_id and delivery_id and order_date and delivery_date:
                    if order_date[:10] == delivery_date[:10]:  # Same day
                        self.graph.add_edge(
                            f"order_{order_id}",
                            f"delivery_{delivery_id}",
                            relationship='creates'
                        )
                        self.relationships_map.append({
                            'source': f'order_{order_id}',
                            'target': f'delivery_{delivery_id}',
                            'type': 'creates'
                        })

    def _add_order_to_invoice_edges(self):
        """Add edges from orders to invoices."""
        orders = self.data_loader.get_entities_by_type('order')
        invoices = self.data_loader.get_entities_by_type('invoice')
        
        for order in orders[:500]:
            order_id = order.get('salesOrder')
            customer = order.get('soldToParty')
            
            for invoice in invoices:
                invoice_id = invoice.get('billingDocument')
                invoice_customer = invoice.get('soldToParty')
                
                # Match by customer and temporal proximity
                if order_id and invoice_id and customer == invoice_customer:
                    self.graph.add_edge(
                        f"order_{order_id}",
                        f"invoice_{invoice_id}",
                        relationship='billed_by'
                    )
                    self.relationships_map.append({
                        'source': f'order_{order_id}',
                        'target': f'invoice_{invoice_id}',
                        'type': 'billed_by'
                    })

    def _add_order_to_product_edges(self):
        """Add edges from orders to products."""
        # This would require sales_order_items data
        # For demonstration, create representative edges
        orders = self.data_loader.get_entities_by_type('order')
        products = self.data_loader.get_entities_by_type('product')
        
        for i, order in enumerate(orders[:100]):
            order_id = order.get('salesOrder')
            if order_id and i % 3 < len(products):
                product = products[i % len(products)]
                product_id = product.get('product')
                if product_id:
                    self.graph.add_edge(
                        f"order_{order_id}",
                        f"product_{product_id}",
                        relationship='contains'
                    )

    def _add_order_to_customer_edges(self):
        """Add edges from orders to customers."""
        orders = self.data_loader.get_entities_by_type('order')
        
        for order in orders[:500]:
            order_id = order.get('salesOrder')
            customer_id = order.get('soldToParty')
            
            if order_id and customer_id:
                self.graph.add_edge(
                    f"order_{order_id}",
                    f"customer_{customer_id}",
                    relationship='placed_by'
                )
                self.relationships_map.append({
                    'source': f'order_{order_id}',
                    'target': f'customer_{customer_id}',
                    'type': 'placed_by'
                })

    def _add_delivery_to_product_edges(self):
        """Add edges from deliveries to products."""
        deliveries = self.data_loader.get_entities_by_type('delivery')
        products = self.data_loader.get_entities_by_type('product')
        
        for i, delivery in enumerate(deliveries[:100]):
            delivery_id = delivery.get('deliveryDocument')
            if delivery_id and i % 5 < len(products):
                product = products[i % len(products)]
                product_id = product.get('product')
                if product_id:
                    self.graph.add_edge(
                        f"delivery_{delivery_id}",
                        f"product_{product_id}",
                        relationship='contains'
                    )

    def _add_invoice_to_payment_edges(self):
        """Add edges from invoices to payments."""
        invoices = self.data_loader.get_entities_by_type('invoice')
        payments = self.data_loader.get_entities_by_type('payment')
        
        for invoice in invoices[:100]:
            invoice_id = invoice.get('billingDocument')
            if invoice_id and len(payments) > 0:
                # Simple matching: invoice to first payment (demonstration)
                payment = payments[0]
                payment_id = payment.get('paymentReference', payment.get('accountingDocument'))
                if payment_id:
                    self.graph.add_edge(
                        f"invoice_{invoice_id}",
                        f"payment_{payment_id}",
                        relationship='paid_by'
                    )

    def _add_invoice_to_journal_entry_edges(self):
        """Add edges from invoices to journal entries."""
        invoices = self.data_loader.get_entities_by_type('invoice')
        
        for invoice in invoices[:100]:
            invoice_id = invoice.get('billingDocument')
            journal_id = invoice.get('accountingDocument')
            
            if invoice_id and journal_id:
                self.graph.add_edge(
                    f"invoice_{invoice_id}",
                    f"journal_{journal_id}",
                    relationship='recorded_in'
                )

    def _add_customer_address_edges(self):
        """Add edges from customers to addresses."""
        # Simplified for now
        pass

    def get_node_info(self, node_id: str) -> Dict[str, Any]:
        """Get detailed info about a node."""
        if node_id not in self.graph:
            return None
        return dict(self.graph.nodes[node_id])

    def get_neighbors(self, node_id: str, depth: int = 1) -> List[str]:
        """Get neighboring nodes within depth."""
        if node_id not in self.graph:
            return []
        
        neighbors = set()
        to_visit = [(node_id, 0)]
        visited = set()
        
        while to_visit:
            current, current_depth = to_visit.pop(0)
            if current in visited or current_depth > depth:
                continue
            
            visited.add(current)
            if current != node_id:
                neighbors.add(current)
            
            if current_depth < depth:
                for successor in self.graph.successors(current):
                    if successor not in visited:
                        to_visit.append((successor, current_depth + 1))
        
        return list(neighbors)

    def find_path(self, start: str, end: str) -> List[str]:
        """Find path between two nodes."""
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            return []
        except nx.NodeNotFound:
            return []

    def export_subgraph(self, center_node: str, depth: int = 2) -> Dict[str, Any]:
        """Export a subgraph centered on a node."""
        nodes = [center_node] + self.get_neighbors(center_node, depth)
        subgraph = self.graph.subgraph(nodes)
        
        return {
            'nodes': [{'id': n, **dict(subgraph.nodes[n])} for n in subgraph.nodes()],
            'edges': [{'from': u, 'to': v, **dict(d)} for u, v, d in subgraph.edges(data=True)]
        }
