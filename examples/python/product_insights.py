"""Summarise what shoppers say about one Kohl's product: ratings, sub-ratings and Q&A.

    python product_insights.py 5008379

The productID is the `webID` from a search result.
"""

import argparse

from client import get, review_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("product_id")
    parser.add_argument("--questions", type=int, default=5)
    args = parser.parse_args()

    reviews = get("/product-reviews", productID=args.product_id, limit=5)["response"]
    stats = review_stats(reviews)
    total = stats.get("TotalReviewCount") or 0
    print(f"{total} ratings, average {stats.get('AverageOverallRating', 0):.2f} out of 5")
    for bucket in sorted(stats.get("RatingDistribution") or [], key=lambda b: -b["RatingValue"]):
        share = bucket["Count"] / total if total else 0
        print(f"  {bucket['RatingValue']} stars  {bucket['Count']:>6}  {share:>5.1%}")
    print(f"  recommended {stats.get('RecommendedCount')}, not recommended {stats.get('NotRecommendedCount')}")

    # Sub-ratings (fit, comfort, quality...) have IDs with a suffix, such as Fit_22.
    averages = stats.get("SecondaryRatingsAverages") or {}
    for rating_id in stats.get("SecondaryRatingsAveragesOrder") or []:
        item = averages.get(rating_id) or {}
        print(f"  {rating_id.split('_')[0]:<12} {item.get('AverageRating', 0):.2f} / {item.get('ValueRange')}")

    # Questions list their answer IDs; the answers themselves are under Includes.Answers.
    qna = get("/product-qnas", productID=args.product_id, limit=args.questions)["response"]
    answers = (qna.get("Includes") or {}).get("Answers") or {}
    print(f"\n{qna['TotalResults']} questions")
    for question in qna["Results"]:
        print(f"Q: {question['QuestionSummary']}")
        for answer_id in question.get("AnswerIds") or []:
            answer = answers.get(answer_id)
            if answer:
                print(f"   A: {answer['AnswerText'][:160]}")


if __name__ == "__main__":
    main()
