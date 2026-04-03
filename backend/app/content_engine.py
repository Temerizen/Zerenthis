def build_script(item):
    topic = item.get("topic", "")
    buyer = item.get("buyer", "")
    promise = item.get("promise", "")

    script = f"""
Today we are breaking down {topic}.

If you are {buyer}, this can help you {promise}.

Step 1: Understand the opportunity.
Step 2: Apply a simple execution strategy.
Step 3: Stay consistent and refine.

This is how you turn this into real results.
"""
    return script.strip()
