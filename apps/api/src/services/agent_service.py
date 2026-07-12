from statistics import mean

from src.services.ai_service import ai_service


def keyword_analysis(product, seeds: list[str]) -> dict:
    base = ai_service.extract_keywords(f"{product.title} {product.description} {' '.join(seeds)}", 30)
    items = []
    for index, keyword in enumerate(base):
        intent = "транзакционный" if index < 10 else "информационный"
        score = max(20, 100 - index * 3)
        items.append({"keyword": keyword, "intent": intent, "growth_score": score, "priority": "high" if score >= 70 else "medium"})
    return {"keywords": items, "recommended_core": [x["keyword"] for x in items[:12]]}


def competitor_analysis(product, competitors: list[dict]) -> dict:
    if not competitors:
        competitors = [
            {"title": "Конкурент A", "price": max(1, product.price * 0.92), "rating": 4.6, "reviews": 320},
            {"title": "Конкурент B", "price": max(1, product.price * 1.08), "rating": 4.8, "reviews": 780},
            {"title": "Конкурент C", "price": max(1, product.price * 0.98), "rating": 4.4, "reviews": 190},
        ]
    prices = [float(x.get("price", 0)) for x in competitors if float(x.get("price", 0)) > 0]
    avg_price = mean(prices) if prices else product.price
    position = "ниже рынка" if product.price < avg_price * 0.95 else "выше рынка" if product.price > avg_price * 1.05 else "в рынке"
    return {
        "competitors_count": len(competitors),
        "average_price": round(avg_price, 2),
        "price_position": position,
        "recommended_price": round(avg_price * 0.99, 2),
        "content_gaps": ["Добавить инфографику с выгодами", "Усилить первый экран", "Раскрыть сценарии использования"],
        "competitors": competitors,
    }


def review_reply(rating: int, text: str, product_name: str) -> dict:
    if rating >= 4:
        reply = f"Спасибо за высокую оценку! Рады, что {product_name} вам понравился. Будем ждать вас снова."
    elif rating == 3:
        reply = f"Спасибо за обратную связь. Нам важно улучшать {product_name}. Напишите, пожалуйста, что именно можно сделать лучше."
    else:
        reply = f"Нам жаль, что {product_name} не оправдал ожиданий. Пожалуйста, напишите в чат продавца — мы постараемся быстро решить вопрос."
    return {"reply": reply, "sentiment": "positive" if rating >= 4 else "neutral" if rating == 3 else "negative", "requires_manager": rating <= 2}


def question_reply(question: str, product_name: str) -> dict:
    return {"reply": f"Спасибо за вопрос о товаре «{product_name}». По имеющейся информации: {question.strip()} — уточните нужную характеристику, и мы дадим точный ответ.", "confidence": 0.72}


def ads_recommendation(product, daily_budget: float, cpc: float, conversion_rate: float, margin_percent: float) -> dict:
    clicks = daily_budget / cpc
    expected_orders = clicks * conversion_rate
    max_cpc = product.price * (margin_percent / 100) * conversion_rate * 0.55
    action = "increase" if cpc < max_cpc * 0.8 else "decrease" if cpc > max_cpc else "hold"
    return {
        "expected_clicks": round(clicks, 1),
        "expected_orders": round(expected_orders, 2),
        "max_profitable_cpc": round(max_cpc, 2),
        "action": action,
        "recommendations": ["Отключать запросы без заказов после накопления статистики", "Разделять кампании по маржинальности", "Повышать ставку только при наличии остатков"],
    }
