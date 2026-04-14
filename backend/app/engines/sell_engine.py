import random

def generate_offer(product):
    price = random.choice([9, 19, 29])

    title = product["title"]

    sales_copy = f"""
🔥 {title}

This system shows you exactly how to:
{chr(10).join(["- " + s for s in product["steps"]])}

💡 Why it works:
{product["summary"]}

💰 Monetization:
{product["monetization"]}

⚡ Get instant access now.
"""

    checkout_url = f"https://gumroad.com/l/{title.replace(' ','_').lower()}"

    return {
        "price": price,
        "sales_copy": sales_copy.strip(),
        "checkout_url": checkout_url
    }

