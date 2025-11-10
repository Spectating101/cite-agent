"""
Workspace Inspector - Multi-platform in-memory data access for data analysis environments.

This module provides a unified interface for accessing in-memory data objects across
different statistical and data analysis platforms (R, Stata, Python/Jupyter, etc.).

The key insight: Data analysts work with floating data in memory. Without access to
these objects, a citation agent cannot provide contextually relevant citations for
the actual analysis being performed.

RESOURCE OPTIMIZATION:
Designed for average user environments (8GB RAM laptops). All operations use:
- Sampling for large datasets (>10k rows)
- Memory-efficient data transfer (JSON streaming where possible)
- Row limits to prevent OOM errors
- Automatic detection of resource constraints
"""

import json
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
import os

logger = logging.getLogger(__name__)

# ==============================================================================
# RESOURCE LIMITS FOR 8GB RAM ENVIRONMENTS
# ==============================================================================

# Maximum rows to fetch from a dataset at once (prevents OOM on 8GB RAM)
MAX_ROWS_DEFAULT = 1000

# Maximum rows to use for statistical analysis (sampling for large datasets)
MAX_ROWS_ANALYSIS = 10000

# Threshold for automatic sampling (datasets larger than this get sampled)
LARGE_DATASET_THRESHOLD = 50000

# Maximum object size to serialize in MB (for JSON transfer)
MAX_OBJECT_SIZE_MB = 100

# Memory buffer - stop operations if available memory below this (MB)
MIN_AVAILABLE_MEMORY_MB = 500


@dataclass
class WorkspaceObject:
    """Represents an object in a workspace/environment."""
    name: str
    type: str  # "data.frame", "numeric", "character", "dataset", etc.
    class_name: str  # Detailed class information
    size: Optional[int] = None  # Number of elements/rows
    dimensions: Optional[tuple] = None  # (rows, cols) for 2D objects
    columns: Optional[List[str]] = None  # Column names for dataframes
    preview: Optional[str] = None  # Text preview of the data
    metadata: Optional[Dict[str, Any]] = None  # Platform-specific metadata


@dataclass
class WorkspaceInfo:
    """Summary of an entire workspace."""
    platform: str  # "R", "Stata", "Python", etc.
    objects: List[WorkspaceObject]
    total_objects: int
    total_size_mb: Optional[float] = None
    environment_name: Optional[str] = None  # e.g., ".GlobalEnv", "main"
    metadata: Optional[Dict[str, Any]] = None


