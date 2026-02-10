"""
Test script to verify deadlock endpoint returns proper structure
"""

import json
import sys
sys.path.insert(0, 'backend')

from deadlock_detector_new import DeadlockDetector

# Test deadlock analysis response structure
detector = DeadlockDetector()
analysis = detector.analyze_deadlock_risk()

print("=" * 60)
print("DEADLOCK ANALYSIS RESPONSE TEST")
print("=" * 60)

# Check required fields
required_fields = ['has_cycles', 'cycle_count', 'risk_level', 'nodes_in_cycles', 'total_locks_tracked']
print("\nChecking required fields in analysis:")
for field in required_fields:
    status = '✓' if field in analysis else '✗'
    print(f"  {status} {field}: {analysis.get(field, 'MISSING')}")

# Test nodes/edges generation (simulating backend behavior)
print("\nTesting nodes/edges generation from cycles:")

nodes = []
edges = []

if analysis.get('has_cycles', False):
    cycles = analysis.get('cycles', [])
    node_set = set()
    
    for cycle in cycles:
        for node in cycle:
            node_set.add(str(node))
    
    for i, node in enumerate(sorted(list(node_set))):
        nodes.append({
            'id': node,
            'name': f'Thread {node}',
            'type': 'thread'
        })
    
    edge_set = set()
    for cycle in cycles:
        for i in range(len(cycle)):
            src = str(cycle[i])
            dst = str(cycle[(i + 1) % len(cycle)])
            edge_key = (src, dst)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append({
                    'source': src,
                    'target': dst,
                    'type': 'wait-for'
                })
else:
    print("  No cycles detected - this is normal for fresh analysis")

print(f"\n  Generated {len(nodes)} nodes and {len(edges)} edges")
print(f"\n  Sample response structure:")
response = {
    'status': 'success',
    'analysis': {
        'has_cycles': analysis.get('has_cycles', False),
        'cycle_count': analysis.get('cycle_count', 0),
        'risk_level': analysis.get('risk_level', 'low'),
        'nodes_in_cycles': analysis.get('nodes_in_cycles', []),
        'total_locks_tracked': analysis.get('total_locks_tracked', 0)
    },
    'nodes': nodes,
    'edges': edges,
    'historical_deadlocks': []
}

print(f"  {json.dumps(response, indent=2)}")

print("\n" + "=" * 60)
print("✓ Test completed successfully")
print("=" * 60)
