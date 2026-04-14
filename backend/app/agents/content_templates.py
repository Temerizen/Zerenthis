from pathlib import Path

YOUTUBE_SCRIPT_TEMPLATE = """TITLE: {title}

HOOK:
{hook}

OPENING:
Today we are diving into: {topic}

CORE POINTS:
1. {point1}
2. {point2}
3. {point3}

CTA:
Subscribe for more high-leverage ideas, systems, and execution.

NOTES:
{notes}
"""

SOCIAL_POST_TEMPLATE = """POST TITLE: {title}

{body}

CALL TO ACTION:
Follow for more.
"""

PDF_TEMPLATE = """# {title}

## Topic
{topic}

## Summary
{summary}

## Key Insights
- {point1}
- {point2}
- {point3}

## Action Steps
{action_steps}
"""

EMAIL_TEMPLATE = """Subject: {title}

Hello,

{body}

Best,
SemantiqAI
"""

THUMBNAIL_TEMPLATE = """THUMBNAIL CONCEPT
Title: {title}
Primary Hook: {hook}
Visual Direction: {visual}
Style Notes: {style}
"""

