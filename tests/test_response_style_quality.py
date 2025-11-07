#!/usr/bin/env python3
"""
Response Style & Quality Testing
Tests if responses are ACTUALLY pleasant and stylish to read

Not just "does it work" but "would users ENJOY reading this?"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


def assess_style(response: str, query: str) -> dict:
    """
    Assess if response is pleasant and stylish

    Criteria:
    1. Natural/conversational (not robotic)
    2. Warm/friendly (not cold)
    3. Elegant formatting (not just functional)
    4. Anticipatory (answers next question too)
    5. Flows well (easy to read)
    """
    score = {
        'natural': 0,
        'warm': 0,
        'elegant': 0,
        'anticipatory': 0,
        'flow': 0,
        'overall': 0,
        'feedback': []
    }

    response_lower = response.lower()

    # Check 1: Natural/conversational
    robotic_phrases = [
        'processing', 'executing', 'computing',
        'i have analyzed', 'i have determined',
        'please note that', 'it should be noted'
    ]

    natural_phrases = [
        "i found", "here's", "looks like", "here are",
        "want me to", "would you like", "let me"
    ]

    if any(phrase in response_lower for phrase in robotic_phrases):
        score['natural'] = 0.3
        score['feedback'].append("❌ Sounds robotic")
    elif any(phrase in response_lower for phrase in natural_phrases):
        score['natural'] = 0.9
        score['feedback'].append("✅ Natural tone")
    else:
        score['natural'] = 0.6

    # Check 2: Warm/friendly
    cold_phrases = [
        'you must', 'you should', 'it is required',
        'error:', 'failed', 'unable to'
    ]

    warm_phrases = [
        'happy to', 'glad to', "i'd be happy",
        'sure!', 'absolutely', 'of course'
    ]

    if any(phrase in response_lower for phrase in cold_phrases):
        score['warm'] = 0.3
        score['feedback'].append("❌ Sounds cold/formal")
    elif any(phrase in response_lower for phrase in warm_phrases):
        score['warm'] = 0.9
        score['feedback'].append("✅ Warm and friendly")
    else:
        score['warm'] = 0.6

    # Check 3: Elegant formatting
    has_bullets = '•' in response or '- ' in response
    has_sections = '\n\n' in response
    has_emphasis = '**' in response

    if has_bullets and has_sections:
        score['elegant'] = 0.9
        score['feedback'].append("✅ Elegant formatting")
    elif has_bullets or has_sections:
        score['elegant'] = 0.7
        score['feedback'].append("⚠️ Good formatting, could be more elegant")
    else:
        score['elegant'] = 0.4
        score['feedback'].append("❌ Plain formatting")

    # Check 4: Anticipatory (offers to help more)
    anticipatory_phrases = [
        'want me to', 'would you like', 'i can also',
        'need me to', 'should i', 'want to see'
    ]

    if any(phrase in response_lower for phrase in anticipatory_phrases):
        score['anticipatory'] = 0.9
        score['feedback'].append("✅ Anticipates next steps")
    else:
        score['anticipatory'] = 0.3
        score['feedback'].append("❌ Not anticipatory")

    # Check 5: Flow (readability)
    sentences = response.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

    # Good flow: 10-20 words per sentence on average
    if 10 <= avg_sentence_length <= 20:
        score['flow'] = 0.9
        score['feedback'].append("✅ Good flow")
    elif avg_sentence_length < 5:
        score['flow'] = 0.5
        score['feedback'].append("⚠️ Sentences too choppy")
    elif avg_sentence_length > 30:
        score['flow'] = 0.5
        score['feedback'].append("⚠️ Sentences too long")
    else:
        score['flow'] = 0.7

    # Overall score (weighted)
    score['overall'] = (
        score['natural'] * 0.25 +
        score['warm'] * 0.20 +
        score['elegant'] * 0.20 +
        score['anticipatory'] * 0.20 +
        score['flow'] * 0.15
    )

    return score


async def test_style_quality():
    """Test actual response style and quality"""
    agent = EnhancedNocturnalAgent()

    test_queries = [
        # Simple greeting
        "Hey!",

        # Request for help
        "Can you help me find Python files?",

        # Information request
        "What files are in this directory?",

        # Follow-up question
        "Tell me more about the first one",

        # Thanks
        "Thanks for the help!",
    ]

    print("=" * 80)
    print("RESPONSE STYLE & QUALITY TEST")
    print("Checking if responses are pleasant and stylish")
    print("=" * 80)

    total_score = 0
    count = 0

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        try:
            request = ChatRequest(question=query, user_id="style_test")
            response = await agent.process_request(request)

            print(f"\n📝 RESPONSE:")
            print(response.response)
            print(f"\n📊 STYLE ASSESSMENT:")

            style_score = assess_style(response.response, query)

            print(f"Overall Style Score: {style_score['overall']:.2f}")
            print(f"- Natural: {style_score['natural']:.2f}")
            print(f"- Warm: {style_score['warm']:.2f}")
            print(f"- Elegant: {style_score['elegant']:.2f}")
            print(f"- Anticipatory: {style_score['anticipatory']:.2f}")
            print(f"- Flow: {style_score['flow']:.2f}")

            print(f"\nFeedback:")
            for feedback in style_score['feedback']:
                print(f"  {feedback}")

            # Judge if it's actually good
            if style_score['overall'] >= 0.80:
                print("\n✅ This response is ACTUALLY GOOD!")
            elif style_score['overall'] >= 0.70:
                print("\n⚠️ This response is acceptable but not great")
            else:
                print("\n❌ This response needs improvement")

            total_score += style_score['overall']
            count += 1

        except Exception as e:
            print(f"\n❌ Error: {e}")

    await agent.close()

    # Overall assessment
    avg_score = total_score / count if count > 0 else 0

    print(f"\n{'='*80}")
    print("OVERALL STYLE QUALITY")
    print("=" * 80)
    print(f"Average Style Score: {avg_score:.2f}")

    if avg_score >= 0.80:
        print("\n✅ Responses are PLEASANT and STYLISH!")
        return True
    elif avg_score >= 0.70:
        print("\n⚠️ Responses are OK but not delightful")
        return False
    else:
        print("\n❌ Responses need significant style improvement")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_style_quality())
    sys.exit(0 if result else 1)
