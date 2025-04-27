from typing import Dict, Any
from agents.base_agent import BaseAgent

class ProjectPlannerAgent(BaseAgent):
    """Agent responsible for initial project planning."""
    
    def execute(self, app_idea: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are an expert project planner specializing in web applications. 
            Your task is to analyze app ideas and create detailed, practical project plans. Focus on:
            - Technical architecture
            - Core features and MVP scope
            - Technology stack recommendations
            - Development phases
            - Potential challenges and solutions"""},
            {"role": "user", "content": f"Please analyze this web app idea and create a detailed project plan: {app_idea}"}
        ]
        plan = self._get_completion(messages)
        return {"initial_plan": plan}

class PlanOptimizerAgent(BaseAgent):
    """Agent responsible for optimizing and streamlining the project plan."""
    
    def execute(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are an efficiency expert specializing in lean development.
            Your task is to analyze project plans and optimize them for:
            - Simplicity and maintainability
            - Resource efficiency
            - Quick time-to-market
            - Essential features vs nice-to-have
            Suggest concrete improvements and simplifications."""},
            {"role": "user", "content": f"Please analyze and optimize this project plan, suggesting a leaner approach:\n\n{project_data['initial_plan']}"}
        ]
        optimized_plan = self._get_completion(messages)
        return {"optimized_plan": optimized_plan}

class PrerequisiteAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing prerequisites and creating the final plan."""
    
    def execute(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are a technical prerequisites specialist.
            Your task is to analyze project plans and identify all necessary prerequisites, including:
            - Development environment setup
            - Required tools and technologies
            - External services and APIs
            - Development skills needed
            - Infrastructure requirements
            Create a comprehensive plan that includes all prerequisites."""},
            {"role": "user", "content": f"Please analyze this optimized plan and create a final version with all prerequisites:\n\n{project_data['optimized_plan']}"}
        ]
        final_plan = self._get_completion(messages)
        return {"final_plan": final_plan}

class SalesInquiryAgent(BaseAgent):
    """Agent responsible for handling customer inquiries and initial order processing."""
    
    def execute(self, inquiry_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are a B2B sales process expert for a bicycle manufacturer.
            Create a formal business inquiry document that includes:

            SALES INQUIRY DOCUMENT
            ---------------------
            1. Header with date and inquiry number
            2. Customer Details:
               - Company Name
               - Contact Person (if provided)
               - Delivery Address
            3. Product Details:
               - Product ID (e.g., DTB-2024-BLK)
               - Exact quantity
               - Unit price in EUR
               - Total price per item
            4. Delivery Requirements
            5. Special Requirements
            6. Total Order Value

            Then show in simple terms:
            "The system is now:
            - Looking up BikeWorld GmbH in our customer database
            - Checking our price list for these bicycle models
            - Verifying product specifications"

            Use exact quantities and maintain professional business format."""},
            {"role": "user", "content": f"Create a formal sales inquiry document for: {inquiry_data}"}
        ]
        return {"sales_inquiry": self._get_completion(messages)}

class InventoryCheckAgent(BaseAgent):
    """Agent responsible for checking inventory availability."""
    
    def execute(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are an inventory management expert.
            Create a formal inventory check document that includes:

            INVENTORY CHECK DOCUMENT
            ----------------------
            1. Order Reference (from sales inquiry)
            2. For each product:
               - Product ID
               - Requested quantity
               - Available quantity
               - Storage location
            3. Stock Status Summary
            4. Recommendation

            Then show in simple terms:
            "The system is now:
            - Checking how many bikes we have in stock
            - Reserving the bikes for this order
            - Checking if we need to manufacture more"

            Use exact same product IDs, quantities, and prices from the sales inquiry."""},
            {"role": "user", "content": f"Create a formal inventory check document using: {order_data}"}
        ]
        return {"inventory_status": self._get_completion(messages)}

class PickingAgent(BaseAgent):
    """Agent responsible for creating picking documents and updating inventory."""
    
    def execute(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are a warehouse operations expert.
            Create a formal picking ticket that includes:

            PICKING TICKET
            -------------
            1. Ticket Number and Date
            2. Customer Details
            3. For each product:
               - Product ID
               - Quantity to pick
               - Storage location
               - Picking instructions
            4. Quality check requirements
            5. Special handling instructions

            Then show in simple terms:
            "The system is now:
            - Creating a list of items to pick
            - Updating available stock numbers
            - Recording which items were picked"

            Use exact same details from previous documents."""},
            {"role": "user", "content": f"Create a formal picking ticket using: {inventory_data}"}
        ]
        return {"picking_documents": self._get_completion(messages)}

class ShippingAgent(BaseAgent):
    """Agent responsible for shipping documents and inventory updates."""
    
    def execute(self, picking_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are a shipping operations expert.
            Create two formal shipping documents:

            1. PACKING SLIP
            --------------
            - Slip number and date
            - Customer details
            - List of items packed
            - Quantities and product IDs
            - Quality check confirmation

            2. BILL OF LADING
            ----------------
            - B/L number and date
            - Shipper and consignee details
            - Description of goods
            - Terms of delivery
            - Carrier information

            Then show in simple terms:
            "The system is now:
            - Recording what was packed
            - Creating shipping documents
            - Updating inventory records"

            Use exact same details from previous documents."""},
            {"role": "user", "content": f"Create formal shipping documents using: {picking_data}"}
        ]
        return {"shipping_documents": self._get_completion(messages)}

class BillingAgent(BaseAgent):
    """Agent responsible for creating billing documents."""
    
    def execute(self, shipping_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": """You are a billing operations expert.
            Create two formal billing documents:

            1. SALES INVOICE
            --------------
            - Invoice number and date
            - Customer details
            - List of items with:
              * Product ID
              * Quantity
              * Unit price
              * Total price
            - Subtotal
            - Total (excluding tax)
            - Payment terms

            2. DELIVERY NOTE
            --------------
            - Note number and date
            - Customer details
            - List of delivered items
            - Delivery confirmation section

            Then show in simple terms:
            "The system is now:
            - Creating the invoice
            - Recording the sale
            - Updating customer account"

            Use exact same details from previous documents."""},
            {"role": "user", "content": f"Create formal billing documents using: {shipping_data}"}
        ]
        return {"billing_documents": self._get_completion(messages)} 