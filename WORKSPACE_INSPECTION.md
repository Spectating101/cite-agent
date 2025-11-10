# Workspace Inspection Feature

## Overview

The Cite Agent now supports **in-memory workspace inspection** across multiple data analysis platforms. This allows you to access and analyze data objects (dataframes, variables, datasets) that exist in your R, Python, or Stata environments - not just files saved to disk.

## Why This Matters

When doing data analysis, you often have:
- Dataframes loaded in R's `.GlobalEnv`
- Python objects in Jupyter notebooks
- Stata datasets in memory
- Intermediate calculation results stored as variables

**Previously:** The agent could only see files on disk - missing all this crucial in-memory data.

**Now:** The agent can inspect, analyze, and provide citations based on the actual data you're working with in real-time.

## Supported Platforms

| Platform | Status | Requirements |
|----------|--------|--------------|
| **Python** | ✅ Fully Implemented | Built-in (always available) |
| **R/RStudio** | ✅ Fully Implemented | Requires R + `jsonlite` package |
| **Stata** | 🚧 Partial (structure ready) | Requires Stata executable |

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Multi-Platform Workspace Manager              │
│  (Auto-detects available platforms)             │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴────────┬─────────────┐
       │                │             │
┌──────▼──────┐  ┌──────▼──────┐  ┌──▼─────────┐
│ Python      │  │ R           │  │ Stata      │
│ Inspector   │  │ Inspector   │  │ Inspector  │
│             │  │             │  │            │
│ • List vars │  │ • .GlobalEnv│  │ • Datasets │
│ • Get data  │  │ • Rscript   │  │ • Variables│
│ • Metadata  │  │ • jsonlite  │  │            │
└─────────────┘  └─────────────┘  └────────────┘
```

### Key Components

1. **WorkspaceInspector** (Base Class)
   - Defines common interface for all platforms
   - Methods: `list_objects()`, `get_object_info()`, `get_object_data()`, `describe_workspace()`

2. **Platform-Specific Inspectors**
   - `PythonWorkspaceInspector`: Direct access via Python namespace
   - `RWorkspaceInspector`: Execute R code via subprocess, JSON serialization
   - `StataWorkspaceInspector`: Template for future Stata integration

3. **Integration with EnhancedNocturnalAgent**
   - New methods: `list_workspace_objects()`, `inspect_workspace_object()`, `get_workspace_data()`, `describe_workspace()`
   - Automatic platform detection

4. **CLI Commands**
   - `workspace` / `list workspace` / `show workspace` - List all objects
   - `inspect <object_name>` - Get detailed info about an object
   - `view <object_name>` - Preview actual data

## Usage Examples

### Command Line Interface

```bash
# Start cite-agent
$ nocturnal

# List workspace objects
👤 You: workspace
📦 Python Workspace (__main__) - 0.0026 MB
┌──────────────────┬─────────────┬──────────┬────────────────┐
│ Name             │ Type        │ Class    │ Size/Dimensions│
├──────────────────┼─────────────┼──────────┼────────────────┤
│ df_sales         │ DataFrame   │ DataFrame│ 100×5          │
│ customer_data    │ DataFrame   │ DataFrame│ 50×3           │
│ total_revenue    │ int         │ int      │ -              │
│ regions          │ list        │ list     │ 4              │
└──────────────────┴─────────────┴──────────┴────────────────┘

# Inspect specific object
👤 You: inspect df_sales
🔍 Object: df_sales
┌─────────────────────────────────────────────────┐
│ Name: df_sales                                  │
│ Type: DataFrame                                 │
│ Class: DataFrame                                │
│ Dimensions: (100, 5)                           │
│ Columns: date, revenue, costs, region, profit   │
│ Column Types: datetime64, int64, int64, ...     │
│                                                 │
│ Preview:                                        │
│   date       revenue  costs  region  profit     │
│   2024-01-01    1500    800  North     700      │
│   ...                                           │
└─────────────────────────────────────────────────┘

# View actual data
👤 You: view df_sales
📊 df_sales (showing 20 of 100 rows)
┌────────────┬─────────┬───────┬────────┬────────┐
│ date       │ revenue │ costs │ region │ profit │
├────────────┼─────────┼───────┼────────┼────────┤
│ 2024-01-01 │ 1500    │ 800   │ North  │ 700    │
│ 2024-01-02 │ 2200    │ 1100  │ South  │ 1100   │
│ ...        │ ...     │ ...   │ ...    │ ...    │
└────────────┴─────────┴───────┴────────┴────────┘

