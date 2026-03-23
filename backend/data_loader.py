"""Data loader for JSONL files from SAP O2C dataset."""
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.entities = {}
        self.relationships = []

    def load_jsonl_files(self, folder_name: str) -> List[Dict[str, Any]]:
        """Load all JSONL files from a folder."""
        folder_path = self.data_dir / folder_name
        records = []
        
        if not folder_path.exists():
            return records
        
        for file in folder_path.glob("*.jsonl"):
            with open(file, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        
        return records

    def load_all_entities(self):
        """Load all entities from the dataset."""
        # Load each entity type
        entity_types = {
            'sales_order_headers': ('salesOrder', 'order'),
            'sales_order_items': ('salesOrderItem', 'order_item'),
            'billing_document_headers': ('billingDocument', 'invoice'),
            'billing_document_items': ('billingDocument', 'invoice_item'),
            'outbound_delivery_headers': ('deliveryDocument', 'delivery'),
            'outbound_delivery_items': ('deliveryDocument', 'delivery_item'),
            'products': ('product', 'product'),
            'business_partners': ('businessPartner', 'customer'),
            'business_partner_addresses': ('address', 'address'),
            'payments_accounts_receivable': ('paymentReference', 'payment'),
            'journal_entry_items_accounts_receivable': ('accountingDocument', 'journal_entry'),
            'plants': ('plant', 'plant'),
            'product_descriptions': ('product', 'product'),
            'customer_company_assignments': ('customerCompanyAssignment', 'assignment'),
            'customer_sales_area_assignments': ('customerSalesAreaAssignment', 'assignment'),
            'product_plants': ('product', 'product'),
            'product_storage_locations': ('product', 'product'),
        }
        
        for folder, (id_field, entity_type) in entity_types.items():
            records = self.load_jsonl_files(folder)
            if records:
                self.entities[entity_type] = {
                    'records': records,
                    'id_field': id_field,
                    'count': len(records)
                }
                print(f"Loaded {len(records)} {entity_type} records")
        
        return self.entities

    def get_entity_count(self) -> Dict[str, int]:
        """Get count of each entity type."""
        return {k: v['count'] for k, v in self.entities.items()}

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all entities of a specific type."""
        return self.entities.get(entity_type, {}).get('records', [])
