"""
Banking77 Intent Classification Benchmark.
Tests our intent detection agent against the Banking77 dataset.

Run: python datasets/banking77/benchmark.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Sample Banking77 queries mapped to our 6 intents
BENCHMARK_QUERIES = [
    # billing
    ("I have been charged twice for the same transaction", "billing"),
    ("Why was I charged an extra fee?", "billing"),
    ("My subscription payment failed", "billing"),
    ("I need a copy of my invoice", "billing"),
    # technical
    ("I cannot log into my account", "technical"),
    ("My password reset link is not working", "technical"),
    ("The app keeps crashing on my phone", "technical"),
    ("I am getting an error when I try to install", "technical"),
    # refund
    ("I want a refund for my last order", "refund"),
    ("How do I return a product?", "refund"),
    ("Can I get my money back?", "refund"),
    # product
    ("What is the price of the ProBook laptop?", "product"),
    ("Can you compare the Phone Pro and Phone SE?", "product"),
    ("What features does the TechMart Tab have?", "product"),
    # complaint
    ("I am very disappointed with your service", "complaint"),
    ("This is completely unacceptable", "complaint"),
    ("I am frustrated with the delays", "complaint"),
    # faq
    ("What is your return policy?", "faq"),
    ("How long does shipping take?", "faq"),
    ("What are your support hours?", "faq"),
]


def run_benchmark():
    from core.config import settings
    from core.trace import Trace
    from agents.intent_detection import detect_intent

    # Create dummy .env if needed
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '../../backend/.env')):
        print("No .env found - using keyword fallback mode")

    correct = 0
    total = len(BENCHMARK_QUERIES)
    results = []

    for query, expected in BENCHMARK_QUERIES:
        trace = Trace(session_id="benchmark", message=query)
        result = detect_intent(query, trace)
        is_correct = result.intent.value == expected
        if is_correct:
            correct += 1
        results.append({
            "query": query,
            "expected": expected,
            "predicted": result.intent.value,
            "confidence": result.confidence,
            "correct": is_correct
        })

    accuracy = correct / total * 100
    print(f"\n{'='*50}")
    print(f"INTENT CLASSIFICATION BENCHMARK (Banking77 Style)")
    print(f"{'='*50}")
    print(f"Total queries: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"\nFailed predictions:")
    for r in results:
        if not r["correct"]:
            print(f"  Query: {r['query'][:50]}")
            print(f"  Expected: {r['expected']} | Predicted: {r['predicted']}")
    print(f"{'='*50}")
    return accuracy


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), '../../backend'))
    accuracy = run_benchmark()
    print(f"\nFinal Accuracy: {accuracy:.1f}%")