# Natural language queries work too!
👤 You: What columns does my df_sales dataframe have?
🤖 Agent: Your df_sales dataframe has 5 columns: date, revenue,
          costs, region, and profit. It contains 100 rows of sales data.
```

### Python API

```python
from cite_agent import EnhancedNocturnalAgent
import pandas as pd

# Create some data
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=10),
    'revenue': [1500, 2200, 1800, 2500, 1900, 2100, 2300, 1700, 2000, 2400]
})

# Initialize agent
agent = EnhancedNocturnalAgent()

# Set namespace (for Python inspector)
python_inspector = agent.workspace_manager.get_inspector("Python")
python_inspector.set_namespace(globals())

# List all objects
result = agent.list_workspace_objects(platform="Python")
print(f"Found {result['total_objects']} objects")

# Inspect specific object
info = agent.inspect_workspace_object('df', platform="Python")
print(f"Object: {info['name']}")
print(f"Dimensions: {info['dimensions']}")
print(f"Columns: {info['columns']}")

# Get actual data
data = agent.get_workspace_data('df', limit=5, platform="Python")
print(f"First 5 rows: {data['data']}")

# Describe entire workspace
workspace = agent.describe_workspace(platform="Python")
print(f"Workspace size: {workspace['total_size_mb']:.2f} MB")
```

### R Integration

```r
# In R session
library(jsonlite)

# Create data
sales_data <- data.frame(
  date = seq.Date(as.Date("2024-01-01"), by="day", length.out=10),
  revenue = c(1500, 2200, 1800, 2500, 1900, 2100, 2300, 1700, 2000, 2400),
  costs = c(800, 1100, 900, 1200, 950, 1050, 1150, 850, 1000, 1200)
)

# In terminal (cite-agent)
$ nocturnal

👤 You: workspace
📦 R Workspace (.GlobalEnv) - 0.0012 MB
┌──────────────┬────────────┬────────────┬─────────────┐
│ Name         │ Type       │ Class      │ Dimensions  │
├──────────────┼────────────┼────────────┼─────────────┤
│ sales_data   │ list       │ data.frame │ 10×3        │
└──────────────┴────────────┴────────────┴─────────────┘

👤 You: What's in my sales_data?
🤖 Agent: Your sales_data is a data.frame with 10 rows and 3 columns:
          - date: Date column
          - revenue: Numeric (revenue figures)
          - costs: Numeric (cost figures)

          Total revenue: 20,500
          Average costs: 1,015
```

## Technical Details

### Python Inspector

- **Access Method**: Direct namespace inspection via `globals()` or custom namespace
- **Supported Types**: DataFrames, lists, tuples, dicts, numpy arrays, variables
- **Data Serialization**: Native Python objects (JSON-compatible)

### R Inspector

- **Access Method**: Subprocess execution of R code via `Rscript`
- **Dependencies**: R installation + `jsonlite` package
- **Communication**: JSON serialization for data transfer
- **Environment**: `.GlobalEnv` by default

**R Code Example (executed internally):**
```r
# List objects
objs <- ls(envir = .GlobalEnv)
info <- lapply(objs, function(obj_name) {
  obj <- get(obj_name, envir = .GlobalEnv)
  list(
    name = obj_name,
    type = typeof(obj),
    class = class(obj),
    dimensions = if(is.data.frame(obj)) dim(obj) else NULL
  )
})
cat(jsonlite::toJSON(info))
```

### Stata Inspector

- **Status**: Scaffold implemented, full integration pending
- **Planned Approach**: Execute Stata .do files, parse output
- **Challenges**: Stata's non-interactive mode limitations

## Installation & Setup

### Python (Always Available)

No setup required - Python inspector works out of the box.

### R Setup

1. Install R: `https://www.r-project.org/`
2. Install jsonlite package:
   ```r
   install.packages("jsonlite")
   ```
3. Ensure `Rscript` is in your PATH
4. Restart cite-agent

### Stata Setup (Future)

1. Install Stata
2. Ensure Stata executable is in PATH
3. (Additional configuration TBD)

## Use Cases

### 1. Data Analysis Workflows

```
Scenario: You're analyzing survey data in R

1. Load data: df <- read.csv("survey.csv")
2. Clean data: df_clean <- filter(df, age > 18)
3. Ask agent: "What statistical tests should I use for this data?"

Agent can now SEE df_clean's structure, column types, and distributions
to provide accurate, context-aware statistical guidance.
```

### 2. Citation Generation

