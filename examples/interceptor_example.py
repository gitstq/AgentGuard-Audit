#!/usr/bin/env python3
"""
Interceptor pattern example for AgentGuard-Audit.

This example demonstrates how to use the interceptor pattern for
zero-intrusion integration with your existing AI Agent code.
"""

import time
import random
from agentguard_audit import AuditEngine, AgentInterceptor
from agentguard_audit.reporters import ConsoleReporter


# Simulate an AI Agent class
class MyAIAgent:
    """Example AI Agent with various capabilities."""

    def __init__(self):
        self.name = "SmartAssistant"

    def search_web(self, query: str) -> dict:
        """Simulate web search."""
        time.sleep(0.1)
        return {"results": [f"Result for: {query}"], "count": 1}

    def calculate(self, expression: str) -> float:
        """Simulate calculation."""
        time.sleep(0.05)
        # Simple eval for demo (don't do this in production!)
        try:
            return eval(expression)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

    def generate_response(self, prompt: str) -> str:
        """Simulate LLM response generation."""
        time.sleep(0.2)
        responses = [
            "I understand your request.",
            "Here's what I found:",
            "I can help with that.",
            "Let me think about this...",
        ]
        return random.choice(responses)

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Simulate sending email."""
        time.sleep(0.15)
        if random.random() < 0.2:  # 20% chance of error
            raise ConnectionError("Failed to connect to email server")
        return {"message_id": f"msg_{random.randint(1000, 9999)}", "status": "sent"}


def main():
    """Run interceptor example."""
    print("🛡️  AgentGuard-Audit Interceptor Example\n")

    # Initialize audit engine
    engine = AuditEngine(
        agent_id="interceptor-demo",
        agent_name="Interceptor Demo Agent",
    )

    # Create interceptor
    interceptor = AgentInterceptor(engine)

    # Create agent
    agent = MyAIAgent()

    # Wrap methods with interceptors
    # Method 1: Using decorators directly

    @interceptor.intercept_tool(tool_name="web_search")
    def audited_search(query: str) -> dict:
        return agent.search_web(query)

    @interceptor.intercept_tool(tool_name="calculator")
    def audited_calculate(expression: str) -> float:
        return agent.calculate(expression)

    @interceptor.intercept_llm()
    def audited_generate(prompt: str) -> str:
        return agent.generate_response(prompt)

    @interceptor.intercept_tool(tool_name="email_sender")
    def audited_send_email(to: str, subject: str, body: str) -> dict:
        return agent.send_email(to, subject, body)

    # Execute audited operations
    print("Executing audited operations...\n")

    operations = [
        ("search", lambda: audited_search("Python programming")),
        ("calculate", lambda: audited_calculate("123 * 456")),
        ("generate", lambda: audited_generate("Explain quantum computing")),
        ("search", lambda: audited_search("Machine learning tutorials")),
        ("generate", lambda: audited_generate("My password is secret123")),  # Will trigger finding
    ]

    for op_name, op_func in operations:
        print(f"  → Executing: {op_name}")
        try:
            result = op_func()
            print(f"    ✓ Success: {str(result)[:50]}...")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Try error handling
    print("\n  → Testing error handling...")
    try:
        # This will likely fail (20% chance per call, try multiple times)
        for i in range(5):
            try:
                audited_send_email("user@example.com", "Test", "Hello!")
                print(f"    ✓ Email {i+1} sent successfully")
            except ConnectionError:
                print(f"    ✗ Email {i+1} failed (expected)")
    except Exception as e:
        print(f"    ✗ Unexpected error: {e}")

    # Generate report
    print("\n" + "=" * 60)
    print("Generating Audit Report...")
    print("=" * 60 + "\n")

    report = engine.generate_report()
    reporter = ConsoleReporter(use_colors=True)
    print(reporter.generate(report))

    print("\n💡 Key Benefits of Interceptor Pattern:")
    print("   • Zero code changes to existing agent logic")
    print("   • Automatic timing and error tracking")
    print("   • Consistent audit trail across all operations")
    print("   • Easy to add/remove without affecting core functionality")


if __name__ == "__main__":
    main()
