#!/bin/bash
# Test suite for improved tool selection

echo "🧪 TESTING IMPROVED TOOL SELECTION"
echo "=================================="
echo ""

# Setup
export $(cat .env.local | grep -v '^#' | xargs)
export NOCTURNAL_FUNCTION_CALLING=1

# Test 1: Data file with explicit request
echo "📝 Test 1: 'load sample_data.csv and calculate mean'"
rm -f ~/.nocturnal_archive/session.json
timeout 30 bash -c 'echo -e "load sample_data.csv and calculate mean\nquit" | cite-agent 2>&1' | grep -E "(🎯.*forcing|🔧 load|Mean:|list_directory)" | head -5
echo ""

# Test 2: Implicit data request
echo "📝 Test 2: 'analyze sample_data.csv'"
rm -f ~/.nocturnal_archive/session.json
timeout 30 bash -c 'echo -e "analyze sample_data.csv\nquit" | cite-agent 2>&1' | grep -E "(🎯.*forcing|🔧 load|Mean:|list_directory)" | head -5
echo ""

# Test 3: Statistics request with filename
echo "📝 Test 3: 'what is the mean of sample_data.csv'"
rm -f ~/.nocturnal_archive/session.json
timeout 30 bash -c 'echo -e "what is the mean of sample_data.csv\nquit" | cite-agent 2>&1' | grep -E "(🎯.*forcing|🔧 load|Mean:|list_directory)" | head -5
echo ""

# Test 4: File browsing (should NOT force load_dataset)
echo "📝 Test 4: 'what files are in this directory' (should use list_directory)"
rm -f ~/.nocturnal_archive/session.json
timeout 30 bash -c 'echo -e "what files are in this directory\nquit" | cite-agent 2>&1' | grep -E "(🎯.*forcing|🔧 list|list_directory)" | head -5
echo ""

# Test 5: Read specific non-data file (should NOT force load_dataset)
echo "📝 Test 5: 'show me README.md' (should use read_file)"
rm -f ~/.nocturnal_archive/session.json
timeout 30 bash -c 'echo -e "show me README.md\nquit" | cite-agent 2>&1' | grep -E "(🎯.*forcing|🔧 read|read_file|load_dataset)" | head -5
echo ""

echo "✅ TESTING COMPLETE"
