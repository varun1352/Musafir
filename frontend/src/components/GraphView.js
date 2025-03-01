import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';

// Sample data for demonstration
const sampleData = {
  nodes: [
    { id: 1, name: "Central Park", position: [0, 0, 0], users: ["Alice", "Bob"] },
    { id: 2, name: "Times Square", position: [5, 0, 0], users: ["Charlie", "David"] },
    { id: 3, name: "Brooklyn Bridge", position: [-5, 0, 0], users: ["Eve", "Frank"] },
    // Add additional nodes as needed...
  ],
  edges: [
    { id: 1, source: 1, target: 2 },
    { id: 2, source: 1, target: 3 },
    { id: 3, source: 2, target: 3 },
  ],
};

// Component for rendering a single node (as a sphere)
function GraphNode({ node, onClick }) {
  return (
    <mesh position={node.position} onClick={() => onClick(node)}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color={'orange'} />
      {/* Use Html to attach a label to the node */}
      <Html position={[0, 0.8, 0]}>
        <div style={{ color: 'white', background: 'rgba(0,0,0,0.5)', padding: '2px 5px', borderRadius: '4px', fontSize: '12px' }}>
          {node.name}
        </div>
      </Html>
    </mesh>
  );
}

// Component for rendering edges between nodes
function GraphEdges({ nodes, edges }) {
  return (
    <group>
      {edges.map((edge) => {
        const source = nodes.find((n) => n.id === edge.source);
        const target = nodes.find((n) => n.id === edge.target);
        if (!source || !target) return null;

        // Create a line between the two nodes
        const start = new THREE.Vector3(...source.position);
        const end = new THREE.Vector3(...target.position);
        const points = [start, end];
        const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);

        return (
          <line key={edge.id} geometry={lineGeometry}>
            <lineBasicMaterial attach="material" color="white" />
          </line>
        );
      })}
    </group>
  );
}

export default function GraphView() {
  const [activeNode, setActiveNode] = useState(null);

  // Handler for when a node is clicked
  const handleNodeClick = (node) => {
    setActiveNode(node);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* 3D Graph canvas */}
      <div style={{ flex: 1 }}>
        <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          {sampleData.nodes.map((node) => (
            <GraphNode key={node.id} node={node} onClick={handleNodeClick} />
          ))}
          <GraphEdges nodes={sampleData.nodes} edges={sampleData.edges} />
          <OrbitControls />
        </Canvas>
      </div>

      {/* Sidebar to display users at the clicked node */}
      {activeNode && (
        <div style={{ width: '300px', background: '#f5f5f5', padding: '10px', overflowY: 'auto' }}>
          <h3>{activeNode.name}</h3>
          <p>Users at this location:</p>
          <ul>
            {activeNode.users.map((user, index) => (
              <li key={index}>{user}</li>
            ))}
          </ul>
          <button onClick={() => setActiveNode(null)}>Close</button>
        </div>
      )}
    </div>
  );
}

