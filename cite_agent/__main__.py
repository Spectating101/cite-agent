#!/usr/bin/env python3
"""
Entry point for python -m cite_agent
Allows running: python3 -m cite_agent
"""

from cite_agent.enhanced_ai_agent import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

