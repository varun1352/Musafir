import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import NodePopup from './NodePopUp'; // adjust the path if needed

// Sample data with arbitrary 3D positions (you can update these as needed)
const sampleData = {
  nodes: [
    {
      id: 1,
      name: "Central Park",
      position: [0, 1, 0],
      users: [
        { name: "Alice", timeSlots: ["10:00 AM - 11:00 AM", "2:00 PM - 3:00 PM"] },
        { name: "Bob", timeSlots: ["11:00 AM - 12:00 PM"] },
      ],
    },
    {
      id: 2,
      name: "Times Square",
      position: [3, 1, -1],
      users: [
        { name: "Charlie", timeSlots: ["1:00 PM - 2:00 PM", "4:00 PM - 5:00 PM"] },
        { name: "David", timeSlots: ["9:00 AM - 10:00 AM"] },
      ],
    },
    {
      id: 3,
      name: "Brooklyn Bridge",
      position: [-3, 1, 1],
      users: [
        { name: "Eve", timeSlots: ["8:00 AM - 9:00 AM", "5:00 PM - 6:00 PM"] },
        { name: "Frank", timeSlots: ["12:00 PM - 1:00 PM"] },
      ],
    },
  ],
  edges: [
    { id: 1, source: 1, target: 2 },
    { id: 2, source: 1, target: 3 },
    { id: 3, source: 2, target: 3 },
  ],
};

// A simple ground plane that doesn't intercept pointer events
function GroundPlane() {
  const handlePointerDown = (e) => {
    e.stopPropagation();
  };

  return (
    <mesh
      rotation-x={-Math.PI / 2}
      position={[0, 0, 0]}
      onPointerDown={handlePointerDown}
    >
      <planeGeometry args={[20, 20]} />
      <meshStandardMaterial color="#222" transparent opacity={0.8} />
    </mesh>
  );
}

// Component for rendering a single node (as a sphere)
function GraphNode({ node, onClick }) {
  const handlePointerDown = (e) => {
    e.stopPropagation();
    console.log("Node clicked:", node);
    onClick(node);
  };

  return (
    <mesh position={node.position} onPointerDown={handlePointerDown}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="orange" />
      <Html position={[0, 1.2, 0]} pointerEvents="none">
        <div
          style={{
            color: "white",
            background: "rgba(0,0,0,0.5)",
            padding: "4px 8px",
            borderRadius: "4px",
            fontSize: "14px",
          }}
        >
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

  const handleNodeClick = (node) => {
    setActiveNode(node);
  };

  const closePopup = () => {
    setActiveNode(null);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* 3D Graph canvas */}
      <div style={{ flex: 1 }}>
        <Canvas camera={{ position: [0, 10, 20], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <GroundPlane />
          {sampleData.nodes.map((node) => (
            <GraphNode key={node.id} node={node} onClick={handleNodeClick} />
          ))}
          <GraphEdges nodes={sampleData.nodes} edges={sampleData.edges} />
          {/* Enable OrbitControls if you need zoom/pan/rotate */}
          {/* <OrbitControls /> */}
        </Canvas>
      </div>
      {/* Modal popup for node details */}
      {activeNode && <NodePopup node={activeNode} onClose={closePopup} />}
    </div>
  );
}
