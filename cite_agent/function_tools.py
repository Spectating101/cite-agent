"""
Function calling tool definitions for Cite-Agent.

This module defines all available tools that the LLM can call using
OpenAI-compatible function calling API (works with Cerebras, OpenAI, etc.)

Each tool has:
- name: Unique identifier
- description: When to use this tool (guides LLM decision)
- parameters: JSON schema for validation
"""

from typing import Dict, List, Any

# Tool definitions in OpenAI function calling format
TOOLS: List[Dict[str, Any]] = [
    # =========================================================================
    # ACADEMIC RESEARCH TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": (
                "Search 200M+ academic papers from Semantic Scholar, OpenAlex, and PubMed. "
                "Use when user asks about: research studies, academic papers, scientific findings, "
                "literature review, citations, peer-reviewed research, methodology, authors. "
                "Examples: 'find papers on machine learning', 'what does research say about X', "
                "'papers by Smith on climate change'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for papers (e.g., 'neural networks', 'climate change impacts')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "sources": {
                        "type": "array",
                        "description": "Which databases to search (default: all)",
                        "items": {
                            "type": "string",
                            "enum": ["semantic_scholar", "openalex", "pubmed"]
                        },
                        "default": ["semantic_scholar", "openalex"]
                    }
                },
                "required": ["query"]
            }
        }
    },

    # =========================================================================
    # FINANCIAL DATA TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_financial_data",
            "description": (
                "Get company financial data from SEC filings and Yahoo Finance. "
                "Use when user asks about: revenue, profit, earnings, market cap, stock price, "
                "financial statements, 10-K/10-Q filings, company metrics, valuation. "
                "Examples: 'Tesla revenue', 'Apple market cap', 'Microsoft P/E ratio'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'TSLA', 'AAPL', 'MSFT')"
                    },
                    "metrics": {
                        "type": "array",
                        "description": "Which metrics to retrieve (default: all available)",
                        "items": {
                            "type": "string",
                            "enum": [
                                "revenue", "profit", "earnings", "market_cap",
                                "stock_price", "pe_ratio", "debt", "cash_flow"
                            ]
                        },
                        "default": ["revenue", "profit", "market_cap"]
                    }
                },
                "required": ["ticker"]
            }
        }
    },

    # =========================================================================
    # WEB SEARCH TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web using DuckDuckGo for current information. "
                "Use when user asks about: current events, recent news, general facts, "
                "products, companies (non-financial), how-to guides, definitions. "
                "Examples: 'latest news on AI', 'what is X', 'how to do Y'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },

    # =========================================================================
    # FILE SYSTEM TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "List files and folders in a directory. "
                "Use when user asks: 'what folders are here', 'list files', 'show directory contents', "
                "'what's in this folder', 'ls'. "
                "DO NOT use for conversational questions about the agent itself."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)",
                        "default": "."
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Include hidden files (default: false)",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read contents of a file. "
                "Use when user asks to: read, show, display, or view a specific file. "
                "Examples: 'read config.json', 'show me app.py', 'what's in README.md'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to read (default: all)",
                        "default": -1
                    }
                },
                "required": ["file_path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "execute_shell_command",
            "description": (
                "Execute a shell command (bash/powershell). "
                "Use for: searching files (grep, find), git operations, running scripts, "
                "system operations. "
                "Examples: 'find Python files', 'git status', 'search for TODO in code'. "
                "IMPORTANT: Only for actual system commands, not for listing directories "
                "(use list_directory for that)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute (e.g., 'git status', 'find . -name \"*.py\"')"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Directory to run command in (default: current)",
                        "default": "."
                    }
                },
                "required": ["command"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write or create a file with content. "
                "Use when user asks to: create, write, save a file. "
                "Examples: 'create test.py with hello world', 'write config.json'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path where file should be created"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite if file exists (default: false)",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },

    # =========================================================================
    # CITATION MANAGEMENT TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "export_to_zotero",
            "description": (
                "Export papers to Zotero-compatible formats (BibTeX or RIS). "
                "Use when user wants to: export citations, save to Zotero, generate BibTeX, "
                "create bibliography, export references for LaTeX/Word. "
                "Examples: 'export to BibTeX', 'save these papers to Zotero', "
                "'generate bibliography for these papers'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "papers": {
                        "type": "array",
                        "description": "List of papers to export (paper objects from previous search)",
                        "items": {"type": "object"}
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format (bibtex or ris)",
                        "enum": ["bibtex", "ris"],
                        "default": "bibtex"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (optional)",
                        "default": None
                    }
                },
                "required": ["papers"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_related_papers",
            "description": (
                "Find papers related to a given paper via citation networks. "
                "Discovers papers that cite the same references (co-citations) or "
                "are cited by similar papers. Great for literature review expansion. "
                "Use when user wants: related papers, similar research, citation network, "
                "papers building on this work, what cites this paper. "
                "Examples: 'find related papers to BERT', 'what papers cite this', "
                "'expand my literature review'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Paper ID, DOI, or title to find related papers for"
                    },
                    "method": {
                        "type": "string",
                        "description": "How to find related papers",
                        "enum": ["citations", "references", "similar"],
                        "default": "similar"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of related papers to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["paper_id"]
            }
        }
    },

    # =========================================================================
    # DATA ANALYSIS & STATISTICS TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "load_dataset",
            "description": (
                "Load a dataset from CSV or Excel file for analysis. "
                "Use when user wants to: analyze data, load CSV/Excel, work with datasets, "
                "read data files, explore data, run statistical analysis. "
                "Examples: 'load data.csv', 'analyze this Excel file', "
                "'I have a dataset at /path/to/data.csv'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to CSV or Excel file (.csv, .xlsx, .xls, .tsv)"
                    }
                },
                "required": ["filepath"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": (
                "Compute descriptive statistics or correlation analysis on loaded dataset. "
                "Use for: descriptive stats (mean, median, std, quartiles), correlation tests, "
                "data summary, exploring relationships between variables. "
                "Examples: 'show me descriptive stats', 'correlate hours and scores', "
                "'is there a relationship between X and Y'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform",
                        "enum": ["descriptive", "correlation"],
                        "default": "descriptive"
                    },
                    "column": {
                        "type": "string",
                        "description": "Column name for descriptive stats (optional, all columns if not specified)"
                    },
                    "var1": {
                        "type": "string",
                        "description": "First variable for correlation (required for correlation)"
                    },
                    "var2": {
                        "type": "string",
                        "description": "Second variable for correlation (required for correlation)"
                    },
                    "method": {
                        "type": "string",
                        "description": "Correlation method",
                        "enum": ["pearson", "spearman"],
                        "default": "pearson"
                    }
                },
                "required": ["analysis_type"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_regression",
            "description": (
                "Run linear or multiple regression analysis on loaded dataset. "
                "Use when user wants: regression analysis, predict Y from X, model relationships, "
                "test predictors, find R-squared, regression coefficients. "
                "Examples: 'regress score on hours', 'predict Y from X1 and X2', "
                "'run regression: sales ~ advertising + price'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "y_variable": {
                        "type": "string",
                        "description": "Dependent variable (outcome) to predict"
                    },
                    "x_variables": {
                        "type": "array",
                        "description": "Independent variables (predictors)",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "model_type": {
                        "type": "string",
                        "description": "Type of regression model",
                        "enum": ["linear"],
                        "default": "linear"
                    }
                },
                "required": ["y_variable", "x_variables"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_assumptions",
            "description": (
                "Check statistical assumptions for tests (normality, homoscedasticity, etc.). "
                "Use when user asks: check assumptions, validate test requirements, "
                "normality test, homoscedasticity, assumption violations. "
                "Examples: 'check regression assumptions', 'is my data normal', "
                "'can I use ANOVA with this data'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "description": "Type of statistical test to check assumptions for",
                        "enum": ["regression", "anova", "ttest"]
                    }
                },
                "required": ["test_type"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "plot_data",
            "description": (
                "Create ASCII plots (scatter, bar, histogram) for data visualization in terminal. "
                "Use when user wants: plot data, visualize relationship, show distribution, "
                "create chart, graph variables. "
                "Examples: 'plot hours vs scores', 'show histogram of ages', "
                "'create bar chart of categories'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "description": "Type of plot to create",
                        "enum": ["scatter", "bar", "histogram"],
                        "default": "scatter"
                    },
                    "x_data": {
                        "description": "X-axis data (column name from dataset or list of values)"
                    },
                    "y_data": {
                        "description": "Y-axis data for scatter plots (column name or list of values)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Plot title",
                        "default": "Data Plot"
                    },
                    "categories": {
                        "type": "array",
                        "description": "Category names for bar chart",
                        "items": {"type": "string"}
                    },
                    "values": {
                        "description": "Values for bar chart or histogram (column name or list)"
                    },
                    "bins": {
                        "type": "integer",
                        "description": "Number of bins for histogram",
                        "default": 10,
                        "minimum": 5,
                        "maximum": 50
                    }
                },
                "required": ["plot_type"]
            }
        }
    },

    # =========================================================================
    # R INTEGRATION TOOLS
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "run_r_code",
            "description": (
                "Execute R code safely with validation and timeout. "
                "Use when user wants: run R script, execute R code, R analysis, "
                "use R packages, statistical analysis in R. "
                "Examples: 'run this R code: lm(y~x)', 'execute R script', "
                "'install.packages in R'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "r_code": {
                        "type": "string",
                        "description": "R code to execute"
                    },
                    "allow_writes": {
                        "type": "boolean",
                        "description": "Allow file write operations (default: false for safety)",
                        "default": False
                    }
                },
                "required": ["r_code"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "detect_project",
            "description": (
                "Detect project type (R project, Jupyter notebook, Python project) in directory. "
                "Use when user asks: what type of project, detect environment, "
                "check if R project, find project files, what packages installed. "
                "Examples: 'what type of project is this', 'am I in an R project', "
                "'what R packages do I have'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check for project (default: current directory)",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },

    # =========================================================================
    # CONVERSATIONAL TOOL
    # =========================================================================
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": (
                "Respond to conversational queries without using any tools. "
                "Use for: greetings ('hi', 'hello'), acknowledgments ('thanks', 'ok'), "
                "meta questions about the agent ('what can you do', 'who made you', 'are you AI'), "
                "simple tests ('test', 'testing'), casual conversation. "
                "Examples: 'test', 'thanks', 'how are you', 'what are your capabilities', "
                "'did you hardcode this', 'who built you'. "
                "IMPORTANT: Use this for questions ABOUT the agent itself, not questions "
                "that need external data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Conversational response to user"
                    }
                },
                "required": ["message"]
            }
        }
    }
]


def get_tool_by_name(name: str) -> Dict[str, Any]:
    """Get tool definition by name"""
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None


def get_tool_names() -> List[str]:
    """Get list of all tool names"""
    return [tool["function"]["name"] for tool in TOOLS]


def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a tool call against its schema.

    Returns:
        (is_valid, error_message)
    """
    tool = get_tool_by_name(tool_name)
    if not tool:
        return False, f"Unknown tool: {tool_name}"

    schema = tool["function"]["parameters"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required parameters
    for param in required:
        if param not in arguments:
            return False, f"Missing required parameter: {param}"

    # Check parameter types (basic validation)
    for param, value in arguments.items():
        if param not in properties:
            return False, f"Unknown parameter: {param}"

        expected_type = properties[param].get("type")
        if expected_type == "string" and not isinstance(value, str):
            return False, f"Parameter {param} must be a string"
        elif expected_type == "integer" and not isinstance(value, int):
            return False, f"Parameter {param} must be an integer"
        elif expected_type == "boolean" and not isinstance(value, bool):
            return False, f"Parameter {param} must be a boolean"
        elif expected_type == "array" and not isinstance(value, list):
            return False, f"Parameter {param} must be an array"

    return True, ""