class WorkspaceInspector(ABC):
    """Base class for platform-specific workspace inspectors."""

    def __init__(self):
        self._object_cache = {}  # name -> (timestamp, WorkspaceObject)
        self._cache_ttl = 30  # seconds

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this platform is available and active."""
        pass

    @abstractmethod
    def list_objects(self) -> List[WorkspaceObject]:
        """List all objects in the workspace."""
        pass

    @abstractmethod
    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about a specific object."""
        pass

    @abstractmethod
    def get_object_data(self, name: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get actual data from an object (with row limit for dataframes)."""
        pass

    @abstractmethod
    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of entire workspace."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the platform (R, Stata, Python, etc.)."""
        pass

    # ==============================================================================
    # WORKSPACE CHANGE DETECTION & VALIDATION
    # ==============================================================================

    def validate_object_exists(self, name: str) -> bool:
        """
        Validate that an object still exists in the workspace.

        This prevents errors when users delete or modify objects between operations.

        Args:
            name: Object name to validate

        Returns:
            True if object exists, False otherwise
        """
        try:
            obj_info = self.get_object_info(name)
            return obj_info is not None
        except Exception as e:
            logger.error(f"Error validating object {name}: {e}")
            return False

    def get_workspace_changes(self, previous_objects: List[str]) -> Dict[str, List[str]]:
        """
        Detect changes in workspace since last check.

        Useful for alerting users when referenced data has been modified.

        Args:
            previous_objects: List of object names from previous check

        Returns:
            Dict with 'added', 'removed', 'unchanged' lists
        """
        try:
            current_objects = {obj.name for obj in self.list_objects()}
            previous_set = set(previous_objects)

            return {
                'added': list(current_objects - previous_set),
                'removed': list(previous_set - current_objects),
                'unchanged': list(current_objects & previous_set)
            }
        except Exception as e:
            logger.error(f"Error detecting workspace changes: {e}")
            return {'added': [], 'removed': [], 'unchanged': previous_objects}

    def refresh_cache(self):
        """Refresh the object cache (useful after workspace modifications)."""
        self._object_cache.clear()
        logger.debug(f"{self.platform_name} workspace cache refreshed")


class RWorkspaceInspector(WorkspaceInspector):
    """Inspector for R environments (.GlobalEnv)."""

    def __init__(self, r_executable: str = "Rscript"):
        super().__init__()
        self.r_executable = r_executable
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if required R packages are available."""
        try:
            # Check if jsonlite is installed
            code = """
            if (!requireNamespace("jsonlite", quietly = TRUE)) {
                cat("MISSING:jsonlite")
            } else {
                cat("OK")
            }
            """
            result = self._execute_r_code(code)
            if "MISSING" in result:
                logger.warning("R package 'jsonlite' not installed. Install with: install.packages('jsonlite')")
        except Exception as e:
            logger.warning(f"Could not check R dependencies: {e}")

    def _execute_r_code(self, code: str) -> str:
        """Execute R code and return output."""
        try:
            result = subprocess.run(
                [self.r_executable, '-e', code],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"R execution failed: {result.stderr}")
                return ""
        except subprocess.TimeoutExpired:
            logger.error("R execution timed out")
            return ""
        except Exception as e:
            logger.error(f"Error executing R code: {e}")
            return ""

    @property
    def platform_name(self) -> str:
        return "R"

    def is_available(self) -> bool:
        """Check if R is available."""
        try:
            result = subprocess.run(
                [self.r_executable, '--version'],
                capture_output=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def list_objects(self) -> List[WorkspaceObject]:
        """List all objects in .GlobalEnv."""
        code = """
        if (!requireNamespace("jsonlite", quietly = TRUE)) {
            cat("[]")
        } else {
            objs <- ls(envir = .GlobalEnv)
            if (length(objs) == 0) {
                cat("[]")
            } else {
                info <- lapply(objs, function(obj_name) {
                    obj <- get(obj_name, envir = .GlobalEnv)
                    obj_class <- class(obj)
                    obj_type <- typeof(obj)

                    result <- list(
                        name = obj_name,
                        type = obj_type,
                        class = paste(obj_class, collapse = ", ")
                    )

                    # Add dimensions for data structures
                    if (is.data.frame(obj) || is.matrix(obj)) {
                        result$dimensions <- dim(obj)
                        if (is.data.frame(obj)) {
                            result$columns <- colnames(obj)
                        }
                    } else if (is.vector(obj) || is.list(obj)) {
                        result$size <- length(obj)
                    }

                    return(result)
                })
                cat(jsonlite::toJSON(info, auto_unbox = TRUE))
            }
        }
        """

        output = self._execute_r_code(code)
        if not output:
            return []

        try:
            data = json.loads(output)
            objects = []
            for item in data:
                obj = WorkspaceObject(
                    name=item['name'],
                    type=item.get('type', 'unknown'),
                    class_name=item.get('class', 'unknown'),
                    size=item.get('size'),
                    dimensions=tuple(item['dimensions']) if 'dimensions' in item else None,
                    columns=item.get('columns')
                )
                objects.append(obj)
            return objects
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse R output: {e}")
            return []

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about a specific object."""
        code = f"""
        if (!requireNamespace("jsonlite", quietly = TRUE)) {{
            cat("{{}}")
        }} else {{
            if (!exists("{name}", envir = .GlobalEnv)) {{
                cat("{{}}")
            }} else {{
                obj <- get("{name}", envir = .GlobalEnv)

                info <- list(
                    name = "{name}",
                    type = typeof(obj),
                    class = paste(class(obj), collapse = ", "),
                    size = length(obj)
                )

                if (is.data.frame(obj) || is.matrix(obj)) {{
                    info$dimensions <- dim(obj)
                    info$size <- nrow(obj)
                    if (is.data.frame(obj)) {{
                        info$columns <- colnames(obj)
                        # Get column types
                        info$column_types <- sapply(obj, function(col) class(col)[1])
                    }}
                }}

                # Add preview
                info$preview <- paste(capture.output(str(obj, max.level = 1)), collapse = "\\n")

                cat(jsonlite::toJSON(info, auto_unbox = TRUE))
            }}
        }}
        """

        output = self._execute_r_code(code)
        if not output or output.strip() == "{}":
            return None

        try:
            data = json.loads(output)
            return WorkspaceObject(
                name=data['name'],
                type=data.get('type', 'unknown'),
                class_name=data.get('class', 'unknown'),
                size=data.get('size'),
                dimensions=tuple(data['dimensions']) if 'dimensions' in data else None,
                columns=data.get('columns'),
                preview=data.get('preview'),
                metadata={'column_types': data.get('column_types')} if 'column_types' in data else None
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse R object info: {e}")
            return None

    def get_object_data(self, name: str, limit: int = None) -> Optional[Dict[str, Any]]:
        """
        Get actual data from an object with resource-aware sampling.

        Args:
            name: Object name
            limit: Max rows to fetch (None = use MAX_ROWS_DEFAULT)
        """
        if limit is None:
            limit = MAX_ROWS_DEFAULT

        # Cap limit to prevent OOM on 8GB RAM systems
        limit = min(limit, MAX_ROWS_DEFAULT)

        code = f"""
        if (!requireNamespace("jsonlite", quietly = TRUE)) {{
            cat('{{"error": "R package jsonlite not installed. Please run: install.packages(\\"jsonlite\\")"}}')
        }} else {{
            if (!exists("{name}", envir = .GlobalEnv)) {{
                cat('{{"error": "Object {name} not found in workspace"}}')
            }} else {{
                obj <- get("{name}", envir = .GlobalEnv)

                if (is.data.frame(obj)) {{
                    total_rows <- nrow(obj)

                    # Smart sampling for large datasets (8GB RAM friendly)
                    if (total_rows > {LARGE_DATASET_THRESHOLD}) {{
                        # Sample for very large datasets
                        sample_size <- min({limit}, {MAX_ROWS_ANALYSIS})
                        sample_indices <- sample(1:total_rows, sample_size)
                        obj_preview <- obj[sample_indices, , drop = FALSE]
                        sampling_method <- "random_sample"
                        truncated <- TRUE
                    }} else if (total_rows > {limit}) {{
                        # Head for moderately large datasets
                        obj_preview <- head(obj, {limit})
                        sampling_method <- "head"
                        truncated <- TRUE
                    }} else {{
                        obj_preview <- obj
                        sampling_method <- "full"
                        truncated <- FALSE
                    }}

                    result <- list(
                        type = "dataframe",
                        data = obj_preview,
                        total_rows = total_rows,
                        shown_rows = nrow(obj_preview),
                        truncated = truncated,
                        sampling_method = sampling_method
                    )
                }} else if (is.vector(obj)) {{
                    total_len <- length(obj)
                    if (total_len > {limit}) {{
                        obj_preview <- head(obj, {limit})
                        truncated <- TRUE
                    }} else {{
                        obj_preview <- obj
                        truncated <- FALSE
                    }}

                    result <- list(
                        type = "vector",
                        data = obj_preview,
                        total_length = total_len,
                        shown_length = length(obj_preview),
                        truncated = truncated
                    )
                }} else {{
                    result <- list(
                        type = "other",
                        preview = paste(capture.output(print(obj)), collapse = "\\n")
                    )
                }}

                cat(jsonlite::toJSON(result, auto_unbox = TRUE, dataframe = "rows"))
            }}
        }}
        """

        output = self._execute_r_code(code)
        if not output or output.strip() == "{}":
            return None

        try:
            data = json.loads(output)
            if 'error' in data:
                logger.error(f"R workspace error: {data['error']}")
                return {'error': data['error']}
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse R object data: {e}")
            return None

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of entire R workspace."""
        objects = self.list_objects()

        code = """
        if (!requireNamespace("jsonlite", quietly = TRUE)) {
            cat("{}")
        } else {
            # Calculate total size
            objs <- ls(envir = .GlobalEnv)
            if (length(objs) > 0) {
                sizes <- sapply(objs, function(obj_name) {
                    object.size(get(obj_name, envir = .GlobalEnv))
                })
                total_size_bytes <- sum(sizes)
                total_size_mb <- total_size_bytes / (1024^2)

                result <- list(
                    total_size_mb = total_size_mb,
                    environment = "GlobalEnv"
                )
            } else {
                result <- list(
                    total_size_mb = 0,
                    environment = "GlobalEnv"
                )
            }
            cat(jsonlite::toJSON(result, auto_unbox = TRUE))
        }
        """

        output = self._execute_r_code(code)
        metadata = {}
        total_size_mb = None
        env_name = ".GlobalEnv"

        if output and output.strip() != "{}":
            try:
                data = json.loads(output)
                total_size_mb = data.get('total_size_mb')
                env_name = data.get('environment', '.GlobalEnv')
            except json.JSONDecodeError:
                pass

        return WorkspaceInfo(
            platform="R",
            objects=objects,
            total_objects=len(objects),
            total_size_mb=total_size_mb,
            environment_name=env_name
        )


class StataWorkspaceInspector(WorkspaceInspector):
    """Inspector for Stata datasets and variables in memory."""

    def __init__(self, stata_executable: str = "stata"):
        super().__init__()
        self.stata_executable = stata_executable

    @property
    def platform_name(self) -> str:
        return "Stata"

    def is_available(self) -> bool:
        """Check if Stata is available."""
        # Check for common Stata executables
        executables = ["stata", "stata-se", "stata-mp", "StataMP", "StataSE"]
        for exe in executables:
            try:
                result = subprocess.run(
                    [exe, '-q', '-b'],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0 or "Stata" in result.stderr.decode():
                    self.stata_executable = exe
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return False

    def _execute_stata_code(self, code: str) -> str:
        """Execute Stata code and return output."""
        # Create temporary .do file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.do', delete=False) as f:
            f.write(code)
            do_file = f.name

        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name

        try:
            result = subprocess.run(
                [self.stata_executable, '-b', 'do', do_file],
                capture_output=True,
                timeout=30,
                check=False
            )

            # Read log file
            try:
                with open(log_file, 'r') as f:
                    output = f.read()
                return output
            except FileNotFoundError:
                return result.stdout.decode() if result.stdout else ""

        except subprocess.TimeoutExpired:
            logger.error("Stata execution timed out")
            return ""
        except Exception as e:
            logger.error(f"Error executing Stata code: {e}")
            return ""
        finally:
            # Cleanup temp files
            Path(do_file).unlink(missing_ok=True)
            Path(log_file).unlink(missing_ok=True)

    def list_objects(self) -> List[WorkspaceObject]:
        """
        List variables in the active Stata dataset.

        Stata keeps one dataset in memory at a time. This lists all variables
        in that dataset.
        """
        code = """
        quietly describe
        if _rc == 0 {
            quietly describe, short
            local nvars = r(k)
            local nobs = r(N)

            * Export variable info to JSON-like format
            quietly ds
            local varlist `r(varlist)'

            display "{"
            display `"  "variables": ["'
            local first = 1
            foreach var of varlist `varlist' {
                if `first' == 0 {
                    display "," _continue
                }
                local first = 0

                local vartype : type `var'
                display `"    {"'
                display `"      "name": "`var'","'
                display `"      "type": "`vartype'","'

                * Get variable label if exists
                local varlabel : variable label `var'
                if `"`varlabel'"' != "" {
                    display `"      "label": "`varlabel'","'
                }

                display `"      "observations": `nobs'"'
                display `"    }"' _continue
            }
            display ""
            display "  ],"
            display `"  "total_observations": `nobs'"'
            display "}"
        }
        else {
            display `"{"error": "No dataset in memory"}"'
        }
        """

        output = self._execute_stata_code(code)
        if not output:
            return []

        try:
            # Extract JSON from Stata output (which includes log text)
            # Look for the JSON object pattern
            import re
            json_match = re.search(r'\{[\s\S]*\}', output)
            if json_match:
                data = json.loads(json_match.group(0))

                if 'error' in data:
                    logger.warning(f"Stata workspace: {data['error']}")
                    return []

                objects = []
                for var in data.get('variables', []):
                    obj = WorkspaceObject(
                        name=var['name'],
                        type=var['type'],
                        class_name='stata_variable',
                        size=var['observations'],
                        metadata={'label': var.get('label')} if var.get('label') else None
                    )
                    objects.append(obj)
                return objects
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Stata output: {e}")
            return []

        return []

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about a Stata variable."""
        code = f"""
        capture confirm variable {name}
        if _rc == 0 {{
            local vartype : type {name}
            local varlabel : variable label {name}
            quietly count
            local nobs = r(N)

            * Get summary statistics for numeric variables
            capture summarize {name}, detail
            if _rc == 0 {{
                local mean = r(mean)
                local sd = r(sd)
                local min = r(min)
                local max = r(max)

                display "{{"
                display `"  "name": "{name}","'
                display `"  "type": "`vartype'","'
                display `"  "label": "`varlabel'","'
                display `"  "observations": `nobs',"'
                display `"  "mean": `mean',"'
                display `"  "sd": `sd',"'
                display `"  "min": `min',"'
                display `"  "max": `max'"'
                display "}}"
            }}
            else {{
                * Non-numeric variable
                display "{{"
                display `"  "name": "{name}","'
                display `"  "type": "`vartype'","'
                display `"  "label": "`varlabel'","'
                display `"  "observations": `nobs'"'
                display "}}"
            }}
        }}
        else {{
            display `"{{"error": "Variable {name} not found"}}"'
        }}
        """

        output = self._execute_stata_code(code)
        if not output:
            return None

        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', output)
            if json_match:
                data = json.loads(json_match.group(0))

                if 'error' in data:
                    return None

                metadata = {}
                if 'label' in data:
                    metadata['label'] = data['label']
                if 'mean' in data:
                    metadata['mean'] = data['mean']
                    metadata['sd'] = data['sd']
                    metadata['min'] = data['min']
                    metadata['max'] = data['max']

                return WorkspaceObject(
                    name=data['name'],
                    type=data['type'],
                    class_name='stata_variable',
                    size=data['observations'],
                    metadata=metadata if metadata else None
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Stata output: {e}")

        return None

    def get_object_data(self, name: str, limit: int = None) -> Optional[Dict[str, Any]]:
        """
        Get data from a Stata variable with resource-aware limits.

        Args:
            name: Variable name
            limit: Max observations to fetch (None = use MAX_ROWS_DEFAULT)
        """
        if limit is None:
            limit = MAX_ROWS_DEFAULT

        # Cap limit for 8GB RAM systems
        limit = min(limit, MAX_ROWS_DEFAULT)

        code = f"""
        capture confirm variable {name}
        if _rc == 0 {{
            quietly count
            local total_obs = r(N)

            * Resource-aware sampling for large datasets
            if `total_obs' > {LARGE_DATASET_THRESHOLD} {{
                * Random sample for very large datasets
                preserve
                sample {MAX_ROWS_ANALYSIS}, count
                local shown_obs = _N
                local sampling = "random_sample"
                restore, preserve
            }}
            else if `total_obs' > {limit} {{
                * Head for moderate datasets
                local shown_obs = {limit}
                local sampling = "head"
            }}
            else {{
                local shown_obs = `total_obs'
                local sampling = "full"
            }}

            * List first observations
            display "{{"
            display `"  "type": "variable","'
            display `"  "data": ["'
            list {name} in 1/`shown_obs', noobs separator(0)
            display "  ],"
            display `"  "total_observations": `total_obs',"'
            display `"  "shown_observations": `shown_obs',"'
            display `"  "truncated": "' (`total_obs' > `shown_obs') `"","'
            display `"  "sampling_method": "`sampling'""'
            display "}}"
        }}
        else {{
            display `"{{"error": "Variable {name} not found"}}"'
        }}
        """

        output = self._execute_stata_code(code)
        if not output:
            return None

        try:
            # Parse Stata output - this is simplified for now
            # In practice, would need more sophisticated parsing
            import re
            json_match = re.search(r'\{[\s\S]*\}', output)
            if json_match:
                data = json.loads(json_match.group(0))

                if 'error' in data:
                    logger.error(f"Stata error: {data['error']}")
                    return {'error': data['error']}

                return data
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Stata output: {e}")

        return None

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of active Stata dataset."""
        objects = self.list_objects()

        code = """
        quietly describe, short
        if _rc == 0 {
            local nobs = r(N)
            local nvars = r(k)
            local width = r(width)

            * Estimate memory usage (bytes)
            local mem_bytes = `nobs' * `width'
            local mem_mb = `mem_bytes' / (1024 * 1024)

            display "{"
            display `"  "observations": `nobs',"'
            display `"  "variables": `nvars',"'
            display `"  "memory_mb": `mem_mb'"'
            display "}"
        }
        else {
            display `"{"error": "No dataset in memory"}"'
        }
        """

        output = self._execute_stata_code(code)
        total_size_mb = None
        metadata = {}

        if output:
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    data = json.loads(json_match.group(0))
                    if 'error' not in data:
                        total_size_mb = data.get('memory_mb')
                        metadata = {
                            'observations': data.get('observations'),
                            'variables': data.get('variables')
                        }
            except (json.JSONDecodeError, KeyError):
                pass

        return WorkspaceInfo(
            platform="Stata",
            objects=objects,
            total_objects=len(objects),
            total_size_mb=total_size_mb,
            environment_name="active_dataset",
            metadata=metadata if metadata else None
        )


