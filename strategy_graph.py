"""
Graph Memory Network Strategy

This strategy treats conversation elements as nodes and their relationships as edges,
enabling complex reasoning and relationship understanding. Particularly suited for
expert systems and knowledge base applications.
"""

import time
import networkx as nx
from typing import List, Dict, Any, Optional, Set
from openai import OpenAI
from memory_strategy_base import BaseMemoryStrategy
from memory_utils import generate_text, get_openai_client


class GraphMemory(BaseMemoryStrategy):
    """
    Graph-based memory strategy using NetworkX for relationship modeling.

    Advantages:
    - Models complex relationships between information
    - Supports logical reasoning queries
    - Structured knowledge representation
    - Excellent for expert systems

    Disadvantages:
    - Complex implementation and maintenance
    - Requires relationship extraction
    - May be overkill for simple conversations
    - Computational overhead for large graphs
    """

    STRATEGY_ID = "graph_knowledge"
    STRATEGY_NAME = "Graph Knowledge Memory"
    STRATEGY_CATEGORY = "Advanced"
    COMPLEXITY_LEVEL = "Very Complex"
    RECOMMENDED_USE_CASES = ["expert_systems", "relationship_modeling", "complex_reasoning"]
    UI_COLOR = "#6366F1"
    UI_ICON = "graph"

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize graph memory system.

        Args:
            client: Optional OpenAI client instance
        """
        self.client = client or get_openai_client()
        self.knowledge_graph = nx.DiGraph()
        self.node_counter = 0
        self.conversation_history: List[Dict[str, str]] = []
        self.entity_extraction_log: List[Dict[str, Any]] = []
        self.graph_metrics_cache: Dict[str, Any] = {}
        self.operation_log: List[Dict[str, Any]] = []

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """Log operation with [GRAPH] prefix."""
        self.operation_log.append({
            "type": op_type,
            "timestamp": time.time(),
            "details": details,
            "prefix": "GRAPH"
        })

    def _track_entity_extraction(self, entities: List[str], relationships: List[str], speaker: str) -> None:
        """Log entity and relationship additions."""
        self.entity_extraction_log.append({
            "event_id": len(self.entity_extraction_log) + 1,
            "entities_count": len(entities),
            "relationships_count": len(relationships),
            "speaker": speaker,
            "timestamp": time.time()
        })
        self.graph_metrics_cache = {}

    def get_graph_topology(self) -> Dict[str, Any]:
        """Return graph structure metrics (nodes, edges, density, avg degree, connected components)."""
        if self.graph_metrics_cache:
            return self.graph_metrics_cache
        num_nodes = self.knowledge_graph.number_of_nodes()
        num_edges = self.knowledge_graph.number_of_edges()
        density = nx.density(self.knowledge_graph) if num_nodes > 1 else 0.0
        degrees = [d for _, d in self.knowledge_graph.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0.0
        try:
            comps = nx.number_weakly_connected_components(self.knowledge_graph)
        except Exception:
            comps = 1
        self.graph_metrics_cache = {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": round(density, 4),
            "avg_degree": round(avg_degree, 4),
            "connected_components": comps
        }
        return self.graph_metrics_cache

    def visualize_graph(self) -> Dict[str, Any]:
        """Return graph data for UI visualization (nodes and edges lists)."""
        topo = self.get_graph_topology()
        nodes = [{"id": n, **dict(self.knowledge_graph.nodes[n])} for n in self.knowledge_graph.nodes()]
        edges = [
            {"source": u, "target": v, "relationship": self.knowledge_graph.edges[u, v].get("relationship", "")}
            for u, v in self.knowledge_graph.edges()
        ]
        return {"topology": topo, "nodes": nodes, "edges": edges}

    def add_message(self, user_input: str, ai_response: str) -> None:
        """
        Add conversation turn to graph by extracting entities and relationships.

        Args:
            user_input: User's message
            ai_response: AI's response
        """
        self.conversation_history.append({
            "user": user_input,
            "assistant": ai_response,
            "turn_id": self.node_counter
        })
        self._extract_and_add_entities(user_input, "user", self.node_counter)
        self._extract_and_add_entities(ai_response, "assistant", self.node_counter)
        self.node_counter += 1
        self._log_operation("ADD_TURN", {"turn_id": self.node_counter - 1})

    def _extract_and_add_entities(self, text: str, speaker: str, turn_id: int) -> None:
        """Extract entities and relationships from text and add to knowledge graph."""
        print(f"[GRAPH EXTRACTION] Processing text: {text[:100]}...")
        extraction_prompt = (
            f"Extract key entities (people, places, concepts, facts) and relationships from this text. "
            f"Format as: ENTITIES: entity1, entity2, entity3... RELATIONSHIPS: entity1->relationship->entity2, etc.\n\n"
            f"Text: {text}\n\n"
            f"If no clear entities or relationships, respond with 'ENTITIES: none RELATIONSHIPS: none'"
        )
        extracted_info = generate_text(
            "You are an entity and relationship extraction expert.",
            extraction_prompt,
            self.client
        )
        print(f"[GRAPH EXTRACTION] LLM extracted: {extracted_info}")
        entities_added, relationships_added = self._parse_and_add_to_graph(extracted_info, speaker, turn_id, text)
        print(f"[GRAPH EXTRACTION] Added {len(entities_added)} entities: {entities_added}")
        print(f"[GRAPH EXTRACTION] Added {len(relationships_added)} relationships: {relationships_added}")
        self._track_entity_extraction(entities_added, relationships_added, speaker)

    def _parse_and_add_to_graph(self, extracted_info: str, speaker: str, turn_id: int, original_text: str) -> tuple:
        """Parse extracted entities and relationships and add them to the knowledge graph. Returns (entities_list, relationships_list)."""
        entities_added: List[str] = []
        relationships_added: List[str] = []
        try:
            if "ENTITIES:" in extracted_info and "RELATIONSHIPS:" in extracted_info:
                parts = extracted_info.split("RELATIONSHIPS:")
                entities_part = parts[0].replace("ENTITIES:", "").strip()
                relationships_part = parts[1].strip() if len(parts) > 1 else ""

                if entities_part.lower() != "none":
                    entities = [e.strip() for e in entities_part.split(",") if e.strip()]
                    for entity in entities:
                        if entity:
                            self.knowledge_graph.add_node(
                                entity,
                                type="entity",
                                speaker=speaker,
                                turn_id=turn_id,
                                context=original_text[:100]
                            )
                            entities_added.append(entity)

                if relationships_part.lower() != "none":
                    relationships = [r.strip() for r in relationships_part.split(",") if r.strip()]
                    for rel in relationships:
                        if "->" in rel:
                            rel_parts = rel.split("->")
                            if len(rel_parts) == 3:
                                source, relation, target = [p.strip() for p in rel_parts]
                                if source and target and relation:
                                    self.knowledge_graph.add_edge(
                                        source, target,
                                        relationship=relation,
                                        turn_id=turn_id,
                                        speaker=speaker
                                    )
                                    relationships_added.append(rel)
        except Exception as e:
            print(f"[GRAPH] Error parsing extracted info: {e}")
        return (entities_added, relationships_added)

    def get_context(self, query: str) -> str:
        """
        Retrieve relevant context by traversing the knowledge graph.

        Args:
            query: Current user query

        Returns:
            Relevant context from knowledge graph and conversation history
        """
        print(f"[GRAPH GET_CONTEXT] Query: {query}")
        print(f"[GRAPH GET_CONTEXT] Current graph has {self.knowledge_graph.number_of_nodes()} nodes, {self.knowledge_graph.number_of_edges()} edges")
        
        if self.knowledge_graph.number_of_nodes() == 0:
            return "No information in memory yet."
            
        query_extraction_prompt = (
            f"Extract ONLY the key named entities (specific people, places, organizations) from this query. "
            f"Focus on proper nouns and specific subjects that would be nodes in a knowledge graph. "
            f"Do NOT extract general words like 'everyone', 'team', 'reports', 'list'. "
            f"Examples:\n"
            f"- From 'Who does Bob report to?' extract: Bob\n"
            f"- From 'List everyone who reports to Alice' extract: Alice\n"
            f"- From 'What is the project status?' extract: project\n"
            f"List entities separated by commas. If no clear named entities, respond with 'none'.\n\n"
            f"Query: {query}"
        )
        query_entities = generate_text(
            "You are an entity extraction expert.",
            query_extraction_prompt,
            self.client
        )
        print(f"[GRAPH GET_CONTEXT] Extracted query entities: {query_entities}")
        
        relevant_info = []
        if query_entities.lower() != "none":
            entities = [e.strip() for e in query_entities.split(",") if e.strip()]
            print(f"[GRAPH GET_CONTEXT] Looking for entities: {entities}")
            print(f"[GRAPH GET_CONTEXT] Available nodes in graph: {list(self.knowledge_graph.nodes())[:20]}")  # Show first 20
            
            for entity in entities:
                for node in self.knowledge_graph.nodes():
                    if entity.lower() in node.lower() or node.lower() in entity.lower():
                        print(f"[GRAPH GET_CONTEXT] Found matching node: {node}")
                        node_data = self.knowledge_graph.nodes[node]
                        relevant_info.append(f"Entity: {node} (from {node_data.get('speaker', 'unknown')})")
                        
                        # Outgoing edges (node -> neighbor)
                        for neighbor in self.knowledge_graph.neighbors(node):
                            edge_data = self.knowledge_graph.edges[node, neighbor]
                            relationship = edge_data.get('relationship', 'related to')
                            relevant_info.append(f"  -> {relationship} -> {neighbor}")
                        
                        # Incoming edges (predecessor -> node)
                        for predecessor in self.knowledge_graph.predecessors(node):
                            edge_data = self.knowledge_graph.edges[predecessor, node]
                            relationship = edge_data.get('relationship', 'related to')
                            relevant_info.append(f"  <- {predecessor} <- {relationship}")
                            
        if not relevant_info:
            print(f"[GRAPH GET_CONTEXT] No relevant entities found, using recent turns")
            recent_turns = self.conversation_history[-3:]
            for turn in recent_turns:
                relevant_info.append(f"Turn {turn['turn_id']}: User: {turn['user']}")
                relevant_info.append(f"Turn {turn['turn_id']}: Assistant: {turn['assistant']}")
                
        context = "### Knowledge Graph Context:\n" + "\n".join(relevant_info) if relevant_info else "No relevant information found."
        print(f"[GRAPH GET_CONTEXT] Returning context with {len(relevant_info)} items")
        return context

    def clear(self) -> None:
        """Reset the knowledge graph and conversation history."""
        self.knowledge_graph.clear()
        self.conversation_history = []
        self.node_counter = 0
        self.entity_extraction_log = []
        self.graph_metrics_cache = {}
        self.operation_log = []
        print("[GRAPH] Graph memory cleared.")

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Return strategy-specific operation log."""
        return list(self.operation_log)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.

        Returns:
            Dictionary containing memory statistics
        """
        topo = self.get_graph_topology()
        num_turns = len(self.conversation_history)
        return {
            "strategy_id": self.STRATEGY_ID,
            "strategy_type": "GraphMemory",
            "graph_metrics": {
                "nodes": topo["nodes"],
                "edges": topo["edges"],
                "density": topo["density"],
                "avg_degree": topo["avg_degree"],
                "connected_components": topo["connected_components"]
            },
            "num_turns": num_turns,
            "memory_size": f"{topo['nodes']} nodes, {topo['edges']} edges, {num_turns} turns",
            "advantages": ["Relationship modeling", "Complex reasoning", "Structured knowledge"],
            "disadvantages": ["Complex implementation", "Extraction dependent", "Computational overhead"]
        }
