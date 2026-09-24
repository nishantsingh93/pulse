import hashlib
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
VERSION = "target-vader-0.1"


def classify(text: str, target: str) -> dict:
    digest = hashlib.sha256(text.encode()).hexdigest()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    target_terms = [t.casefold().lstrip("#") for t in re.findall(r'[\w#-]+', target)]
    relevant = [s for s in sentences if all(t in s.casefold() for t in target_terms)]
    base = {"target": target, "text_hash": digest, "model_version": VERSION}
    if not relevant:
        return {**base, "label": "unknown", "score": None, "abstention_reason": "target_not_in_text", "evidence_text": None}
    scores = [analyzer.polarity_scores(s)["compound"] for s in relevant]
    if max(scores) >= .35 and min(scores) <= -.35:
        return {**base, "label": "unknown", "score": None, "abstention_reason": "mixed_polarity", "evidence_text": relevant[0][:500]}
    value = sum(scores) / len(scores)
    if abs(value) < .35:
        return {**base, "label": "unknown", "score": round(value * 1000), "abstention_reason": "low_confidence", "evidence_text": relevant[0][:500]}
    return {**base, "label": "positive" if value > 0 else "negative", "score": round(value * 1000), "abstention_reason": None, "evidence_text": relevant[0][:500]}