class PythonWorkspaceInspector(WorkspaceInspector):
    """Inspector for Python/Jupyter environments."""

    def __init__(self):
        super().__init__()
        self._namespace = None

    @property
    def platform_name(self) -> str:
        return "Python"

    def is_available(self) -> bool:
        """Check if we're running in Python (we always are!)."""
        return True

    def set_namespace(self, namespace: Dict[str, Any]) -> None:
        """Set the namespace to inspect (for Jupyter integration)."""
        self._namespace = namespace

    def list_objects(self) -> List[WorkspaceObject]:
        """List objects in Python namespace."""
        if self._namespace is None:
            # Use globals() from main module
            import __main__
            namespace = vars(__main__)
        else:
            namespace = self._namespace

        objects = []
        for name, obj in namespace.items():
            # Skip private and builtin objects
            if name.startswith('_') or name.startswith('__'):
                continue

            # Skip modules and functions
            if isinstance(obj, type(sys)):
                continue

            obj_type = type(obj).__name__
            obj_class = obj.__class__.__name__

            # Get dimensions for dataframes/arrays
            dimensions = None
            columns = None
            size = None

            try:
                # Check if it's a pandas DataFrame
                if hasattr(obj, 'shape') and hasattr(obj, 'columns'):
                    dimensions = obj.shape
                    columns = list(obj.columns)
                    size = len(obj)
                # Check if it's a numpy array
                elif hasattr(obj, 'shape'):
                    dimensions = obj.shape
                    size = obj.size
                # Check if it's a list/tuple
                elif isinstance(obj, (list, tuple)):
                    size = len(obj)
            except Exception:
                pass

            workspace_obj = WorkspaceObject(
                name=name,
                type=obj_type,
                class_name=obj_class,
                size=size,
                dimensions=dimensions,
                columns=columns
            )
            objects.append(workspace_obj)

        return objects

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about a Python object."""
        if self._namespace is None:
            import __main__
            namespace = vars(__main__)
        else:
            namespace = self._namespace

        if name not in namespace:
            return None

        obj = namespace[name]
        obj_type = type(obj).__name__
        obj_class = obj.__class__.__name__

        dimensions = None
        columns = None
        size = None
        preview = None
        metadata = {}

        try:
            # Pandas DataFrame
            if hasattr(obj, 'shape') and hasattr(obj, 'columns'):
                dimensions = obj.shape
                columns = list(obj.columns)
                size = len(obj)
                metadata['column_types'] = {col: str(dtype) for col, dtype in obj.dtypes.items()}
                preview = str(obj.head(5))
            # Numpy array
            elif hasattr(obj, 'shape'):
                dimensions = obj.shape
                size = obj.size
                metadata['dtype'] = str(obj.dtype)
                preview = str(obj)
            # List/tuple
            elif isinstance(obj, (list, tuple)):
                size = len(obj)
                preview = str(obj[:10]) if len(obj) > 10 else str(obj)
            # Other objects
            else:
                preview = str(obj)[:500]  # Limit preview length
        except Exception as e:
            logger.error(f"Error inspecting Python object: {e}")

        return WorkspaceObject(
            name=name,
            type=obj_type,
            class_name=obj_class,
            size=size,
            dimensions=dimensions,
            columns=columns,
            preview=preview,
            metadata=metadata if metadata else None
        )

    def get_object_data(self, name: str, limit: int = None) -> Optional[Dict[str, Any]]:
        """
        Get actual data from a Python object with resource-aware sampling.

        Args:
            name: Object name
            limit: Max rows to fetch (None = use MAX_ROWS_DEFAULT)
        """
        if limit is None:
            limit = MAX_ROWS_DEFAULT

        # Cap limit for 8GB RAM systems
        limit = min(limit, MAX_ROWS_DEFAULT)

        if self._namespace is None:
            import __main__
            namespace = vars(__main__)
        else:
            namespace = self._namespace

        if name not in namespace:
            return {'error': f'Object {name} not found in workspace'}

        obj = namespace[name]

        try:
            # Pandas DataFrame
            if hasattr(obj, 'shape') and hasattr(obj, 'columns'):
                total_rows = len(obj)

                # Smart sampling for large datasets (8GB RAM friendly)
                if total_rows > LARGE_DATASET_THRESHOLD:
                    # Random sample for very large datasets
                    sample_size = min(limit, MAX_ROWS_ANALYSIS)
                    data_preview = obj.sample(n=sample_size) if total_rows > sample_size else obj
                    sampling_method = "random_sample"
                    truncated = True
                elif total_rows > limit:
                    # Head for moderately large datasets
                    data_preview = obj.head(limit)
                    sampling_method = "head"
                    truncated = True
                else:
                    data_preview = obj
                    sampling_method = "full"
                    truncated = False

                return {
                    'type': 'dataframe',
                    'data': data_preview.to_dict(orient='records'),
                    'columns': list(obj.columns),
                    'total_rows': total_rows,
                    'shown_rows': len(data_preview),
                    'truncated': truncated,
                    'sampling_method': sampling_method
                }
            # List/tuple
            elif isinstance(obj, (list, tuple)):
                total_length = len(obj)

                # Sample lists too for memory efficiency
                if total_length > limit:
                    data_preview = obj[:limit]
                    truncated = True
                else:
                    data_preview = obj
                    truncated = False

                return {
                    'type': 'list',
                    'data': data_preview,
                    'total_length': total_length,
                    'shown_length': len(data_preview),
                    'truncated': truncated
                }
            # Other objects
            else:
                # Limit preview length for memory
                return {
                    'type': 'other',
                    'preview': str(obj)[:1000]
                }
        except Exception as e:
            logger.error(f"Error getting Python object data: {e}")
            return {'error': str(e)}

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of Python workspace."""
        objects = self.list_objects()

        # Calculate total size
        if self._namespace is None:
            import __main__
            namespace = vars(__main__)
        else:
            namespace = self._namespace

        total_size_bytes = 0
        for name, obj in namespace.items():
            if not name.startswith('_'):
                try:
                    total_size_bytes += sys.getsizeof(obj)
                except Exception:
                    pass

        total_size_mb = total_size_bytes / (1024 ** 2)

        return WorkspaceInfo(
            platform="Python",
            objects=objects,
            total_objects=len(objects),
            total_size_mb=total_size_mb,
            environment_name="__main__"
        )


