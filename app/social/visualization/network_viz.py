"""Obsidian-style PyVis graph engine."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from app.social.visualization.utils import node_color, node_tooltip, power_law_size


class NetworkVizBuilder:
    """Build stable, pruned, interactive PyVis story maps."""

    def __init__(self, edge_threshold: float = 0.5, max_nodes: int = 900):
        self.edge_threshold = edge_threshold
        self.max_nodes = max_nodes

    def export_html(self, G: nx.Graph, output_path: Path) -> Path:
        from pyvis.network import Network

        graph = self._prepare_graph(G)
        network = Network(height="760px", width="100%", bgcolor="#0f1218", font_color="#f4f4f5")
        network.set_options(self._options())

        for node, attrs in graph.nodes(data=True):
            degree = graph.degree(node)
            prominence = float(attrs.get("degree_centrality", 0) or 0)
            entity_type = attrs.get("entity_type", "unknown")
            network.add_node(
                node,
                label=node,
                title=node_tooltip(node, attrs, degree),
                color=node_color(entity_type),
                size=power_law_size(prominence, degree),
                group=str(attrs.get("community_name", "Unassigned theme")),
                borderWidth=1,
            )

        for u, v, attrs in graph.edges(data=True):
            weight = float(attrs.get("weight", 1.0) or 1.0)
            network.add_edge(
                u,
                v,
                id=f"{u}__{v}",
                value=weight,
                width=max(0.4, min(4.5, weight)),
                title=f"Connection strength: {weight:.2f}",
                color={"color": "#556070", "opacity": 0.42},
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        network.write_html(str(output_path), open_browser=False, notebook=False)
        self._inject_focus_mode(output_path)
        return output_path

    def _prepare_graph(self, G: nx.Graph) -> nx.Graph:
        graph = self._sample_graph(G)
        remove_edges = [
            (u, v)
            for u, v, attrs in graph.edges(data=True)
            if float(attrs.get("weight", 0) or 0) <= self.edge_threshold
        ]
        graph.remove_edges_from(remove_edges)
        isolates = list(nx.isolates(graph))
        if graph.number_of_nodes() > 40:
            graph.remove_nodes_from(isolates)
        return graph

    def _sample_graph(self, G: nx.Graph) -> nx.Graph:
        if G.number_of_nodes() <= self.max_nodes:
            return G.copy()
        scores = dict(G.degree(weight="weight"))
        keep = {
            node
            for node, _ in sorted(scores.items(), key=lambda item: -item[1])[: self.max_nodes]
        }
        return G.subgraph(keep).copy()

    @staticmethod
    def _options() -> str:
        return """
        {
          "nodes": {
            "shape": "dot",
            "font": {"size": 15, "face": "Inter, Arial", "color": "#f4f4f5"},
            "borderWidth": 1
          },
          "edges": {
            "smooth": {"type": "continuous"},
            "color": {"inherit": false}
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 80,
            "navigationButtons": true,
            "keyboard": true
          },
          "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -55,
              "centralGravity": 0.008,
              "springLength": 120,
              "springConstant": 0.055,
              "damping": 0.72,
              "avoidOverlap": 0.55
            },
            "maxVelocity": 50,
            "minVelocity": 0.75,
            "stabilization": {
              "enabled": true,
              "iterations": 200,
              "updateInterval": 20,
              "fit": true
            }
          }
        }
        """

    @staticmethod
    def _inject_focus_mode(path: Path) -> None:
        html = path.read_text(encoding="utf-8")
        controls = """
<style>
  .hen-controls{position:fixed;top:16px;left:16px;z-index:9999;background:#171b24;border:1px solid #2c3342;border-radius:8px;padding:12px;width:300px;color:#f4f4f5;font-family:Inter,Arial,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.28)}
  .hen-controls input{width:100%;box-sizing:border-box;background:#0f1218;color:#f4f4f5;border:1px solid #343c4d;border-radius:6px;padding:8px;margin-top:6px}
  .hen-controls button{background:#d6a84f;color:#111827;border:0;border-radius:6px;padding:7px 10px;margin-top:8px;cursor:pointer}
  .hen-controls .hint{font-size:11px;color:#aab2c0;margin-top:8px;line-height:1.35}
</style>
<div class="hen-controls">
  <strong>Story Map Focus</strong>
  <input id="hen-search" placeholder="Search an idea..." />
  <button onclick="henSearchNode()">Focus idea</button>
  <button onclick="henResetFocus()">Reset</button>
  <div class="hint">Click any dot to highlight its neighbors and dim the rest.</div>
</div>
<script>
function henDimExcept(selectedId){
  if(!window.network || !window.nodes || !window.edges) return;
  const connected = new Set(network.getConnectedNodes(selectedId));
  connected.add(selectedId);
  nodes.update(nodes.get().map(n => ({
    id:n.id,
    color: connected.has(n.id) ? n.color : {background:'#2a3140', border:'#394153'},
    font: {color: connected.has(n.id) ? '#f4f4f5' : '#6b7280'}
  })));
  edges.update(edges.get().map(e => ({
    id:e.id,
    color: connected.has(e.from) && connected.has(e.to) ? {color:'#d6a84f', opacity:.9} : {color:'#303848', opacity:.12}
  })));
}
function henResetFocus(){
  location.reload();
}
function henSearchNode(){
  const query = document.getElementById('hen-search').value.toLowerCase();
  if(!query || !window.network || !window.nodes) return;
  const all = nodes.get();
  const match = all.find(n => String(n.label || n.id).toLowerCase().includes(query));
  if(match){
    network.selectNodes([match.id]);
    network.focus(match.id, {scale: 1.35, animation: true});
    henDimExcept(match.id);
  }
}
setTimeout(() => {
  if(window.network){
    network.on("selectNode", params => {
      if(params.nodes && params.nodes.length){ henDimExcept(params.nodes[0]); }
    });
    network.on("deselectNode", () => henResetFocus());
  }
}, 500);
</script>
"""
        html = html.replace("<body>", f"<body>{controls}", 1)
        path.write_text(html, encoding="utf-8")
