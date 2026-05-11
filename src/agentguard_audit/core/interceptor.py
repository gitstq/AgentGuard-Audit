"""Interceptor for transparent agent monitoring."""

import functools
import time
from typing import Any, Callable, Dict, Optional

from .audit_engine import AuditEngine


class AgentInterceptor:
    """
    Interceptor for transparent integration with AI Agents.

    Provides decorators and context managers for zero-intrusion auditing.
    """

    def __init__(self, audit_engine: AuditEngine):
        """
        Initialize interceptor.

        Args:
            audit_engine: The audit engine to use for logging
        """
        self.audit_engine = audit_engine

    def intercept_tool(
        self,
        tool_name: Optional[str] = None,
        capture_output: bool = True,
    ) -> Callable:
        """
        Decorator to intercept and audit tool calls.

        Args:
            tool_name: Optional name override for the tool
            capture_output: Whether to capture tool output

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                tool = tool_name or func.__name__

                try:
                    result = func(*args, **kwargs)
                    latency = (time.time() - start_time) * 1000

                    self.audit_engine.audit_tool_call(
                        tool_name=tool,
                        tool_input={"args": args, "kwargs": kwargs},
                        tool_output=result if capture_output else "<captured>",
                        latency_ms=latency,
                    )

                    return result

                except Exception as e:
                    latency = (time.time() - start_time) * 1000

                    self.audit_engine.audit_event(
                        event_type="tool_call_error",
                        input_data={"tool": tool, "args": args, "kwargs": kwargs},
                        output_data={"error": str(e), "error_type": type(e).__name__},
                        metadata={"tool_name": tool, "latency_ms": latency},
                    )
                    raise

            return wrapper
        return decorator

    def intercept_llm(
        self,
        capture_prompt: bool = True,
        capture_response: bool = True,
    ) -> Callable:
        """
        Decorator to intercept and audit LLM calls.

        Args:
            capture_prompt: Whether to capture the prompt
            capture_response: Whether to capture the response

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                # Extract prompt from args/kwargs
                prompt = ""
                if args:
                    prompt = str(args[0])
                elif "prompt" in kwargs:
                    prompt = kwargs["prompt"]
                elif "messages" in kwargs:
                    prompt = str(kwargs["messages"])

                try:
                    result = func(*args, **kwargs)
                    latency = (time.time() - start_time) * 1000

                    # Extract response and token count
                    response = ""
                    token_count = 0

                    if isinstance(result, str):
                        response = result
                    elif isinstance(result, dict):
                        response = result.get("content", str(result))
                        token_count = result.get("usage", {}).get("total_tokens", 0)
                    else:
                        response = str(result)

                    self.audit_engine.audit_llm_request(
                        prompt=prompt if capture_prompt else "<captured>",
                        response=response if capture_response else "<captured>",
                        token_count=token_count,
                        latency_ms=latency,
                    )

                    return result

                except Exception as e:
                    latency = (time.time() - start_time) * 1000

                    self.audit_engine.audit_error(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        context={"prompt": prompt if capture_prompt else "<captured>"},
                    )
                    raise

            return wrapper
        return decorator

    def intercept_function(
        self,
        event_type: str,
        metadata_extractor: Optional[Callable] = None,
    ) -> Callable:
        """
        Generic decorator to intercept any function.

        Args:
            event_type: Type of event to log
            metadata_extractor: Optional function to extract metadata

        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                metadata = {}
                if metadata_extractor:
                    try:
                        metadata = metadata_extractor(*args, **kwargs)
                    except Exception:
                        pass

                try:
                    result = func(*args, **kwargs)
                    latency = (time.time() - start_time) * 1000

                    metadata["latency_ms"] = latency
                    metadata["success"] = True

                    self.audit_engine.audit_event(
                        event_type=event_type,
                        input_data={"args": str(args), "kwargs": str(kwargs)},
                        output_data={"result": str(result)[:1000]},
                        metadata=metadata,
                    )

                    return result

                except Exception as e:
                    latency = (time.time() - start_time) * 1000

                    metadata["latency_ms"] = latency
                    metadata["success"] = False
                    metadata["error"] = str(e)

                    self.audit_engine.audit_event(
                        event_type=f"{event_type}_error",
                        input_data={"args": str(args), "kwargs": str(kwargs)},
                        output_data={"error": str(e), "error_type": type(e).__name__},
                        metadata=metadata,
                    )
                    raise

            return wrapper
        return decorator


class InterceptorContext:
    """Context manager for temporary interception."""

    def __init__(self, audit_engine: AuditEngine, event_type: str = "context_block"):
        """
        Initialize context.

        Args:
            audit_engine: The audit engine to use
            event_type: Type of event for the context block
        """
        self.audit_engine = audit_engine
        self.event_type = event_type
        self.event_id: Optional[str] = None

    def __enter__(self):
        """Enter context."""
        event = self.audit_engine.audit_event(
            event_type=f"{self.event_type}_start",
            input_data={},
            metadata={"context": "entered"},
        )
        self.event_id = event.event_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type is not None:
            self.audit_engine.audit_error(
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                context={"context": self.event_type},
            )
        else:
            self.audit_engine.audit_event(
                event_type=f"{self.event_type}_end",
                input_data={},
                metadata={"context": "exited", "parent_event_id": self.event_id},
            )
        return False  # Don't suppress exceptions