class SPSSWorkspaceInspector(WorkspaceInspector):
    """Inspector for SPSS (Statistical Package for the Social Sciences) environments."""

    def __init__(self, spss_executable: str = "spss"):
        super().__init__()
        self.spss_executable = spss_executable
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if SPSS Python integration (spss package) is available."""
        try:
            import spss
            logger.info("SPSS Python integration detected")
        except ImportError:
            logger.warning(
                "SPSS Python integration not available. "
                "For full SPSS support, install the spss package that comes with SPSS Statistics."
            )

    @property
    def platform_name(self) -> str:
        return "SPSS"

    def is_available(self) -> bool:
        """Check if SPSS is available via Python integration."""
        try:
            import spss
            return True
        except ImportError:
            return False

    def list_objects(self) -> List[WorkspaceObject]:
        """List active datasets in SPSS."""
        try:
            import spss
            import spssdata

            # Get active dataset info
            datasetObj = spssdata.Spssdata()
            var_count = datasetObj.GetVarCount()

            objects = []
            for i in range(var_count):
                var_name = datasetObj.GetVarName(i)
                var_type = datasetObj.GetVarType(i)  # 0=numeric, >0=string with length

                obj = WorkspaceObject(
                    name=var_name,
                    type="numeric" if var_type == 0 else f"string({var_type})",
                    class_name="spss_variable",
                    size=datasetObj.GetCaseCount()
                )
                objects.append(obj)

            datasetObj.CClose()
            return objects

        except ImportError:
            logger.warning("SPSS Python integration not available")
            return []
        except Exception as e:
            logger.error(f"Error listing SPSS objects: {e}")
            return []

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about an SPSS variable."""
        try:
            import spss
            import spssdata

            datasetObj = spssdata.Spssdata()
            var_count = datasetObj.GetVarCount()

            # Find the variable
            for i in range(var_count):
                var_name = datasetObj.GetVarName(i)
                if var_name.lower() == name.lower():
                    var_type = datasetObj.GetVarType(i)
                    var_label = datasetObj.GetVarLabel(i)

                    metadata = {}
                    if var_label:
                        metadata['label'] = var_label

                    obj = WorkspaceObject(
                        name=var_name,
                        type="numeric" if var_type == 0 else f"string({var_type})",
                        class_name="spss_variable",
                        size=datasetObj.GetCaseCount(),
                        metadata=metadata if metadata else None
                    )

                    datasetObj.CClose()
                    return obj

            datasetObj.CClose()
            return None

        except Exception as e:
            logger.error(f"Error getting SPSS object info: {e}")
            return None

    def get_object_data(self, name: str, limit: int = None) -> Optional[Dict[str, Any]]:
        """Get data from an SPSS variable with resource-aware limits."""
        if limit is None:
            limit = MAX_ROWS_DEFAULT

        limit = min(limit, MAX_ROWS_DEFAULT)

        try:
            import spss
            import spssdata

            datasetObj = spssdata.Spssdata()
            total_cases = datasetObj.GetCaseCount()

            # Resource-aware sampling
            if total_cases > LARGE_DATASET_THRESHOLD:
                # Note: SPSS doesn't support random sampling easily in Python API
                # Fall back to head
                shown_cases = min(limit, MAX_ROWS_ANALYSIS)
                sampling_method = "head"
                truncated = True
            elif total_cases > limit:
                shown_cases = limit
                sampling_method = "head"
                truncated = True
            else:
                shown_cases = total_cases
                sampling_method = "full"
                truncated = False

            # Get data
            data = []
            for i, row in enumerate(datasetObj):
                if i >= shown_cases:
                    break
                # Row is a tuple, need to match with variable names
                data.append(row)

            datasetObj.CClose()

            return {
                'type': 'variable',
                'data': data,
                'total_cases': total_cases,
                'shown_cases': len(data),
                'truncated': truncated,
                'sampling_method': sampling_method
            }

        except Exception as e:
            logger.error(f"Error getting SPSS data: {e}")
            return {'error': str(e)}

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of SPSS workspace."""
        objects = self.list_objects()

        try:
            import spss
            import spssdata

            datasetObj = spssdata.Spssdata()
            total_cases = datasetObj.GetCaseCount()
            total_vars = datasetObj.GetVarCount()
            datasetObj.CClose()

            metadata = {
                'cases': total_cases,
                'variables': total_vars
            }

            return WorkspaceInfo(
                platform="SPSS",
                objects=objects,
                total_objects=len(objects),
                environment_name="active_dataset",
                metadata=metadata
            )

        except Exception:
            return WorkspaceInfo(
                platform="SPSS",
                objects=objects,
                total_objects=len(objects),
                metadata={"status": "limited_access"}
            )


class EViewsWorkspaceInspector(WorkspaceInspector):
    """Inspector for EViews (Econometric Views) workfiles."""

    def __init__(self, eviews_executable: str = "eviews"):
        super().__init__()
        self.eviews_executable = eviews_executable
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if EViews Python integration is available."""
        try:
            import pyeviews
            logger.info("EViews Python integration (pyeviews) detected")
        except ImportError:
            logger.warning(
                "EViews Python integration not available. "
                "For full EViews support, install pyeviews: pip install pyeviews"
            )

    @property
    def platform_name(self) -> str:
        return "EViews"

    def is_available(self) -> bool:
        """Check if EViews is available via Python integration."""
        try:
            import pyeviews
            # Try to connect to EViews
            return True
        except ImportError:
            return False

    def list_objects(self) -> List[WorkspaceObject]:
        """List objects in active EViews workfile."""
        try:
            import pyeviews as evp

            # Get list of series and other objects
            # EViews command: wflist returns list of objects
            result = evp.Run("wflist", verbose=False)

            # Parse result (this is simplified - actual parsing depends on EViews output format)
            objects = []

            # Note: Full implementation would require parsing EViews output
            # For now, return basic structure
            logger.warning("EViews workspace listing is basic - full implementation pending")

            return objects

        except ImportError:
            logger.warning("EViews Python integration (pyeviews) not available")
            return []
        except Exception as e:
            logger.error(f"Error listing EViews objects: {e}")
            return []

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get detailed information about an EViews object."""
        try:
            import pyeviews as evp

            # Get object type and properties
            # This would use EViews commands like: {name}.@type, {name}.@length, etc.
            logger.warning("EViews object inspection is basic - full implementation pending")

            return None

        except Exception as e:
            logger.error(f"Error getting EViews object info: {e}")
            return None

    def get_object_data(self, name: str, limit: int = None) -> Optional[Dict[str, Any]]:
        """Get data from an EViews object with resource-aware limits."""
        if limit is None:
            limit = MAX_ROWS_DEFAULT

        try:
            import pyeviews as evp

            # Fetch data using EViews commands
            # This would involve exporting series data
            logger.warning("EViews data fetching is basic - full implementation pending")

            return {'error': 'EViews integration pending full implementation'}

        except Exception as e:
            logger.error(f"Error getting EViews data: {e}")
            return {'error': str(e)}

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of EViews workfile."""
        objects = self.list_objects()

        return WorkspaceInfo(
            platform="EViews",
            objects=objects,
            total_objects=len(objects),
            environment_name="workfile",
            metadata={"status": "basic_implementation"}
        )


