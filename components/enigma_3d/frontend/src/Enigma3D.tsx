import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Html, DragControls } from '@react-three/drei';
import * as THREE from 'three';
import { Component } from '@streamlit/component-v2-lib';
import { createRoot } from 'react-dom/client';


const EnigmaScene: React.FC<{ data: any; setValue: (value: any) => void }> = ({ data, setValue }) => {
  const { hookedTools = [] } = data;
  const enigmaRef = useRef<THREE.Group>(null!);
  const toolRefs = useRef<THREE.Mesh[]>([]);
  const dragRef = useRef<any>(null);
  const { camera } = useThree();

  const { scene: enigmaScene } = useGLTF('/models/enigma.glb');

  const tools = ['ScienceClaw', 'GPD', 'AI-Researcher', 'HyperAgent', 'Chutes'];

  useFrame(() => {
    if (enigmaRef.current) enigmaRef.current.rotation.y += 0.0015; // subtle idle rotation
  });

  const handleInspect = (tool: string) => setValue({ type: 'inspect_tool', tool });
  const handleHook = (tool: string) => setValue({ type: 'hook_tool', tool });

  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 15, 10]} intensity={1.2} color="#ffcc88" />
      <Environment preset="night" />
      <fog attach="fog" args={['#0f0a05', 8, 45]} />

      {/* Wooden table */}
      <mesh position={[0, -2, 0]} rotation={[-Math.PI * 0.5, 0, 0]}>
        <planeGeometry args={[15, 15]} />
        <meshStandardMaterial color="#3c2f1f" roughness={0.95} />
      </mesh>

      {/* 3D Enigma Machine */}
      <group ref={enigmaRef} position={[0, 0.2, 0]} scale={1.6}>
        <primitive object={enigmaScene} />
        {/* Invisible click zone for zoom */}
        <mesh onClick={() => setValue({ type: 'zoom_machine' })} position={[0, 1, 0]}>
          <boxGeometry args={[3, 1, 4]} />
          <meshStandardMaterial visible={false} />
        </mesh>
      </group>

      {/* 3D Tool Inventory (spheres with labels) */}
      {tools.map((tool, i) => (
        <mesh
          key={tool}
          ref={(el) => { if (el) toolRefs.current[i] = el; }}
          position={[5 + Math.cos(i) * 4, 2 + Math.sin(i) * 1.5, -4 + (i % 3) * 2]}
          onClick={() => handleInspect(tool)}
        >
          <sphereGeometry args={[0.65]} />
          <meshStandardMaterial 
            color={hookedTools.includes(tool) ? '#00ff44' : '#ffaa00'} 
            emissive={hookedTools.includes(tool) ? '#00ff44' : '#ffaa00'} 
            emissiveIntensity={0.6}
          />
          <Html position={[0, 1.4, 0]} style={{ color: '#ffcc00', fontFamily: 'Courier New, monospace', fontSize: '15px', textShadow: '0 0 6px #000' }} distanceFactor={10}>
            {tool}
          </Html>
        </mesh>
      ))}

      {/* Drag Controls — drag tool onto machine area to hook */}
      <DragControls ref={dragRef} objects={toolRefs.current} onDragEnd={(e) => {
        const idx = toolRefs.current.indexOf(e.object as THREE.Mesh);
        if (idx !== -1) {
          const dragged = tools[idx];
          // Proximity check (simple distance to center)
          handleHook(dragged);
        }
      }} />

      <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} minDistance={6} maxDistance={35} target={[0, 0, 0]} />
    </>
  );
};

const Enigma3D: Component = (args) => {
  const containerRef = useRef<HTMLDivElement>(null!);
  const rootRef = useRef<any>(null);

  useEffect(() => {
    if (!rootRef.current && containerRef.current) {
      rootRef.current = createRoot(containerRef.current);
    }
    if (rootRef.current) {
      rootRef.current.render(
        <Canvas style={{ background: '#0a0503' }} camera={{ position: [0, 8, 18], fov: 45 }}>
          <EnigmaScene data={args.data || {}} setValue={args.setValue} />
        </Canvas>
      );
    }
  }, [args.data]);

  return <div ref={containerRef} style={{ width: '100%', height: '620px' }} />;
};

export default Enigma3D;
