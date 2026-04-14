def score_idea(text: str) -> int:

    text = text.lower()

    score = 50



    weights = {

        "ai": 10,

        "automation": 10,

        "product": 8,

        "bundle": 6,

        "tiktok": 7,

        "shorts": 7,

        "youtube": 6,

        "research": 5,

        "learning": 4,

        "templates": 8,

        "faceless": 6,

        "digital": 5,

        "monetization": 10,

        "cash": 8,

        "viral": 7

    }



    for key, value in weights.items():

        if key in text:

            score += value



    return min(score, 100)





def score_feedback(clicks: int = 0, saves: int = 0, conversions: int = 0, revenue: float = 0.0) -> int:

    score = 0

    score += min(clicks // 10, 20)

    score += min(saves * 2, 20)

    score += min(conversions * 8, 40)

    score += min(int(revenue // 10), 20)

    return min(score, 100)









