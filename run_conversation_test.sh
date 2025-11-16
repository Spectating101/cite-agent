#!/bin/bash
# Run conversation test with proper environment

export USE_LOCAL_KEYS=true
export CEREBRAS_API_KEY=csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj
export NOCTURNAL_FUNCTION_CALLING=1
export NOCTURNAL_DEBUG=0  # Reduce noise

python3 test_llm_conversation.py 2>&1 | tee conversation_output.txt
