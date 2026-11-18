from collections import deque
from loguru import logger
from contagion_graph.graph_builder import build_contagion_graph

ATTENUATION_FACTOR = 0.65
MIN_SURPRISE_THRESHOLD = 0.05

def propagate_shock(
    source_ticker: str,
    primary_direction: str,
    primary_magnitude: float,
    max_hops: int = 2
) -> list[dict]:
    """
    [Novelty 3] Breadth-First Search (BFS) shock propagation across the contagion graph.
    Propagates primary surprise to adjacent nodes with geometric attenuation:
      secondary_mag = primary_mag * edge_weight * (ATTENUATION_FACTOR ^ hop)
      
    Filters out transmissions below MIN_SURPRISE_THRESHOLD (0.05).
    """
    G = build_contagion_graph()
    src = source_ticker.upper()
    
    if src not in G:
        logger.info(f"Source ticker {src} has no outbound contagion edges.")
        return []
        
    secondary_signals = []
    visited = {src: 0}
    queue = deque([(src, primary_magnitude, 0)])
    
    while queue:
        current_node, current_mag, hop = queue.popleft()
        
        if hop >= max_hops:
            continue
            
        for neighbor in G.successors(current_node):
            edge_data = G[current_node][neighbor]
            weight = edge_data.get("weight", 0.5)
            delay = edge_data.get("delay_hours", 2.0)
            rel = edge_data.get("relationship", "correlated")
            
            # Attenuation formula
            attenuated_mag = round(float(current_mag * weight * (ATTENUATION_FACTOR ** (hop + 1))), 4)
            
            if attenuated_mag < MIN_SURPRISE_THRESHOLD:
                continue
                
            if neighbor not in visited or visited[neighbor] > hop + 1:
                visited[neighbor] = hop + 1
                queue.append((neighbor, attenuated_mag, hop + 1))
                
                secondary_signals.append({
                    "primary_source": src,
                    "target_ticker": neighbor,
                    "propagated_direction": primary_direction,
                    "propagated_magnitude": attenuated_mag,
                    "hop_distance": hop + 1,
                    "expected_delay_hours": delay * (hop + 1),
                    "supply_chain_link": rel
                })
                
    logger.info(f"Propagated {len(secondary_signals)} secondary signals from {src} (Mag: {primary_magnitude:.2f})")
    return secondary_signals

if __name__ == "__main__":
    signals = propagate_shock("TSM", "BULLISH", 0.65)
    for s in signals:
        print(s)
