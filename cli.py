import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from app.models.state import ShoppingAgentState
from app.models.cart import Cart, HITLApprovalRequest
from app.agents.graph import shopping_graph
from app.agents.cart_agent import autonomous_cart_agent

console = Console()

async def run_cli():
    console.print(Panel.fit(
        "[bold cyan]⚡ AUTONOMOUS E-COMMERCE AI SHOPPING AGENT[/bold cyan]\n"
        "[dim]Powered by LangGraph Multi-Agent Architecture • Hybrid Search • Shopify Verified • HITL Guarded[/dim]",
        border_style="cyan"
    ))

    cart = Cart(id="cli_cart")
    hitl_req = None
    session_id = "cli_session_001"

    console.print("\n[bold green]Ready! Try typing:[/bold green] [italic]'I need a laptop under ₹70,000 for programming, machine learning, and gaming.'[/italic]")
    console.print("[dim]Commands: 'cart' to view cart, 'checkout' to initiate review, 'exit' to quit.\n[/dim]")

    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]Customer[/bold yellow]").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Exiting shopping session. Goodbye![/dim]")
                break

            # Handle direct cart command
            if user_input.lower() == "cart":
                cart.recalculate()
                t = Table(title="🛒 Current Shopping Cart", border_style="magenta")
                t.add_column("Item", style="cyan")
                t.add_column("Variant SKU", style="dim")
                t.add_column("Qty", justify="center")
                t.add_column("Unit Price", justify="right")
                t.add_column("Total", justify="right", style="green")
                for it in cart.items:
                    t.add_row(it.title, it.sku or "N/A", str(it.quantity), f"₹{it.price:,.2f}", f"₹{it.item_total:,.2f}")
                console.print(t)
                console.print(f"[bold]Subtotal:[/bold] ₹{cart.subtotal:,.2f} | [bold]Tax (18%):[/bold] ₹{cart.tax_amount:,.2f} | [bold]Estimated Total:[/bold] [bold green]₹{cart.total:,.2f}[/bold green]")
                continue

            # Execute LangGraph Pipeline
            console.print("[cyan]⏳ Agents collaborating: Intent -> Search -> Inventory -> Comparison -> Recommendation...[/cyan]")
            
            initial_state: ShoppingAgentState = {
                "messages": [{"role": "user", "content": user_input}],
                "session_id": session_id,
                "user_query": user_input,
                "intent": None,
                "clarification_needed": False,
                "clarification_questions": [],
                "search_query": "",
                "search_filters": {},
                "candidate_products": [],
                "comparison_data": None,
                "recommended_products": [],
                "inventory_checked": False,
                "live_inventory_details": {},
                "cart": cart.model_dump(),
                "hitl_approval_required": hitl_req is not None and not hitl_req.confirmed,
                "hitl_approval_request": hitl_req.model_dump() if hitl_req else None,
                "hitl_confirmed": hitl_req.confirmed if hitl_req else False,
                "checkout_url": cart.checkout_url,
                "next_step": "search",
                "final_response": ""
            }

            final_state = await shopping_graph.ainvoke(initial_state)

            # Sync cart state
            if final_state.get("cart"):
                cart = Cart(**final_state["cart"])

            # 1. Print Extracted Intent Breakdown
            intent = final_state.get("intent")
            if intent:
                intent_table = Table(title="🎯 Extracted Customer Intent", border_style="blue")
                intent_table.add_column("Parameter", style="bold")
                intent_table.add_column("Extracted Value", style="cyan")
                intent_table.add_row("Category", str(intent.get("category")))
                intent_table.add_row("Max Budget", f"₹{intent.get('budget_max'):,.2f}" if intent.get("budget_max") else "Not specified")
                intent_table.add_row("Target Purposes", ", ".join(intent.get("purpose", [])) or "General")
                intent_table.add_row("Preferred Specs", str(intent.get("preferred_specs", {})))
                console.print(intent_table)

            # 2. Render Markdown Response
            response_md = final_state.get("final_response", "")
            if response_md:
                console.print("\n[bold cyan]🤖 Shopping Agent Output:[/bold cyan]")
                console.print(Markdown(response_md))

            # 3. Check for Human-In-The-Loop Confirmation
            if final_state.get("hitl_approval_required"):
                req_data = final_state.get("hitl_approval_request", {})
                hitl_req = HITLApprovalRequest(**req_data)
                
                console.print("\n" + "="*60)
                console.print("[bold red]🛡️ HUMAN-IN-THE-LOOP CHECKOUT CONFIRMATION[/bold red]")
                console.print("[yellow]The agent NEVER places orders or charges payment autonomously without your explicit authorization.[/yellow]")
                
                user_confirms = Confirm.ask(f"\nDo you authorize proceeding to secure checkout with total ₹{cart.total:,.2f}?")
                if user_confirms:
                    hitl_req.confirmed = True
                    checkout_res = await autonomous_cart_agent.execute_confirmed_checkout(cart, hitl_req)
                    console.print(Panel(
                        f"[bold green]✅ ORDER AUTHORIZED BY CUSTOMER![/bold green]\n\n"
                        f"[bold]Verified Live Total:[/bold] ₹{cart.total:,.2f}\n"
                        f"[bold]Shopify Permlink Checkout URL:[/bold]\n[underline cyan]{checkout_res['checkout_url']}[/underline cyan]\n\n"
                        f"[dim]Click the URL above to complete payment on Shopify.[/dim]",
                        border_style="green"
                    ))
                    hitl_req = None
                else:
                    console.print("[bold yellow]Checkout was not authorized. Order remains in cart for adjustments.[/bold yellow]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    asyncio.run(run_cli())