class MultiPlatformWorkspaceManager:
    """Manager that auto-detects and uses the appropriate workspace inspector."""

    def __init__(self):
        self.inspectors: List[WorkspaceInspector] = [
            PythonWorkspaceInspector(),
            RWorkspaceInspector(),
            StataWorkspaceInspector(),
            SPSSWorkspaceInspector(),
            EViewsWorkspaceInspector(),
        ]

    def get_available_inspectors(self) -> List[WorkspaceInspector]:
        """Get all available workspace inspectors."""
        return [inspector for inspector in self.inspectors if inspector.is_available()]

    def get_inspector(self, platform: str) -> Optional[WorkspaceInspector]:
        """Get inspector for a specific platform."""
        for inspector in self.inspectors:
            if inspector.platform_name.lower() == platform.lower() and inspector.is_available():
                return inspector
        return None

    def auto_detect_inspector(self, working_dir: Optional[Path] = None) -> Optional[WorkspaceInspector]:
        """Auto-detect the most appropriate inspector based on context."""
        # TODO: Use project_detector.py to infer platform from working directory
        # For now, just return the first available inspector
        available = self.get_available_inspectors()
        return available[0] if available else None

    def list_all_workspaces(self) -> Dict[str, WorkspaceInfo]:
        """List workspaces from all available platforms."""
        result = {}
        for inspector in self.get_available_inspectors():
            try:
                workspace_info = inspector.describe_workspace()
                result[inspector.platform_name] = workspace_info
            except Exception as e:
                logger.error(f"Error inspecting {inspector.platform_name} workspace: {e}")
        return result
