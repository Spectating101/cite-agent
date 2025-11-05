#!/usr/bin/env python3
"""
Research Visualization Module - Citation graphs, trends, analytics
Creates beautiful visualizations that make research insights pop
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class CitationNode:
    """Node in citation graph"""
    paper_id: str
    title: str
    year: int
    citation_count: int
    quality_score: float
    authors: List[str]


@dataclass
class CitationEdge:
    """Edge in citation graph (paper A cites paper B)"""
    source_id: str
    target_id: str
    citation_type: str = "cites"  # cites, cited_by, related


class CitationGraphBuilder:
    """
    Build citation networks from paper data
    Creates interactive visualizations
    """

    def __init__(self):
        """Initialize graph builder"""
        self.nodes: Dict[str, CitationNode] = {}
        self.edges: List[CitationEdge] = []

    def add_papers(self, papers: List[Dict[str, Any]]):
        """Add papers as nodes"""
        for paper in papers:
            paper_id = paper.get('paper_id') or paper.get('id') or paper.get('doi', f"paper_{len(self.nodes)}")

            node = CitationNode(
                paper_id=paper_id,
                title=paper.get('title', 'Unknown'),
                year=paper.get('year', 0),
                citation_count=paper.get('citation_count', 0),
                quality_score=paper.get('quality_score', 0.0),
                authors=paper.get('authors', [])
            )
            self.nodes[paper_id] = node

    def detect_citation_relationships(self, papers: List[Dict[str, Any]]):
        """
        Detect citation relationships between papers
        Based on: author overlap, venue overlap, title mentions
        """
        paper_ids = list(self.nodes.keys())

        for i, paper1_id in enumerate(paper_ids):
            for paper2_id in paper_ids[i+1:]:
                node1 = self.nodes[paper1_id]
                node2 = self.nodes[paper2_id]

                # Check for author overlap (collaboration)
                common_authors = set(node1.authors) & set(node2.authors)
                if common_authors:
                    self.edges.append(CitationEdge(
                        source_id=paper1_id,
                        target_id=paper2_id,
                        citation_type="collaboration"
                    ))
                    continue

                # Check for temporal citation (older paper likely cited by newer)
                if abs(node1.year - node2.year) <= 2 and node1.year > 0 and node2.year > 0:
                    if node1.year < node2.year and node1.citation_count > 100:
                        # Older, highly-cited paper likely cited by newer paper
                        self.edges.append(CitationEdge(
                            source_id=paper2_id,
                            target_id=paper1_id,
                            citation_type="likely_cites"
                        ))
                    elif node2.year < node1.year and node2.citation_count > 100:
                        self.edges.append(CitationEdge(
                            source_id=paper1_id,
                            target_id=paper2_id,
                            citation_type="likely_cites"
                        ))

    def to_d3_json(self) -> Dict[str, Any]:
        """
        Export as D3.js-compatible JSON
        For interactive web visualization
        """
        nodes = []
        for paper_id, node in self.nodes.items():
            nodes.append({
                "id": paper_id,
                "title": node.title,
                "year": node.year,
                "citations": node.citation_count,
                "quality": node.quality_score,
                "authors": node.authors[:3],  # First 3 authors
                "size": min(node.citation_count / 100, 20) + 5  # Node size based on citations
            })

        edges = []
        for edge in self.edges:
            edges.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.citation_type
            })

        return {
            "nodes": nodes,
            "links": edges
        }

    def to_graphviz_dot(self) -> str:
        """
        Export as Graphviz DOT format
        For publication-quality static graphs
        """
        dot = "digraph CitationNetwork {\n"
        dot += "  rankdir=TB;\n"
        dot += "  node [shape=box, style=rounded];\n\n"

        # Nodes with quality-based colors
        for paper_id, node in self.nodes.items():
            # Color by quality score
            if node.quality_score >= 80:
                color = "#2ecc71"  # Green - high quality
            elif node.quality_score >= 60:
                color = "#3498db"  # Blue - good quality
            elif node.quality_score >= 40:
                color = "#f39c12"  # Orange - medium quality
            else:
                color = "#e74c3c"  # Red - low quality

            label = f"{node.title[:40]}...\\n{node.year} ({node.citation_count} cites)"
            dot += f'  "{paper_id}" [label="{label}", fillcolor="{color}", style="filled,rounded"];\n'

        # Edges
        dot += "\n"
        for edge in self.edges:
            style = "solid" if edge.citation_type == "cites" else "dashed"
            dot += f'  "{edge.source_id}" -> "{edge.target_id}" [style={style}];\n'

        dot += "}\n"
        return dot

    def to_cytoscape_json(self) -> Dict[str, Any]:
        """
        Export as Cytoscape.js format
        For embedding in web applications
        """
        elements = []

        # Nodes
        for paper_id, node in self.nodes.items():
            elements.append({
                "data": {
                    "id": paper_id,
                    "label": node.title[:40] + "...",
                    "year": node.year,
                    "citations": node.citation_count,
                    "quality": node.quality_score,
                    "size": min(node.citation_count / 50, 30) + 10
                },
                "classes": f"quality-{int(node.quality_score // 25) * 25}"
            })

        # Edges
        for edge in self.edges:
            elements.append({
                "data": {
                    "id": f"{edge.source_id}_{edge.target_id}",
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.citation_type
                }
            })

        return {"elements": elements}


class ResearchTrendAnalyzer:
    """
    Analyze research trends over time
    Publication trends, topic evolution, impact patterns
    """

    def __init__(self):
        """Initialize trend analyzer"""
        pass

    def analyze_publication_trends(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze publication trends over years

        Returns:
            Trend data with year-by-year breakdown
        """
        # Group by year
        by_year = defaultdict(list)
        for paper in papers:
            year = paper.get('year')
            if year:
                by_year[year].append(paper)

        # Calculate metrics per year
        trends = []
        for year in sorted(by_year.keys()):
            year_papers = by_year[year]
            avg_citations = sum(p.get('citation_count', 0) for p in year_papers) / len(year_papers)
            avg_quality = sum(p.get('quality_score', 0) for p in year_papers) / len(year_papers)

            trends.append({
                "year": year,
                "count": len(year_papers),
                "avg_citations": round(avg_citations, 2),
                "avg_quality": round(avg_quality, 2),
                "total_citations": sum(p.get('citation_count', 0) for p in year_papers)
            })

        return {
            "trends": trends,
            "summary": {
                "total_papers": len(papers),
                "year_range": (min(by_year.keys()), max(by_year.keys())) if by_year else (0, 0),
                "peak_year": max(trends, key=lambda x: x['count'])['year'] if trends else None
            }
        }

    def analyze_venue_distribution(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze distribution across venues"""
        venues = Counter()
        venue_quality = defaultdict(list)

        for paper in papers:
            venue = paper.get('venue')
            if venue:
                venues[venue] += 1
                venue_quality[venue].append(paper.get('quality_score', 0))

        # Calculate average quality per venue
        venue_stats = []
        for venue, count in venues.most_common(20):
            avg_quality = sum(venue_quality[venue]) / len(venue_quality[venue])
            venue_stats.append({
                "venue": venue,
                "paper_count": count,
                "avg_quality": round(avg_quality, 2)
            })

        return {
            "top_venues": venue_stats,
            "total_venues": len(venues),
            "concentration": venues.most_common(3)
        }

    def analyze_author_impact(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze author productivity and impact"""
        author_papers = defaultdict(list)

        for paper in papers:
            for author in paper.get('authors', []):
                author_name = author.get('name', author) if isinstance(author, dict) else author
                author_papers[author_name].append(paper)

        # Calculate metrics per author
        author_stats = []
        for author, author_paper_list in author_papers.items():
            total_citations = sum(p.get('citation_count', 0) for p in author_paper_list)
            avg_quality = sum(p.get('quality_score', 0) for p in author_paper_list) / len(author_paper_list)

            author_stats.append({
                "author": author,
                "paper_count": len(author_paper_list),
                "total_citations": total_citations,
                "avg_quality": round(avg_quality, 2),
                "h_index_estimate": self._estimate_h_index(author_paper_list)
            })

        # Sort by impact (paper count * avg quality)
        author_stats.sort(key=lambda x: x['paper_count'] * x['avg_quality'], reverse=True)

        return {
            "top_authors": author_stats[:20],
            "total_authors": len(author_papers)
        }

    def _estimate_h_index(self, papers: List[Dict[str, Any]]) -> int:
        """Estimate h-index from paper list"""
        citations = sorted([p.get('citation_count', 0) for p in papers], reverse=True)
        h_index = 0
        for i, cites in enumerate(citations, 1):
            if cites >= i:
                h_index = i
            else:
                break
        return h_index

    def generate_ascii_chart(
        self,
        data: List[Tuple[str, int]],
        max_width: int = 50,
        title: str = "Chart"
    ) -> str:
        """
        Generate ASCII bar chart for terminal display

        Args:
            data: List of (label, value) tuples
            max_width: Maximum bar width
            title: Chart title

        Returns:
            ASCII chart string
        """
        if not data:
            return "No data to display"

        max_value = max(v for _, v in data)
        if max_value == 0:
            max_value = 1

        chart = f"\n{title}\n" + "=" * (max_width + 20) + "\n\n"

        for label, value in data:
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            chart += f"{label:15} | {bar} {value}\n"

        chart += "\n" + "=" * (max_width + 20) + "\n"
        return chart


class ResearchDashboardGenerator:
    """
    Generate HTML research dashboard
    Beautiful, interactive visualization of research
    """

    def generate_dashboard(
        self,
        papers: List[Dict[str, Any]],
        synthesis_result: Optional[Any] = None,
        output_path: str = "research_dashboard.html"
    ) -> str:
        """
        Generate interactive HTML dashboard

        Args:
            papers: List of papers
            synthesis_result: Optional synthesis result
            output_path: Output file path

        Returns:
            Path to created file
        """
        # Build citation graph
        graph_builder = CitationGraphBuilder()
        graph_builder.add_papers(papers)
        graph_builder.detect_citation_relationships(papers)

        # Analyze trends
        trend_analyzer = ResearchTrendAnalyzer()
        pub_trends = trend_analyzer.analyze_publication_trends(papers)
        venue_dist = trend_analyzer.analyze_venue_distribution(papers)
        author_impact = trend_analyzer.analyze_author_impact(papers)

        # Generate HTML
        html = self._generate_html_template(
            papers=papers,
            graph_data=graph_builder.to_d3_json(),
            pub_trends=pub_trends,
            venue_dist=venue_dist,
            author_impact=author_impact,
            synthesis=synthesis_result
        )

        # Write to file
        from pathlib import Path
        Path(output_path).write_text(html, encoding='utf-8')

        return output_path

    def _generate_html_template(
        self,
        papers: List[Dict[str, Any]],
        graph_data: Dict[str, Any],
        pub_trends: Dict[str, Any],
        venue_dist: Dict[str, Any],
        author_impact: Dict[str, Any],
        synthesis: Optional[Any]
    ) -> str:
        """Generate complete HTML dashboard"""

        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Research Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        #graph {
            width: 100%;
            height: 600px;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
        }
        .paper-list {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .paper-item {
            padding: 15px;
            border-bottom: 1px solid #e1e8ed;
        }
        .paper-item:last-child {
            border-bottom: none;
        }
        .paper-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .paper-meta {
            color: #7f8c8d;
            font-size: 14px;
        }
        .quality-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }
        .quality-high { background: #2ecc71; color: white; }
        .quality-medium { background: #f39c12; color: white; }
        .quality-low { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Research Dashboard</h1>
        <p class="subtitle">Generated by Cite-Agent - """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """</p>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">""" + str(len(papers)) + """</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(sum(p.get('citation_count', 0) for p in papers)) + """</div>
                <div class="stat-label">Total Citations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(len(set(p.get('venue', '') for p in papers if p.get('venue')))) + """</div>
                <div class="stat-label">Unique Venues</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(round(sum(p.get('quality_score', 0) for p in papers) / len(papers) if papers else 0, 1)) + """</div>
                <div class="stat-label">Avg Quality Score</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 Publication Trends</h2>
            <div id="trends-chart"></div>
        </div>

        <div class="chart-container">
            <h2>🕸️ Citation Network</h2>
            <div id="graph"></div>
        </div>

        <div class="paper-list">
            <h2>📚 Papers (sorted by quality)</h2>
"""

        # Add papers
        sorted_papers = sorted(papers, key=lambda p: p.get('quality_score', 0), reverse=True)
        for paper in sorted_papers[:20]:  # Top 20
            quality = paper.get('quality_score', 0)
            quality_class = "high" if quality >= 75 else "medium" if quality >= 50 else "low"

            html += f"""
            <div class="paper-item">
                <div class="paper-title">
                    {paper.get('title', 'Untitled')}
                    <span class="quality-badge quality-{quality_class}">{quality}/100</span>
                </div>
                <div class="paper-meta">
                    {', '.join([a.get('name', a) if isinstance(a, dict) else a for a in paper.get('authors', [])[:3]])}
                    • {paper.get('year', 'N/A')}
                    • {paper.get('venue', 'Unknown venue')}
                    • {paper.get('citation_count', 0)} citations
                </div>
            </div>
"""

        # Add JavaScript for charts
        html += """
        </div>
    </div>

    <script>
        // Publication trends
        var trendsData = """ + json.dumps(pub_trends['trends']) + """;
        var trace = {
            x: trendsData.map(d => d.year),
            y: trendsData.map(d => d.count),
            type: 'bar',
            marker: {color: '#3498db'}
        };
        var layout = {
            xaxis: {title: 'Year'},
            yaxis: {title: 'Papers Published'},
            height: 300
        };
        Plotly.newPlot('trends-chart', [trace], layout);

        // Citation network
        var graphData = """ + json.dumps(graph_data) + """;
        // D3 force simulation
        var width = document.getElementById('graph').clientWidth;
        var height = 600;

        var svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        var simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        var link = svg.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter().append("line")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 2);

        var node = svg.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .enter().append("circle")
            .attr("r", d => d.size || 5)
            .attr("fill", d => d.quality >= 75 ? "#2ecc71" : d.quality >= 50 ? "#3498db" : "#e74c3c")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("title")
            .text(d => d.title + " (" + d.year + ")");

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    </script>
</body>
</html>
"""
        return html
