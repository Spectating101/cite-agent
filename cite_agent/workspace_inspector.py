"""
Workspace Inspector - Multi-platform in-memory data access for data analysis environments.

This module provides a unified interface for accessing in-memory data objects across
different statistical and data analysis platforms (R, Stata, Python/Jupyter, etc.).

The key insight: Data analysts work with floating data in memory. Without access to
these objects, a citation agent cannot provide contextually relevant citations for
the actual analysis being performed.
"""

import json
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


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


class RWorkspaceInspector(WorkspaceInspector):
    """Inspector for R environments (.GlobalEnv)."""

    def __init__(self, r_executable: str = "Rscript"):
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

    def get_object_data(self, name: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get actual data from an object."""
        code = f"""
        if (!requireNamespace("jsonlite", quietly = TRUE)) {{
            cat("{{}}")
        }} else {{
            if (!exists("{name}", envir = .GlobalEnv)) {{
                cat("{{}}")
            }} else {{
                obj <- get("{name}", envir = .GlobalEnv)

                if (is.data.frame(obj)) {{
                    # Limit rows for large dataframes
                    if (nrow(obj) > {limit}) {{
                        obj_preview <- head(obj, {limit})
                        truncated <- TRUE
                    }} else {{
                        obj_preview <- obj
                        truncated <- FALSE
                    }}

                    result <- list(
                        type = "dataframe",
                        data = obj_preview,
                        total_rows = nrow(obj),
                        shown_rows = nrow(obj_preview),
                        truncated = truncated
                    )
                }} else if (is.vector(obj)) {{
                    if (length(obj) > {limit}) {{
                        obj_preview <- head(obj, {limit})
                        truncated <- TRUE
                    }} else {{
                        obj_preview <- obj
                        truncated <- FALSE
                    }}

                    result <- list(
                        type = "vector",
                        data = obj_preview,
                        total_length = length(obj),
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
            return json.loads(output)
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
        """List dataset variables in memory."""
        # TODO: Implement Stata variable listing
        # This requires executing Stata commands to describe the dataset
        logger.warning("Stata workspace inspection not fully implemented yet")
        return []

    def get_object_info(self, name: str) -> Optional[WorkspaceObject]:
        """Get information about a Stata variable."""
        logger.warning("Stata workspace inspection not fully implemented yet")
        return None

    def get_object_data(self, name: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get data from a Stata variable."""
        logger.warning("Stata workspace inspection not fully implemented yet")
        return None

    def describe_workspace(self) -> WorkspaceInfo:
        """Get summary of Stata workspace."""
        logger.warning("Stata workspace inspection not fully implemented yet")
        return WorkspaceInfo(
            platform="Stata",
            objects=[],
            total_objects=0,
            metadata={"status": "not_implemented"}
        )


class PythonWorkspaceInspector(WorkspaceInspector):
    """Inspector for Python/Jupyter environments."""

    def __init__(self):
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

    def get_object_data(self, name: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get actual data from a Python object."""
        if self._namespace is None:
            import __main__
            namespace = vars(__main__)
        else:
            namespace = self._namespace

        if name not in namespace:
            return None

        obj = namespace[name]

        try:
            # Pandas DataFrame
            if hasattr(obj, 'shape') and hasattr(obj, 'columns'):
                total_rows = len(obj)
                truncated = total_rows > limit
                data_preview = obj.head(limit)

                return {
                    'type': 'dataframe',
                    'data': data_preview.to_dict(orient='records'),
                    'columns': list(obj.columns),
                    'total_rows': total_rows,
                    'shown_rows': len(data_preview),
                    'truncated': truncated
                }
            # List/tuple
            elif isinstance(obj, (list, tuple)):
                total_length = len(obj)
                truncated = total_length > limit
                data_preview = obj[:limit]

                return {
                    'type': 'list',
                    'data': data_preview,
                    'total_length': total_length,
                    'shown_length': len(data_preview),
                    'truncated': truncated
                }
            # Other objects
            else:
                return {
                    'type': 'other',
                    'preview': str(obj)[:1000]
                }
        except Exception as e:
            logger.error(f"Error getting Python object data: {e}")
            return None

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


class MultiPlatformWorkspaceManager:
    """Manager that auto-detects and uses the appropriate workspace inspector."""

    def __init__(self):
        self.inspectors: List[WorkspaceInspector] = [
            PythonWorkspaceInspector(),
            RWorkspaceInspector(),
            StataWorkspaceInspector(),
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
