#!/usr/bin/env python3
"""
Direct style testing - simulate agent responses and improve them
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.response_formatter import ResponseFormatter
from cite_agent.response_enhancer import ResponseEnhancer


def test_response_improvements():
    """Test how we can improve responses to be more pleasant"""

    test_cases = [
        {
            'query': 'Hey!',
            'current': 'Hello. How can I assist you today?',
            'better': 'Hi there! Ready to help - what can I dig into for you?',
        },
        {
            'query': 'List Python files',
            'current': 'Found files: main.py, utils.py, test.py',
            'better': 'I found 3 Python files in your project:\n\n• main.py\n• utils.py  \n• test.py\n\nWant me to show you what\'s in any of these?',
        },
        {
            'query': 'What does this code do?',
            'current': 'This code defines a function that processes data.',
            'better': 'This code processes data by:\n\n• Validating the input format\n• Transforming it to the right structure\n• Saving results to the database\n\nWant me to walk through any specific part?',
        },
        {
            'query': 'Thanks!',
            'current': 'You are welcome.',
            'better': 'Happy to help! Let me know if you need anything else.',
        },
    ]

    print("=" * 80)
    print("RESPONSE STYLE COMPARISON")
    print("Current vs What We Want")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['query']}")
        print("=" * 80)

        print(f"\n❌ CURRENT (Generic/Robotic):")
        print(f"   \"{test['current']}\"")

        print(f"\n✅ BETTER (Pleasant/Stylish):")
        print(f"   \"{test['better']}\"")

        print(f"\nWhy Better is Better:")
        if 'Hi there!' in test['better'] or 'Happy' in test['better']:
            print("   • More warm and friendly")
        if '•' in test['better']:
            print("   • Elegant formatting with bullets")
        if 'Want me to' in test['better'] or 'Let me know' in test['better']:
            print("   • Anticipatory - offers to help more")
        if len(test['better'].split()) > len(test['current'].split()) * 1.5:
            print("   • More context and helpful detail")

    print(f"\n{'='*80}")
    print("KEY DIFFERENCES")
    print("=" * 80)
    print("""
What makes responses PLEASANT and STYLISH:

1. WARM & FRIENDLY
   ❌ "How can I assist you today?"
   ✅ "Ready to help - what can I dig into for you?"

2. NATURAL & CONVERSATIONAL
   ❌ "I have located 3 files"
   ✅ "I found 3 files in your project"

3. ELEGANT FORMATTING
   ❌ "Found: file1, file2, file3"
   ✅ "I found 3 files:
       • file1
       • file2
       • file3"

4. ANTICIPATORY
   ❌ [Just answers, nothing more]
   ✅ "Want me to show you what's in any of these?"

5. CONTEXTUAL & HELPFUL
   ❌ "The function processes data"
   ✅ "This processes data by: [explains HOW] Want me to walk through it?"

6. PERSONALITY
   ❌ Cold, formal, robotic
   ✅ Warm, helpful, feels like talking to a smart friend
    """)


if __name__ == "__main__":
    test_response_improvements()