```
Scenario: You need to cite the methods used

👤 You: I'm running a linear regression on my df_sales data.
        What papers should I cite for the methodology?

🤖 Agent: [Inspects df_sales, sees it has revenue, costs, time series]

          For linear regression with time series sales data, cite:
          1. Box, G. E., & Jenkins, G. M. (1970). Time Series Analysis...
          2. Hamilton, J. D. (1994). Time Series Analysis...

          Since your data has 100 observations, you should also
          consider autocorrelation tests. Cite:
          3. Durbin, J., & Watson, G. S. (1950). Testing for serial...
```

### 3. Debugging Data Issues

```
👤 You: My regression keeps failing
🤖 Agent: [Inspects your dataframe]
          I see the issue - your 'revenue' column has 5 NA values
          and 'region' has inconsistent capitalization (North vs north).
          Here's how to fix it: [provides code + citations]
```

## API Reference

### EnhancedNocturnalAgent Methods

#### `list_workspace_objects(platform: Optional[str] = None) -> Dict[str, Any]`

List all objects in workspace.

**Parameters:**
- `platform`: Optional platform name ("R", "Python", "Stata"). Auto-detects if None.

**Returns:**
```python
{
    "platform": "Python",
    "objects": [
        {
            "name": "df_sales",
            "type": "DataFrame",
            "class": "DataFrame",
            "size": 100,
            "dimensions": (100, 5),
            "columns": ["date", "revenue", "costs", "region", "profit"]
        },
        ...
    ],
    "total_objects": 5
}
```

#### `inspect_workspace_object(name: str, platform: Optional[str] = None) -> Dict[str, Any]`

Get detailed information about a specific object.

**Parameters:**
- `name`: Object name
- `platform`: Optional platform name

**Returns:**
```python
{
    "name": "df_sales",
    "type": "DataFrame",
    "class": "DataFrame",
    "size": 100,
    "dimensions": (100, 5),
    "columns": ["date", "revenue", "costs", "region", "profit"],
    "preview": "   date       revenue  costs\n0  2024-01-01    1500    800\n...",
    "metadata": {
        "column_types": {
            "date": "datetime64",
            "revenue": "int64",
            ...
        }
    }
}
```

#### `get_workspace_data(name: str, limit: int = 100, platform: Optional[str] = None) -> Dict[str, Any]`

Get actual data from an object.

**Parameters:**
- `name`: Object name
- `limit`: Max rows/elements to return
- `platform`: Optional platform name

**Returns:**
```python
{
    "type": "dataframe",
    "data": [
        {"date": "2024-01-01", "revenue": 1500, "costs": 800},
        ...
    ],
    "total_rows": 100,
    "shown_rows": 20,
    "truncated": True
}
```

#### `describe_workspace(platform: Optional[str] = None) -> Dict[str, Any]`

Get summary of entire workspace.

**Parameters:**
- `platform`: Optional platform name. If None, returns all platforms.

**Returns:**
```python
{
    "platform": "Python",
    "total_objects": 5,
    "total_size_mb": 0.0026,
    "objects": [...],
    "environment_name": "__main__"
}
```

## Limitations & Future Work

### Current Limitations

1. **R Workspace**: Requires R subprocess - slower than native access
2. **Stata**: Not fully implemented yet
3. **Large Objects**: Previews are truncated (configurable limits)
4. **Binary Data**: Images, models, etc. show metadata only, not visual preview

### Future Enhancements

1. **RStudio Server API**: Direct connection for faster R access
2. **Stata Integration**: Complete .do file execution and parsing
3. **Julia Support**: Add Julia workspace inspector
4. **SAS/SPSS**: Support for proprietary statistical software
5. **Jupyter Kernel**: Direct kernel communication for Jupyter notebooks
6. **Visualization**: Automatic plot generation for dataframes
7. **Smart Caching**: Cache workspace state to reduce subprocess calls

## Contributing

To add support for a new platform:

1. Create a new inspector class inheriting from `WorkspaceInspector`
2. Implement required methods:
   - `is_available()`
   - `list_objects()`
   - `get_object_info(name)`
   - `get_object_data(name, limit)`
   - `describe_workspace()`
3. Add to `MultiPlatformWorkspaceManager.inspectors`
4. Test with real platform environment
5. Submit PR with documentation

## License

Same as Cite Agent main project.

## Contact

For questions or issues related to workspace inspection:
- GitHub Issues: [cite-agent/issues](https://github.com/Spectating101/cite-agent/issues)
- Tag: `workspace-inspection`

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
**Status**: Production Ready (Python + R), Beta (Stata)
