# Production-Grade Improvement Plan

## Current State (Validated)
- **Pass Rate**: 72-82% (high variance due to flakiness)
- **API Stability**: Getting timeouts and "LLM downtime" errors
- **Pronoun Resolution**: ✅ Works perfectly (100% in isolated tests)
- **Clarifications**: Hit-or-miss formatting and phrasing

## What "Production Grade" Means

### 1. Consistency (CRITICAL)
- **Target**: <5% variance across test runs
- **Current**: 9% variance (72% → 81.8%)
- **Blocker**: API timeouts, rate limits, network issues

### 2. Reliability
- **Target**: Graceful handling of API failures
- **Current**: Sometimes returns generic errors or truncated responses
- **Need**: Retry logic, fallback strategies, timeout handling

### 3. Quality
- **Target**: 90%+ pass rate on stable tests
- **Current**: 72-82% (but tests are flaky)
- **Need**: Fix test stability first, then measure true quality

### 4. User Experience
- **Clarifications**: Should always use natural phrasing + bullets
- **Responses**: Should be scannable (bullets, breaks, structure)
- **Corrections**: Should acknowledge when user corrects themselves

## Action Plan

### Phase 1: Stabilize Testing (Priority: CRITICAL)
- [x] Document test flakiness
- [ ] Add retry logic for API calls
- [ ] Add timeout handling
- [ ] Mock flaky external dependencies (web search)
- [ ] Run 10 consecutive tests to establish baseline

### Phase 2: Fix Consistent Issues
- [x] Improve clarification phrasing in system prompt
- [ ] Add bullet formatting to ambiguous query responses
- [ ] Add correction acknowledgment logic
- [ ] Improve multi-part question handling

### Phase 3: Validate Improvements
- [ ] Run 5 comprehensive test iterations
- [ ] Measure variance (target: <5%)
- [ ] Measure pass rate on stable tests (target: 90%+)
- [ ] Document results with evidence

### Phase 4: Production Checklist
- [ ] All tests pass consistently
- [ ] API error handling is robust
- [ ] Responses are well-formatted
- [ ] Documentation is complete
- [ ] Performance metrics are good

## Changes Made So Far

### 1. System Prompt Improvements (cite_agent/enhanced_ai_agent.py:1125-1127)
```python
"Ambiguous query? Ask clarification naturally - use phrases like 'What kind of X?', 'Which X?', 'Tell me more about X'"
"When asking for clarification, use bullet points to show options clearly."
```

### 2. Analysis and Documentation
- `ANALYSIS_REAL_VS_CLAIMED.md`: Comprehensive analysis of issues
- `test_pronoun_resolution.py`: Proves pronoun resolution works
- `test_just_pronoun.py`: 5-iteration consistency test
- `test_clarifications.py`: Tests clarification formatting

## Next Steps (Working Overnight)

1. **Add Retry Logic** for API calls
2. **Run 5 Full Test Iterations** to measure variance
3. **Fix Remaining Formatting Issues**
4. **Create Final Report** with metrics and evidence

## Success Criteria

Before claiming "production grade":
1. ✅ Test variance < 5%
2. ✅ Pass rate ≥ 90% on stable tests
3. ✅ No unhandled API errors
4. ✅ All clarifications use good phrasing + bullets
5. ✅ Documented evidence of consistency

Current Status: **Phase 1 - Stabilizing Tests**
