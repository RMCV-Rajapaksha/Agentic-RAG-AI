from llama_index.core.tools import FunctionTool

def multiply(a: int, b: int) -> int:
    """
    Multiplies two integers and returns the result.
    Use this tool for any multiplication calculation.
    """
    print(f"🛠️  Calling multiply tool with: a={a}, b={b}")
    return a * b

# Wrap the function in a LlamaIndex FunctionTool
# This makes it compatible with the agent framework.
multiply_tool = FunctionTool.from_defaults(
    fn=multiply,
    name="integer_multiplier", # Give it a unique name
)
