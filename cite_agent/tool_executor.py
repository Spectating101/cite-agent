"""
Tool executor for Cite-Agent function calling.

Executes tools requested by the LLM and returns structured results.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ToolExecutor:
    """
    Executes tools requested via function calling.

    This class bridges between the function calling layer and the existing
    agent capabilities (Archive API, FinSight API, shell, etc.)
    """

    def __init__(self, agent):
        """
        Initialize tool executor.

        Args:
            agent: EnhancedNocturnalAgent instance (for accessing APIs, shell, etc.)
        """
        self.agent = agent
        self.debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool and return results.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from LLM

        Returns:
            Dict with tool results or error
        """
        if self.debug_mode:
            print(f"🔧 [Tool Executor] Executing: {tool_name}({json.dumps(arguments)[:100]}...)")

        try:
            if tool_name == "search_papers":
                return await self._execute_search_papers(arguments)
            elif tool_name == "get_financial_data":
                return await self._execute_get_financial_data(arguments)
            elif tool_name == "web_search":
                return await self._execute_web_search(arguments)
            elif tool_name == "list_directory":
                return self._execute_list_directory(arguments)
            elif tool_name == "read_file":
                return self._execute_read_file(arguments)
            elif tool_name == "write_file":
                return self._execute_write_file(arguments)
            elif tool_name == "execute_shell_command":
                return self._execute_shell_command(arguments)
            elif tool_name == "export_to_zotero":
                return self._execute_export_to_zotero(arguments)
            elif tool_name == "find_related_papers":
                return await self._execute_find_related_papers(arguments)
            elif tool_name == "chat":
                return self._execute_chat(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            if self.debug_mode:
                print(f"❌ [Tool Executor] Error executing {tool_name}: {e}")
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    async def _execute_search_papers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search_papers tool"""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        sources = args.get("sources", ["semantic_scholar", "openalex"])  # For logging only

        if not query:
            return {"error": "Missing required parameter: query"}

        if self.debug_mode:
            print(f"📚 [Archive API] Searching: {query} (limit={limit}, sources={sources})")

        # Call Archive API via agent
        # Note: search_academic_papers has built-in source fallback, doesn't accept sources param
        try:
            results = await self.agent.search_academic_papers(
                query=query,
                limit=limit
            )

            if self.debug_mode:
                papers = results.get("results", [])
                print(f"📚 [Archive API] Found {len(papers)} papers")

            return {
                "papers": results.get("results", []),
                "count": len(results.get("results", [])),
                "query": query,
                "sources_tried": results.get("sources_tried", [])
            }

        except Exception as e:
            return {"error": f"Archive API error: {str(e)}"}

    async def _execute_get_financial_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get_financial_data tool"""
        ticker = args.get("ticker", "").upper()
        metrics = args.get("metrics", ["revenue", "profit", "market_cap"])

        if not ticker:
            return {"error": "Missing required parameter: ticker"}

        if self.debug_mode:
            print(f"💰 [FinSight API] Getting data for {ticker}: {metrics}")

        # Call FinSight API via agent
        try:
            results = await self.agent.get_financial_metrics(
                ticker=ticker,
                metrics=metrics
            )

            if self.debug_mode:
                print(f"💰 [FinSight API] Retrieved {len(results)} metrics")

            return {
                "ticker": ticker,
                "data": results,
                "company_name": ticker  # get_financial_metrics doesn't return company name
            }

        except Exception as e:
            return {"error": f"FinSight API error: {str(e)}"}

    async def _execute_web_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web_search tool"""
        query = args.get("query", "")
        num_results = args.get("num_results", 5)

        if not query:
            return {"error": "Missing required parameter: query"}

        if self.debug_mode:
            print(f"🌐 [Web Search] Searching: {query} (num_results={num_results})")

        # Call web search via agent
        try:
            results = await self.agent.web_search.search_web(
                query=query,
                num_results=num_results
            )

            if self.debug_mode:
                print(f"🌐 [Web Search] Found {len(results.get('results', []))} results")

            return {
                "results": results.get("results", []),
                "count": len(results.get("results", [])),
                "query": query
            }

        except Exception as e:
            return {"error": f"Web search error: {str(e)}"}

    def _execute_list_directory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list_directory tool"""
        path = args.get("path", ".")
        show_hidden = args.get("show_hidden", False)

        if self.debug_mode:
            print(f"📁 [List Directory] Path: {path}, show_hidden: {show_hidden}")

        # Use shell command to list directory
        try:
            if self.agent.shell_session:
                if show_hidden:
                    command = f"ls -lah {path}"
                else:
                    command = f"ls -lh {path}"

                output = self.agent.execute_command(command)

                if self.debug_mode:
                    print(f"📁 [List Directory] Got {len(output)} chars of output")

                return {
                    "path": path,
                    "listing": output,
                    "command": command
                }
            else:
                # Fallback to Python's pathlib
                path_obj = Path(path).expanduser()
                if not path_obj.exists():
                    return {"error": f"Path does not exist: {path}"}

                if not path_obj.is_dir():
                    return {"error": f"Not a directory: {path}"}

                entries = []
                for entry in path_obj.iterdir():
                    if not show_hidden and entry.name.startswith('.'):
                        continue
                    entries.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "is_file": entry.is_file()
                    })

                listing = "\n".join([
                    f"{'[DIR]' if e['is_dir'] else '[FILE]'} {e['name']}"
                    for e in entries
                ])

                return {
                    "path": str(path_obj),
                    "listing": listing,
                    "entries": entries
                }

        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}

    def _execute_read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute read_file tool"""
        file_path = args.get("file_path", "")
        lines = args.get("lines", -1)

        if not file_path:
            return {"error": "Missing required parameter: file_path"}

        if self.debug_mode:
            print(f"📄 [Read File] Path: {file_path}, lines: {lines}")

        try:
            path_obj = Path(file_path).expanduser()
            if not path_obj.exists():
                return {"error": f"File does not exist: {file_path}"}

            if not path_obj.is_file():
                return {"error": f"Not a file: {file_path}"}

            with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                if lines > 0:
                    content = ''.join(f.readlines()[:lines])
                else:
                    content = f.read()

            if self.debug_mode:
                print(f"📄 [Read File] Read {len(content)} characters")

            return {
                "file_path": str(path_obj),
                "content": content,
                "lines_read": len(content.split('\n'))
            }

        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _execute_write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute write_file tool"""
        file_path = args.get("file_path", "")
        content = args.get("content", "")
        overwrite = args.get("overwrite", False)

        if not file_path:
            return {"error": "Missing required parameter: file_path"}

        if self.debug_mode:
            print(f"✏️  [Write File] Path: {file_path}, overwrite: {overwrite}, content_len: {len(content)}")

        try:
            path_obj = Path(file_path).expanduser()

            if path_obj.exists() and not overwrite:
                return {"error": f"File already exists (use overwrite=true): {file_path}"}

            # Create parent directories if needed
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)

            if self.debug_mode:
                print(f"✏️  [Write File] Wrote {len(content)} characters")

            return {
                "file_path": str(path_obj),
                "bytes_written": len(content.encode('utf-8')),
                "success": True
            }

        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    def _execute_shell_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute execute_shell_command tool"""
        command = args.get("command", "")
        working_directory = args.get("working_directory", ".")

        if not command:
            return {"error": "Missing required parameter: command"}

        if self.debug_mode:
            print(f"⚙️  [Shell Command] Executing: {command} (cwd: {working_directory})")

        # Safety check
        if not self.agent.shell_session:
            return {"error": "Shell session not available"}

        # Classify command safety
        safety_level = self.agent._classify_command_safety(command)
        if safety_level in ('BLOCKED', 'DANGEROUS'):
            return {
                "error": f"Command blocked for safety: {command}",
                "safety_level": safety_level
            }

        try:
            # Change directory if needed
            if working_directory and working_directory != ".":
                cd_command = f"cd {working_directory} 2>/dev/null && pwd"
                cd_output = self.agent.execute_command(cd_command)
                if "ERROR" in cd_output:
                    return {"error": f"Failed to change directory: {working_directory}"}

            # Execute command
            output = self.agent.execute_command(command)

            if self.debug_mode:
                print(f"⚙️  [Shell Command] Output: {len(output)} characters")

            return {
                "command": command,
                "output": output,
                "working_directory": working_directory,
                "success": "ERROR" not in output
            }

        except Exception as e:
            return {"error": f"Failed to execute command: {str(e)}"}

    def _execute_export_to_zotero(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute export_to_zotero tool"""
        papers = args.get("papers", [])
        format_type = args.get("format", "bibtex").lower()
        filename = args.get("filename")

        if not papers:
            return {"error": "No papers provided to export"}

        if self.debug_mode:
            print(f"📚 [Zotero Export] Exporting {len(papers)} papers to {format_type}")

        try:
            from datetime import datetime

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cite_agent_export_{timestamp}.{format_type}"

            # Ensure correct extension
            if not filename.endswith(f".{format_type}"):
                filename = f"{filename}.{format_type}"

            output_path = Path(filename).expanduser()

            if format_type == "bibtex":
                content = self._generate_bibtex(papers)
            elif format_type == "ris":
                content = self._generate_ris(papers)
            else:
                return {"error": f"Unsupported format: {format_type}"}

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if self.debug_mode:
                print(f"📚 [Zotero Export] Exported to {output_path}")

            return {
                "success": True,
                "filename": str(output_path),
                "format": format_type,
                "papers_count": len(papers),
                "message": f"Exported {len(papers)} papers to {output_path}. Import this file in Zotero via File → Import."
            }

        except Exception as e:
            return {"error": f"Export failed: {str(e)}"}

    def _generate_bibtex(self, papers: list) -> str:
        """Generate BibTeX content from papers"""
        from datetime import datetime

        content = f"% Generated by Cite-Agent\n"
        content += f"% Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for paper in papers:
            # Generate citation key
            title = paper.get('title', 'Unknown')
            authors_raw = paper.get('authors', [])
            year = paper.get('year', 'YEAR')

            # Normalize authors - handle both string list and dict list formats
            authors = []
            for author in authors_raw:
                if isinstance(author, dict):
                    authors.append(author.get('name', ''))
                elif isinstance(author, str):
                    authors.append(author)

            first_author = authors[0].split()[-1] if authors else "Unknown"
            title_word = title.split()[0] if title else "Paper"
            citation_key = f"{first_author}{year}{title_word}".replace(" ", "").replace(",", "").replace(":", "")

            # Build BibTeX entry
            content += f"@article{{{citation_key},\n"
            content += f"  title = {{{title}}},\n"

            if authors:
                authors_str = " and ".join(authors)
                content += f"  author = {{{authors_str}}},\n"

            content += f"  year = {{{year}}},\n"

            if 'venue' in paper and paper['venue']:
                content += f"  journal = {{{paper['venue']}}},\n"

            if 'doi' in paper and paper['doi']:
                content += f"  doi = {{{paper['doi']}}},\n"

            if 'url' in paper and paper['url']:
                content += f"  url = {{{paper['url']}}},\n"

            if 'abstract' in paper and paper['abstract']:
                abstract = paper['abstract'].replace("\n", " ").replace("{", "").replace("}", "")[:500]
                content += f"  abstract = {{{abstract}...}},\n"

            content += "}\n\n"

        return content

    def _generate_ris(self, papers: list) -> str:
        """Generate RIS content from papers (Zotero also supports this)"""
        content = ""

        for paper in papers:
            content += "TY  - JOUR\n"  # Journal article type

            title = paper.get('title', '')
            if title:
                content += f"TI  - {title}\n"

            authors_raw = paper.get('authors', [])
            # Normalize authors - handle both string list and dict list formats
            for author in authors_raw:
                if isinstance(author, dict):
                    author_name = author.get('name', '')
                elif isinstance(author, str):
                    author_name = author
                else:
                    continue
                if author_name:
                    content += f"AU  - {author_name}\n"

            year = paper.get('year', '')
            if year:
                content += f"PY  - {year}\n"

            venue = paper.get('venue', '')
            if venue:
                content += f"JO  - {venue}\n"

            doi = paper.get('doi', '')
            if doi:
                content += f"DO  - {doi}\n"

            url = paper.get('url', '')
            if url:
                content += f"UR  - {url}\n"

            abstract = paper.get('abstract', '')
            if abstract:
                content += f"AB  - {abstract}\n"

            content += "ER  - \n\n"

        return content

    async def _execute_find_related_papers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find_related_papers tool"""
        paper_id = args.get("paper_id", "")
        method = args.get("method", "similar")
        limit = args.get("limit", 10)

        if not paper_id:
            return {"error": "Missing required parameter: paper_id"}

        if self.debug_mode:
            print(f"🔗 [Related Papers] Finding related papers for: {paper_id} (method: {method})")

        try:
            # Use Archive API to find related papers
            # This typically works by searching for the paper first, then getting related papers
            result = await self.agent.search_academic_papers(
                query=paper_id,
                limit=1,
                sources=['semantic_scholar', 'openalex']
            )

            if 'error' in result or result.get('papers_count', 0) == 0:
                # If we can't find the exact paper, search for similar ones
                related_result = await self.agent.search_academic_papers(
                    query=f"related to {paper_id}",
                    limit=limit,
                    sources=['semantic_scholar', 'openalex']
                )

                return {
                    "method": "similar_search",
                    "query": paper_id,
                    "related_papers": related_result.get('papers', []),
                    "count": len(related_result.get('papers', [])),
                    "note": "Found papers related to the query (exact paper match not found)"
                }

            # Got the paper, now find related ones based on method
            base_paper = result['papers'][0]

            if method == "citations":
                # Papers that cite this paper
                query = f"cites:{base_paper.get('title', paper_id)}"
            elif method == "references":
                # Papers referenced by this paper
                query = f"references:{base_paper.get('title', paper_id)}"
            else:  # similar
                # Papers with similar topics/keywords
                query = f"{base_paper.get('title', paper_id)} similar research"

            related_result = await self.agent.search_academic_papers(
                query=query,
                limit=limit,
                sources=['semantic_scholar', 'openalex']
            )

            if self.debug_mode:
                print(f"🔗 [Related Papers] Found {len(related_result.get('papers', []))} related papers")

            return {
                "method": method,
                "base_paper": {
                    "title": base_paper.get('title'),
                    "authors": base_paper.get('authors', []),
                    "year": base_paper.get('year'),
                    "citations": base_paper.get('citations_count', 0)
                },
                "related_papers": related_result.get('papers', []),
                "count": len(related_result.get('papers', [])),
                "message": f"Found {len(related_result.get('papers', []))} papers {method} '{base_paper.get('title', paper_id)}'"
            }

        except Exception as e:
            return {"error": f"Failed to find related papers: {str(e)}"}

    def _execute_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat tool (pure conversational response)"""
        message = args.get("message", "")

        if self.debug_mode:
            print(f"💬 [Chat] Conversational response: {message[:100]}...")

        # Chat tool just returns the message directly
        # The LLM has already generated the response in the 'message' parameter
        return {
            "message": message,
            "type": "conversational"
        }
