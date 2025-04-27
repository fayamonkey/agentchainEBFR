from typing import Dict, Any
from agents.specialized_agents import (
    SalesInquiryAgent, InventoryCheckAgent, PickingAgent,
    ShippingAgent, BillingAgent
)

class SalesProcessOrchestrator:
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the orchestrator with all required agents."""
        self.inquiry_agent = SalesInquiryAgent(model_name)
        self.inventory_agent = InventoryCheckAgent(model_name)
        self.picking_agent = PickingAgent(model_name)
        self.shipping_agent = ShippingAgent(model_name)
        self.billing_agent = BillingAgent(model_name)
        
    def show_process_chart(self, current_step: str):
        """Display the current position in the process flow."""
        print("\n📊 Current Position in Sales Process:")
        print("=" * 50)
        steps = [
            ("Sales Inquiry", "📝"),
            ("Inventory Check", "🔍"),
            ("Picking", "📦"),
            ("Shipping", "🚚"),
            ("Billing", "💰")
        ]
        
        for step, icon in steps:
            if step == current_step:
                print(f"➡️ {icon} {step} <- You are here")
            else:
                print(f"   {icon} {step}")
        print("=" * 50)
        
    def process_sales_inquiry(self, initial_inquiry: str) -> Dict[str, Any]:
        """Process a sales inquiry through the entire workflow."""
        print("\n🏢 B2B Sales Process Simulation")
        print("=" * 50)
        
        # Step 1: Process Initial Inquiry
        self.show_process_chart("Sales Inquiry")
        print("\n📝 Processing Sales Inquiry")
        print("-" * 50)
        inquiry_result = self.inquiry_agent.execute({"inquiry": initial_inquiry})
        print(inquiry_result["sales_inquiry"])
        input("\nPress Enter to continue to inventory check...")
        
        # Step 2: Inventory Check
        self.show_process_chart("Inventory Check")
        print("\n🔍 Checking Inventory")
        print("-" * 50)
        inventory_result = self.inventory_agent.execute(inquiry_result)
        print(inventory_result["inventory_status"])
        
        # Decision Point 1: FG Stock Status
        print("\n❓ Decision Point - Finished Goods (FG) Stock")
        print("1. Sufficient FG stock available")
        print("2. Insufficient FG stock - Check Raw Materials")
        fg_choice = input("Select scenario (1-2): ")
        
        if fg_choice == "2":
            print("\n❓ Decision Point - Raw Materials (RM) Stock")
            print("1. Sufficient RM stock - Can manufacture")
            print("2. Insufficient RM stock - Need to order")
            rm_choice = input("Select scenario (1-2): ")
            
            if rm_choice == "2":
                print("\n⚠️ Process halted: Insufficient stock and materials")
                print("Next steps would be:")
                print("1. Order required raw materials")
                print("2. Update customer about delay")
                print("3. Reschedule production when materials arrive")
                return {"status": "halted", "reason": "insufficient_stock"}
        
        # Step 3: Picking Process
        self.show_process_chart("Picking")
        print("\n📦 Creating Picking Documents")
        print("-" * 50)
        picking_result = self.picking_agent.execute({
            "inquiry": inquiry_result,
            "inventory": inventory_result,
            "fg_status": "sufficient" if fg_choice == "1" else "insufficient"
        })
        print(picking_result["picking_documents"])
        input("\nPress Enter to continue to shipping...")
        
        # Step 4: Shipping Process
        self.show_process_chart("Shipping")
        print("\n🚚 Processing Shipment")
        print("-" * 50)
        shipping_result = self.shipping_agent.execute(picking_result)
        print(shipping_result["shipping_documents"])
        input("\nPress Enter to continue to billing...")
        
        # Step 5: Billing Process
        self.show_process_chart("Billing")
        print("\n💰 Generating Billing Documents")
        print("-" * 50)
        billing_result = self.billing_agent.execute(shipping_result)
        print(billing_result["billing_documents"])
        
        print("\n✅ Process completed successfully!")
        print("\nProcess Summary:")
        print("1. Sales Inquiry: Customer order received and processed")
        print("2. Inventory: Stock availability confirmed")
        print("3. Picking: Items picked from warehouse")
        print("4. Shipping: Goods prepared for shipment")
        print("5. Billing: Invoice and delivery note generated")
        
        return {
            "inquiry_result": inquiry_result,
            "inventory_result": inventory_result,
            "picking_result": picking_result,
            "shipping_result": shipping_result,
            "billing_result": billing_result
        } 