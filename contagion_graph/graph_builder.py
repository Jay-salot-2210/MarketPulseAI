import networkx as nx
from loguru import logger

def build_contagion_graph() -> nx.DiGraph:
    """
    [Novelty 3] Cross-Asset Contagion Graph
    Constructs a directed weighted network of tech supply chains, bellwethers, and competitors.
    Includes global semiconductor nodes (TSMC, ASML) feeding US mega-cap tech.
    
    Edges have:
      - 'weight': transmission strength [0.0 to 1.0]
      - 'delay_hours': typical shock propagation lead-lag
      - 'relationship': e.g., 'foundry_supplier', 'lithography_equipment', 'gpu_competitor'
    """
    G = nx.DiGraph()
    
    # Supply-chain and sector contagion edges
    edges = [
        # Upstream semiconductor equipment & foundries -> Chip designers
        ("ASML", "TSM", {"weight": 0.82, "delay_hours": 3.0, "relationship": "lithography_supplier"}),
        ("TSM", "NVDA", {"weight": 0.78, "delay_hours": 2.5, "relationship": "exclusive_foundry"}),
        ("TSM", "AAPL", {"weight": 0.72, "delay_hours": 4.0, "relationship": "primary_foundry"}),
        ("TSM", "AMD",  {"weight": 0.69, "delay_hours": 3.5, "relationship": "foundry_supplier"}),
        
        # Chip designers -> Hyperscalers & Consumers
        ("NVDA", "MSFT", {"weight": 0.65, "delay_hours": 4.0, "relationship": "ai_infrastructure"}),
        ("NVDA", "AMD",  {"weight": 0.74, "delay_hours": 1.0, "relationship": "direct_competitor"}),
        ("AMD", "NVDA",  {"weight": 0.68, "delay_hours": 1.0, "relationship": "direct_competitor"}),
        ("MSFT", "AAPL", {"weight": 0.45, "delay_hours": 5.0, "relationship": "mega_cap_liquidity"}),
        ("AAPL", "TSLA", {"weight": 0.35, "delay_hours": 6.0, "relationship": "risk_sentiment"}),
    ]
    
    for u, v, data in edges:
        G.add_edge(u, v, **data)
        
    logger.info(f"Contagion graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

if __name__ == "__main__":
    G = build_contagion_graph()
    print("Nodes:", list(G.nodes))
    print("Edges:", list(G.edges(data=True)))
