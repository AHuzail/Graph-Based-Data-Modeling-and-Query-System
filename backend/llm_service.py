"""LLM integration using Google Gemini."""
import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = None
        self.conversation_history = []
        self.available = False
        
        if self.api_key and self.api_key != 'your_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.available = True
                print("✓ LLM service initialized")
            except Exception as e:
                print(f"⚠ LLM service initialization failed: {e}")
        else:
            print("⚠ GOOGLE_API_KEY not set - LLM features will be disabled")

    def generate_query_from_natural_language(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert natural language query to structured query."""
        
        if not self.available:
            return {
                'query_type': 'INVALID',
                'parameters': {},
                'explanation': 'LLM service not available - please configure GOOGLE_API_KEY',
                'is_valid': False
            }
        
        system_prompt = """You are an expert at converting natural language questions about business data into structured queries.

Available query types you can suggest:
1. "products_by_billing_count" - Find products with most billing documents
2. "trace_document_flow" - Trace order -> delivery -> invoice -> payment
3. "incomplete_flows" - Find orders with missing delivery/billing/payment
4. "customer_search" - Find all documents for a customer
5. "summary_statistics" - Get overview of the dataset
6. "general_analysis" - Provide analysis based on data

The dataset contains:
- Sales Orders (with amounts, dates, customers)
- Deliveries (outbound shipments)
- Billing Documents (invoices)
- Payments
- Customers
- Products
- Journal Entries

Guidelines:
- Extract query intent and parameters from the question
- Return a JSON response with 'query_type', 'parameters', and 'explanation'
- If query is outside dataset scope, set query_type to 'INVALID' with explanation
- Be strict about off-topic queries
"""

        prompt = f"""{system_prompt}

User question: {query}

Dataset context:
{json.dumps(context, indent=2)}

Respond ONLY with valid JSON in this format:
{{
    "query_type": "products_by_billing_count|trace_document_flow|incomplete_flows|customer_search|summary_statistics|general_analysis|INVALID",
    "parameters": {{}},
    "explanation": "Brief explanation of what will be queried",
    "is_valid": true/false
}}
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            if response_text.startswith('{'):
                result = json.loads(response_text)
            else:
                # Try to find JSON in response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    result = json.loads(response_text[start:end])
                else:
                    result = {
                        'query_type': 'INVALID',
                        'parameters': {},
                        'explanation': 'Could not parse response',
                        'is_valid': False
                    }
            
            return result
        except Exception as e:
            return {
                'query_type': 'INVALID',
                'parameters': {},
                'explanation': f'Error processing query: {str(e)}',
                'is_valid': False
            }

    def generate_natural_language_response(
        self,
        query: str,
        query_results: Dict[str, Any]
    ) -> str:
        """Convert structured query results to natural language."""
        
        system_prompt = """You are an expert business analyst explaining data insights to non-technical users.

Guidelines:
- Provide clear, concise explanations
- Highlight key findings and anomalies
- Use business language (orders, customers, revenue, etc.)
- Be specific with numbers and dates
- Mention if results are limited or sampled
- Keep response under 300 words
- If no meaningful results, clearly state that
"""

        prompt = f"""{system_prompt}

Query asked: {query}

Query results:
{json.dumps(query_results, indent=2, default=str)}

Provide a natural language explanation of these results for a business user.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def chat(self, message: str, context: Dict[str, Any]) -> str:
        """Have a multi-turn conversation with context."""
        
        system_message = """You are an intelligent assistant for exploring business data graphs.
        
You have access to a graph of:
- Sales Orders
- Deliveries
- Billing Documents
- Payments
- Customers
- Products

Your role is to:
1. Understand user questions about their business data
2. Suggest relevant queries
3. Interpret results in business context
4. REFUSE any questions outside the dataset domain

Key behaviors:
- Only discuss data and analysis from the provided dataset
- Be specific about what data is available
- Ask clarifying questions if needed
- Do not engage with general knowledge questions unrelated to the dataset
"""

        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # Check if message is about the dataset
        domain_check = f"""Is this question about the SAP Order-to-Cash dataset (orders, deliveries, invoices, payments, customers, products)?

Question: {message}

Answer with ONLY 'yes' or 'no'."""
        
        try:
            domain_response = self.model.generate_content(domain_check)
            if 'no' in domain_response.text.lower():
                response = "I can only help with questions about the provided dataset. This question appears to be outside my scope. Please ask about orders, deliveries, invoices, payments, customers, or products."
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response
                })
                return response
        except Exception as e:
            print(f"Error in domain check: {e}")
        
        # Generate response based on dataset
        prompt = f"""{system_message}

Dataset Summary:
{json.dumps(context, indent=2)}

User: {message}

Respond naturally and helpfully. If you can suggest a query, mention it. If you need clarification, ask."""

        try:
            response = self.model.generate_content(prompt)
            assistant_response = response.text
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_response
            })
            return assistant_response
        except Exception as e:
            return f"Error: {str(e)}"

    def get_conversation_history(self):
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
