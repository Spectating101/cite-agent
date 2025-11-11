# Cite-Agent: Your Local AI Research Assistant

[![Version](https://img.shields.io/badge/version-1.4.1-blue.svg)](https://pypi.org/project/cite-agent/)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> **Stop switching between 10 different tools. Ask questions in plain English, get instant answers.**

**Cite-Agent** is your local AI assistant that reads your files, searches academic papers, and gets financial data — all through natural conversation. Built for researchers who need to analyze data, review literature, and manage files without leaving their flow.

**What makes it unique**: ChatGPT can't read your local files. RStudio can't search academic papers. Cite-Agent does both, plus financial data integration, in one conversation.

## 🌟 Features

### 📂 **Read Your Local Files** (ChatGPT can't do this)
Ask questions about your data without writing code.

```
You: show me my data.csv
Agent: [Displays first 100 lines, detects 9 columns: Date, Ticker, Price, Volume...]

You: what's the average price?
Agent: $45.23 (calculated from 1,247 rows)

You: find my cm522 project
Agent: Found: /home/user/Downloads/cm522-main/
```

**Supported formats**: CSV, R scripts, Python files, Jupyter notebooks
**Privacy**: Everything stays on your machine
**No copy-pasting**: Direct file system access

### 🔬 **Academic Research**
Search papers across multiple databases with proper citations.

- Multi-source search (Semantic Scholar, OpenAlex, PubMed)
- **Full PDF reading and summarization**
- Citation verification and quality scoring
- DOI resolution and metadata extraction
- Automatic access to paywalled papers via Unpaywall
- **Citation Network Mapping** - Find foundational papers and research lineages
- **Smart Paper Comparison** - Compare methodologies and results side-by-side
- **Trend Analysis** - Track topic evolution and emerging areas

### 💰 **Financial Data Integration**
Get company metrics without hunting through EDGAR filings.

```
You: Tesla revenue
Agent: $96.77B (TTM)

You: what about Microsoft?
Agent: $245.12B (TTM)

You: which is bigger?
Agent: Microsoft's revenue is 2.5x larger than Tesla's
```

**Data sources**: FinSight API (SEC filings, real-time metrics)
**What you can ask**: Revenue, earnings, P/E ratio, growth rates, comparisons
**Context memory**: Remembers companies across questions

### 🧠 **Conversation Memory**
Context that actually works — no repeating yourself.

- Tracks up to 30,000 tokens of conversation
- Maintains file context across questions
- Resolves pronouns ("it", "that company", "those rows")
- Remembers your current directory and recent files

### 🗂️ **Natural Language File Management**
Navigate without memorizing terminal commands.

```
You: where am i?
Agent: /home/user/projects

You: list files here
Agent: [Shows directory contents intelligently]

You: go to Downloads
Agent: Now in: /home/user/Downloads
```

### 📤 **Enhanced Export Formats**
Export research in any format you need.

- BibTeX, RIS, EndNote XML
- Zotero JSON, Obsidian markdown
- Citation manager integration
- Clipboard support for instant citations

---

## 🆚 Why Choose Cite-Agent?

### **vs. ChatGPT/Claude Web Interfaces**
| Feature | ChatGPT/Claude | Cite-Agent |
|---------|----------------|------------|
| Read your local files | ❌ Can't access filesystem | ✅ Reads CSV, R, Python, Jupyter |
| Remember file context | ❌ Must copy-paste | ✅ Direct access, maintains context |
| Privacy | ⚠️ Data sent to cloud | ✅ Runs locally on your machine |
| Academic search | ⚠️ Generic web search | ✅ Multi-source academic databases |
| Financial data | ❌ No direct access | ✅ Real-time SEC filings via FinSight |

### **vs. RStudio/Jupyter Alone**
| Feature | RStudio/Jupyter | Cite-Agent |
|---------|-----------------|------------|
| Coding required | ⚠️ Must write code | ✅ Natural language queries |
| Academic paper search | ❌ No integration | ✅ Built-in multi-source search |
| Financial data | ❌ Manual lookup | ✅ Automatic SEC filing access |
| File navigation | ⚠️ Terminal commands | ✅ Plain English |
| Context memory | ❌ No conversation | ✅ 30,000 token memory |

### **vs. Google Scholar/Research Tools**
| Feature | Google Scholar | Cite-Agent |
|---------|----------------|------------|
| Read local data files | ❌ Web-only | ✅ Full filesystem access |
| Financial integration | ❌ Papers only | ✅ Academic + Financial combined |
| Conversational | ❌ Search box | ✅ Natural dialogue |
| Export formats | ⚠️ Limited | ✅ 7+ formats (BibTeX, RIS, Zotero, etc.) |

**The unique combination**: No competitor offers local file reading + academic search + financial data in one conversational interface.

---

## 🚀 Quick Start

### Installation

**Option 1: pipx (Recommended - handles PATH automatically)**
```bash
# Install pipx if you don't have it
pip install --user pipx
python3 -m pipx ensurepath

# Install cite-agent
pipx install cite-agent

# Ready to use (no PATH setup needed)
cite-agent --version
```

**Option 2: pip (requires PATH setup)**
```bash
# Install
pip install --user cite-agent

# Add to PATH (one-time setup)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Ready to use
cite-agent --version
```

**If cite-agent command not found:** Run `python3 -m cite_agent.cli` instead.

### Basic Usage

```bash
# Interactive mode (recommended)
cite-agent

# Example conversations:
> show me my data.csv
> what columns does it have?
> calculate the average price
> find recent papers on transformer models
> Tesla revenue
> compare that to Microsoft

# Single query mode
cite-agent "show me my thesis_data.csv"
cite-agent "find papers on ESG investing"
cite-agent "what's Apple's P/E ratio?"

# File exploration
cite-agent "find my cm522 project"
cite-agent "list files in Downloads"
cite-agent "show me calculate_betas.R"

# Get help
cite-agent --help
cite-agent --tips
```

### Python API

```python
import asyncio
from cite_agent import EnhancedNocturnalAgent, ChatRequest

async def main():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    request = ChatRequest(
        question="What is the current state of AI in healthcare?",
        user_id="user123",
        conversation_id="conv456"
    )
    
    response = await agent.process_request(request)
    print(response.response)
    print(f"Confidence: {response.confidence_score}")
    print(f"Tools used: {response.tools_used}")
    
    await agent.close()

asyncio.run(main())
```

---

## 💡 Real Use Cases

### **Use Case 1: Finance Homework** (15 minutes saved)
```
You: I need to calculate beta for Apple stock
Agent: I can help with that. Do you have returns data?

You: show me my data/returns.csv
Agent: [Displays file, detects columns: Date, AAPL, SPY, MSFT...]

You: calculate correlation between AAPL and SPY
Agent: Correlation: 0.73 (strong positive relationship)
```
**vs. Traditional workflow**: Google formula → Write pandas/R code → Debug → Run

### **Use Case 2: Literature Review** (30 minutes saved)
```
You: find recent papers on ESG investing performance
Agent: [Returns 5 key papers with summaries and citations]

You: what does the 2023 MIT study say?
Agent: [Summarizes: "ESG portfolios showed 2.1% higher risk-adjusted returns..."]

You: compare that to the Stanford paper
Agent: MIT focuses on long-term returns (10yr), Stanford examines short-term (3yr)
```
**vs. Traditional workflow**: Google Scholar → Open tabs → Read abstracts → Take notes

### **Use Case 3: Data Exploration** (10 minutes saved)
```
You: show me my thesis_data.csv
Agent: [Displays data, detects 12 columns, 1,247 rows]

You: any missing values?
Agent: Yes, 3 rows have missing Price values (rows 45, 127, 983)

You: show me those rows
Agent: [Displays the 3 problematic rows with context]
```
**vs. Traditional workflow**: Open RStudio → Load library → Write code → Run checks

### **Use Case 4: Company Analysis** (20 minutes saved)
```
You: compare revenue growth: Tesla, Ford, GM
Agent:
  Tesla: +18.8% YoY
  Ford: +11.2% YoY
  GM: +9.7% YoY
  Tesla is growing fastest.

You: what about their profit margins?
Agent: [Remembers context]
  Tesla: 23.1%
  Ford: 6.2%
  GM: 7.1%
```
**vs. Traditional workflow**: EDGAR filings → Extract numbers → Spreadsheet → Calculate

---

## 📖 Documentation

### Command Line Interface

#### Basic Commands

```bash
# Show version
cite-agent --version

# Interactive setup
cite-agent --setup

# Show tips
cite-agent --tips

# Check for updates
cite-agent --check-updates
```

#### Query Examples

**Local file analysis** (unique to Cite-Agent):
```bash
cite-agent "show me my data/returns.csv"
cite-agent "what's the average of column Price?"
cite-agent "any missing values in this dataset?"
cite-agent "find my thesis project"
cite-agent "show me calculate_betas.R and explain what it does"
```

**Academic research**:
```bash
cite-agent "find recent papers on transformer architecture"
cite-agent "compare methodologies in these 3 papers"
cite-agent "what's the citation count for BERT paper?"
cite-agent "find seminal papers on deep learning"
```

**Financial data**:
```bash
cite-agent "Apple revenue"
cite-agent "compare Tesla vs Ford profit margins"
cite-agent "Microsoft P/E ratio"
cite-agent "show me NVIDIA's YoY growth"
```

**Multi-language support**:
```bash
cite-agent "我的p值是0.05，這顯著嗎？"
cite-agent "找關於ESG投資的論文"
```

#### Runtime Controls

- Responses render immediately—there’s no artificial typing delay.
- Press `Ctrl+C` while the agent is thinking or streaming to interrupt and ask a different question on the spot.

### Python API Reference

#### EnhancedNocturnalAgent

The main agent class for programmatic access.

```python
class EnhancedNocturnalAgent:
    async def initialize(self, force_reload: bool = False)
    async def process_request(self, request: ChatRequest) -> ChatResponse
    async def process_request_streaming(self, request: ChatRequest)
    async def search_academic_papers(self, query: str, limit: int = 10) -> Dict[str, Any]
    async def get_financial_data(self, ticker: str, metric: str, limit: int = 12) -> Dict[str, Any]
    async def synthesize_research(self, paper_ids: List[str], max_words: int = 500) -> Dict[str, Any]
    async def close(self)
```

#### Data Models

```python
@dataclass
class ChatRequest:
    question: str
    user_id: str = "default"
    conversation_id: str = "default"
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatResponse:
    response: str
    tools_used: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    model: str = "enhanced-nocturnal-agent"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tokens_used: int = 0
    confidence_score: float = 0.0
    execution_results: Dict[str, Any] = field(default_factory=dict)
    api_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

#### Research
- `POST /api/search` - Search academic papers
- `POST /api/synthesize` - Synthesize research papers
- `POST /api/format` - Format citations

#### Financial Data
- `GET /v1/finance/calc/{ticker}/{metric}` - Get financial metrics
- `GET /v1/finance/kpis/{ticker}` - Get company KPIs
- `GET /v1/finance/reports/{ticker}` - Get financial reports

#### Analytics
- `GET /api/download/stats/summary` - Download statistics
- `GET /api/analytics/overview` - Usage overview
- `GET /api/analytics/users` - User statistics

#### Download Tracking
- `GET /api/download/windows` - Track Windows downloads
- `GET /api/download/macos` - Track macOS downloads
- `GET /api/download/linux` - Track Linux downloads

## 🔧 Configuration

### Environment Variables

```bash
# Authentication
NOCTURNAL_ACCOUNT_EMAIL=your@email.edu
NOCTURNAL_ACCOUNT_PASSWORD=your_password

# API Configuration
NOCTURNAL_API_URL=https://cite-agent-api-720dfadd602c.herokuapp.com
ARCHIVE_API_URL=https://cite-agent-api-720dfadd602c.herokuapp.com/api
FINSIGHT_API_URL=https://cite-agent-api-720dfadd602c.herokuapp.com/v1/finance

# Optional
NOCTURNAL_DEBUG=1  # Enable debug logging
NOCTURNAL_QUERY_LIMIT=25  # Default query limit
```

### Session Management

Sessions are automatically managed and stored in:
- **Linux/macOS**: `~/.nocturnal_archive/session.json`
- **Windows**: `%USERPROFILE%\.nocturnal_archive\session.json`

## 📊 Analytics & Monitoring

### User Tracking

The system automatically tracks:
- User registrations and logins
- Query history and usage patterns
- Token consumption and costs
- Response quality and citation accuracy

### Download Analytics

Track installer downloads across platforms:
- Windows, macOS, Linux downloads
- Geographic distribution (IP-based)
- Referrer tracking
- Download trends and patterns

### Dashboard Access

Access the analytics dashboard at:
```
https://cite-agent-api-720dfadd602c.herokuapp.com/dashboard
```

## 💰 Pricing

**Currently in Beta**: Free access while we gather feedback and improve.

### Future Pricing Plan
- **Academic/Student**: 300 NTD/month (~$10 USD)
  - Unlimited queries
  - All features included
  - Local file reading, academic search, financial data
  - Priority support
  - Educational institution verification required

**No credit card required during beta. Just install and use.**

### Why 300 NTD?
- **Less than one textbook**: Typical textbook costs 1,000-2,000 NTD
- **Saves hours per week**: 15-30 min saved per research task
- **Replace multiple tools**: Google Scholar + RStudio + Terminal + Excel
- **Privacy included**: Your data never leaves your machine

## 🛠️ Development

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/cite-agent.git
cd cite-agent

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Start development server
python -m cite_agent.dashboard
```

### Building from Source

```bash
# Build wheel
python setup.py bdist_wheel

# Install locally
pip install dist/cite_agent-1.0.5-py3-none-any.whl
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔒 Security & Privacy

### Data Protection
- All user data encrypted in transit and at rest
- JWT-based authentication with 30-day expiration
- No storage of sensitive personal information
- GDPR compliant data handling

### API Security
- Rate limiting per user tier
- Input validation and sanitization
- SQL injection prevention
- CORS protection

## 👥 Who Is This For?

### **Graduate Students**
- Analyze thesis data without writing code
- Search academic literature across multiple databases
- Get financial data for research projects
- Manage project files efficiently

### **Researchers & Academics**
- Quick data exploration and validation
- Literature reviews with proper citations
- Multi-file project management
- Context-aware research assistance

### **Finance Students**
- Company financial analysis and comparisons
- Quick SEC filing lookups
- Historical data access
- No more hunting through EDGAR

### **Anyone Who Works With Data**
- No coding required for simple analysis
- Natural language interface
- CSV, R, Python, Jupyter support
- Privacy-focused local execution

---

## 📈 Technical Specifications

### Performance
- **Response time**: ~1.7 seconds average
- **Backend capacity**: 86,400 queries/day
- **Conversation memory**: 30,000 token window
- **File preview**: First 100 lines automatically displayed
- **Context retention**: Remembers files and variables across questions

### Architecture
- **LLM backend**: Cerebras GPT-OSS-120B (100% test pass rate)
- **Multi-source APIs**: Semantic Scholar, OpenAlex, PubMed, FinSight
- **Caching**: DiskCache for offline mode
- **Async/await**: Non-blocking I/O for fast responses
- **Privacy**: All file operations local, no data uploaded

### Platform Support
- **Linux**: Full support
- **macOS**: Full support
- **Windows**: Via WSL (installer in development)
- **Python**: 3.8+ required

## 🐛 Troubleshooting

### Common Issues

#### CLI Hangs on Startup
```bash
# Clear session and reconfigure
rm -rf ~/.nocturnal_archive
cite-agent --setup
```

#### Authentication Errors
```bash
# Check credentials
cite-agent --setup

# Verify email format (must be academic)
# Valid: user@university.edu, student@ac.uk
# Invalid: user@gmail.com, user@company.com
```

#### API Connection Issues
```bash
# Check network connectivity
curl https://cite-agent-api-720dfadd602c.herokuapp.com/api/health

# Verify API keys
echo $NOCTURNAL_ACCOUNT_EMAIL
```

### Debug Mode

```bash
# Enable debug logging
export NOCTURNAL_DEBUG=1
cite-agent "your query"
```

### Support

- **Documentation**: [Full docs](https://docs.cite-agent.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cite-agent/issues)
- **Email**: support@cite-agent.com
- **Discord**: [Community Server](https://discord.gg/cite-agent)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAlex** for academic data
- **Semantic Scholar** for research papers
- **FinSight** for financial data
- **Cerebras** for GPT-OSS-120B inference
- **FastAPI** for the backend framework

---

## 🎯 The Bottom Line

**Stop switching between 10 tools. Cite-Agent combines:**
- ✅ Local file reading (CSV, R, Python, Jupyter)
- ✅ Academic paper search (multi-source)
- ✅ Financial data (SEC filings, real-time)
- ✅ Natural language interface
- ✅ Privacy-focused (runs locally)

**No competitor offers all of this in one conversational interface.**

**Try it now:**
```bash
pip install cite-agent
cite-agent
```

First question to ask: `"what can you do?"`

---

**Built for researchers who value their time.**
