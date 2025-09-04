/**
 * Componente de Visualização 3D da Cidade Inteligente
 * Versão 1.2 - Dashboard 3D com Three.js
 */

import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';
import { Card, Row, Col, Statistic, Switch, Slider, Button, Space } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  ReloadOutlined,
  EyeOutlined,
  SettingOutlined 
} from '@ant-design/icons';

interface Agent3D {
  id: string;
  type: 'citizen' | 'business' | 'government' | 'infrastructure';
  position: { x: number; y: number; z: number };
  status: 'active' | 'inactive' | 'crisis';
  data: any;
}

interface City3DProps {
  agents: Agent3D[];
  events: any[];
  metrics: any;
  onAgentClick?: (agent: Agent3D) => void;
  onEventClick?: (event: any) => void;
}

const City3DVisualization: React.FC<City3DProps> = ({
  agents,
  events,
  metrics,
  onAgentClick,
  onEventClick
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const controlsRef = useRef<OrbitControls>();
  const animationIdRef = useRef<number>();
  
  const [isPlaying, setIsPlaying] = useState(true);
  const [viewMode, setViewMode] = useState<'overview' | 'street' | 'building'>('overview');
  const [showGrid, setShowGrid] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [bloomIntensity, setBloomIntensity] = useState(1.0);
  const [cameraSpeed, setCameraSpeed] = useState(1.0);

  // Cores para diferentes tipos de agentes
  const agentColors = {
    citizen: 0x4CAF50,      // Verde
    business: 0x2196F3,     // Azul
    government: 0x9C27B0,   // Roxo
    infrastructure: 0xFF9800 // Laranja
  };

  // Status colors
  const statusColors = {
    active: 0x4CAF50,
    inactive: 0x757575,
    crisis: 0xF44336
  };

  useEffect(() => {
    if (!mountRef.current) return;

    // Inicializar Three.js
    initThreeJS();
    
    // Carregar modelos 3D
    loadCityModels();
    
    // Iniciar animação
    if (isPlaying) {
      animate();
    }

    return () => {
      cleanup();
    };
  }, []);

  useEffect(() => {
    updateAgents();
  }, [agents]);

  useEffect(() => {
    updateEvents();
  }, [events]);

  const initThreeJS = () => {
    if (!mountRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    scene.fog = new THREE.Fog(0x0a0a0a, 50, 200);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(50, 50, 50);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true 
    });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    rendererRef.current = renderer;

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2;
    controls.minDistance = 10;
    controls.maxDistance = 200;
    controlsRef.current = controls;

    // Post-processing
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(mountRef.current.clientWidth, mountRef.current.clientHeight),
      1.5, // strength
      0.4, // radius
      0.85 // threshold
    );
    composer.addPass(bloomPass);

    // Lighting
    setupLighting(scene);

    // Grid
    if (showGrid) {
      setupGrid(scene);
    }

    // City base
    setupCityBase(scene);

    mountRef.current.appendChild(renderer.domElement);
  };

  const setupLighting = (scene: THREE.Scene) => {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);

    // Directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(50, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 500;
    directionalLight.shadow.camera.left = -100;
    directionalLight.shadow.camera.right = 100;
    directionalLight.shadow.camera.top = 100;
    directionalLight.shadow.camera.bottom = -100;
    scene.add(directionalLight);

    // Point lights for city ambiance
    const pointLight1 = new THREE.PointLight(0x4CAF50, 0.5, 100);
    pointLight1.position.set(20, 10, 20);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x2196F3, 0.5, 100);
    pointLight2.position.set(-20, 10, -20);
    scene.add(pointLight2);
  };

  const setupGrid = (scene: THREE.Scene) => {
    const gridHelper = new THREE.GridHelper(200, 50, 0x444444, 0x444444);
    gridHelper.position.y = 0;
    scene.add(gridHelper);
  };

  const setupCityBase = (scene: THREE.Scene) => {
    // City ground
    const groundGeometry = new THREE.PlaneGeometry(200, 200);
    const groundMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x2a2a2a,
      transparent: true,
      opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // City boundaries
    const boundaryGeometry = new THREE.BoxGeometry(200, 2, 200);
    const boundaryMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x1a1a1a,
      transparent: true,
      opacity: 0.3
    });
    const boundary = new THREE.Mesh(boundaryGeometry, boundaryMaterial);
    boundary.position.y = -1;
    scene.add(boundary);
  };

  const loadCityModels = async () => {
    if (!sceneRef.current) return;

    const loader = new GLTFLoader();
    
    try {
      // Carregar modelos de prédios (se disponíveis)
      // loader.load('/models/buildings.gltf', (gltf) => {
      //   sceneRef.current?.add(gltf.scene);
      // });

      // Por enquanto, criar prédios procedurais
      createProceduralBuildings();
    } catch (error) {
      console.warn('Erro ao carregar modelos 3D:', error);
      createProceduralBuildings();
    }
  };

  const createProceduralBuildings = () => {
    if (!sceneRef.current) return;

    // Criar prédios procedurais
    for (let i = 0; i < 20; i++) {
      const building = createBuilding();
      building.position.set(
        (Math.random() - 0.5) * 180,
        0,
        (Math.random() - 0.5) * 180
      );
      sceneRef.current.add(building);
    }
  };

  const createBuilding = () => {
    const group = new THREE.Group();
    
    // Base do prédio
    const baseGeometry = new THREE.BoxGeometry(
      2 + Math.random() * 4,
      5 + Math.random() * 15,
      2 + Math.random() * 4
    );
    const baseMaterial = new THREE.MeshLambertMaterial({ 
      color: new THREE.Color().setHSL(0.1, 0.2, 0.3 + Math.random() * 0.3)
    });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = baseGeometry.parameters.height / 2;
    base.castShadow = true;
    base.receiveShadow = true;
    group.add(base);

    // Janelas
    const windowGeometry = new THREE.PlaneGeometry(0.3, 0.5);
    const windowMaterial = new THREE.MeshBasicMaterial({ 
      color: 0x87CEEB,
      transparent: true,
      opacity: 0.8
    });

    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const window = new THREE.Mesh(windowGeometry, windowMaterial);
        window.position.set(
          -baseGeometry.parameters.width / 2 + 0.5 + i * 0.8,
          baseGeometry.parameters.height / 2 - 1 - j * 1.5,
          baseGeometry.parameters.depth / 2 + 0.01
        );
        group.add(window);
      }
    }

    return group;
  };

  const updateAgents = () => {
    if (!sceneRef.current) return;

    // Remover agentes antigos
    const oldAgents = sceneRef.current.getObjectByName('agents');
    if (oldAgents) {
      sceneRef.current.remove(oldAgents);
    }

    // Criar grupo de agentes
    const agentsGroup = new THREE.Group();
    agentsGroup.name = 'agents';

    agents.forEach(agent => {
      const agentMesh = createAgentMesh(agent);
      agentsGroup.add(agentMesh);
    });

    sceneRef.current.add(agentsGroup);
  };

  const createAgentMesh = (agent: Agent3D) => {
    const group = new THREE.Group();
    
    // Cor baseada no tipo
    const baseColor = agentColors[agent.type];
    const statusColor = statusColors[agent.status];
    
    // Geometria baseada no tipo
    let geometry: THREE.BufferGeometry;
    switch (agent.type) {
      case 'citizen':
        geometry = new THREE.SphereGeometry(0.5, 8, 6);
        break;
      case 'business':
        geometry = new THREE.BoxGeometry(1, 1, 1);
        break;
      case 'government':
        geometry = new THREE.ConeGeometry(0.5, 1.5, 6);
        break;
      case 'infrastructure':
        geometry = new THREE.CylinderGeometry(0.3, 0.3, 2, 8);
        break;
      default:
        geometry = new THREE.SphereGeometry(0.5, 8, 6);
    }

    const material = new THREE.MeshLambertMaterial({ 
      color: agent.status === 'crisis' ? statusColor : baseColor,
      emissive: agent.status === 'crisis' ? 0x220000 : 0x000000
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(agent.position.x, agent.position.y, agent.position.z);
    mesh.castShadow = true;
    mesh.userData = { agent };
    
    // Adicionar label se habilitado
    if (showLabels) {
      const label = createAgentLabel(agent);
      label.position.set(0, 2, 0);
      group.add(label);
    }

    // Adicionar animação de pulsação para agentes em crise
    if (agent.status === 'crisis') {
      mesh.userData.animate = true;
    }

    group.add(mesh);
    return group;
  };

  const createAgentLabel = (agent: Agent3D) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return new THREE.Group();

    canvas.width = 128;
    canvas.height = 64;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.fillStyle = 'white';
    context.font = '12px Arial';
    context.textAlign = 'center';
    context.fillText(agent.type.toUpperCase(), canvas.width / 2, 20);
    context.fillText(agent.id.slice(0, 8), canvas.width / 2, 40);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(4, 2, 1);

    return sprite;
  };

  const updateEvents = () => {
    if (!sceneRef.current) return;

    // Remover eventos antigos
    const oldEvents = sceneRef.current.getObjectByName('events');
    if (oldEvents) {
      sceneRef.current.remove(oldEvents);
    }

    // Criar grupo de eventos
    const eventsGroup = new THREE.Group();
    eventsGroup.name = 'events';

    events.forEach(event => {
      const eventMesh = createEventMesh(event);
      eventsGroup.add(eventMesh);
    });

    sceneRef.current.add(eventsGroup);
  };

  const createEventMesh = (event: any) => {
    const geometry = new THREE.SphereGeometry(2, 16, 16);
    const material = new THREE.MeshBasicMaterial({ 
      color: 0xff0000,
      transparent: true,
      opacity: 0.6,
      wireframe: true
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(event.x || 0, 5, event.z || 0);
    mesh.userData = { event };

    // Animação de pulsação
    mesh.userData.animate = true;
    mesh.userData.animationSpeed = 0.02;

    return mesh;
  };

  const animate = () => {
    if (!isPlaying) return;

    animationIdRef.current = requestAnimationFrame(animate);

    if (controlsRef.current) {
      controlsRef.current.update();
    }

    // Animar agentes
    if (sceneRef.current) {
      const agentsGroup = sceneRef.current.getObjectByName('agents');
      if (agentsGroup) {
        agentsGroup.children.forEach(child => {
          if (child.userData.animate) {
            child.rotation.y += 0.01;
            child.scale.setScalar(1 + Math.sin(Date.now() * 0.005) * 0.1);
          }
        });
      }

      // Animar eventos
      const eventsGroup = sceneRef.current.getObjectByName('events');
      if (eventsGroup) {
        eventsGroup.children.forEach(child => {
          if (child.userData.animate) {
            child.rotation.y += child.userData.animationSpeed || 0.01;
            child.scale.setScalar(1 + Math.sin(Date.now() * 0.01) * 0.2);
          }
        });
      }
    }

    if (rendererRef.current && sceneRef.current && cameraRef.current) {
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    }
  };

  const cleanup = () => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
    }
    if (rendererRef.current && mountRef.current) {
      mountRef.current.removeChild(rendererRef.current.domElement);
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      animate();
    }
  };

  const handleViewModeChange = (mode: 'overview' | 'street' | 'building') => {
    setViewMode(mode);
    if (cameraRef.current) {
      switch (mode) {
        case 'overview':
          cameraRef.current.position.set(50, 50, 50);
          break;
        case 'street':
          cameraRef.current.position.set(10, 5, 10);
          break;
        case 'building':
          cameraRef.current.position.set(5, 20, 5);
          break;
      }
    }
  };

  return (
    <div style={{ height: '100%', position: 'relative' }}>
      {/* Canvas 3D */}
      <div 
        ref={mountRef} 
        style={{ 
          width: '100%', 
          height: '100%',
          background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)'
        }} 
      />

      {/* Controles */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        zIndex: 1000
      }}>
        <Card size="small" style={{ background: 'rgba(0,0,0,0.8)', color: 'white' }}>
          <Space direction="vertical">
            <Button 
              type="primary" 
              icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={handlePlayPause}
            >
              {isPlaying ? 'Pausar' : 'Play'}
            </Button>
            
            <div>
              <div style={{ color: 'white', marginBottom: 8 }}>Modo de Visualização:</div>
              <Space>
                <Button 
                  size="small"
                  type={viewMode === 'overview' ? 'primary' : 'default'}
                  onClick={() => handleViewModeChange('overview')}
                >
                  Visão Geral
                </Button>
                <Button 
                  size="small"
                  type={viewMode === 'street' ? 'primary' : 'default'}
                  onClick={() => handleViewModeChange('street')}
                >
                  Rua
                </Button>
                <Button 
                  size="small"
                  type={viewMode === 'building' ? 'primary' : 'default'}
                  onClick={() => handleViewModeChange('building')}
                >
                  Prédio
                </Button>
              </Space>
            </div>

            <div>
              <div style={{ color: 'white', marginBottom: 8 }}>Configurações:</div>
              <Space direction="vertical" size="small">
                <div>
                  <span style={{ color: 'white', fontSize: 12 }}>Grid: </span>
                  <Switch 
                    size="small" 
                    checked={showGrid} 
                    onChange={setShowGrid}
                  />
                </div>
                <div>
                  <span style={{ color: 'white', fontSize: 12 }}>Labels: </span>
                  <Switch 
                    size="small" 
                    checked={showLabels} 
                    onChange={setShowLabels}
                  />
                </div>
              </Space>
            </div>
          </Space>
        </Card>
      </div>

      {/* Estatísticas */}
      <div style={{
        position: 'absolute',
        top: 20,
        right: 20,
        zIndex: 1000
      }}>
        <Card size="small" style={{ background: 'rgba(0,0,0,0.8)', color: 'white' }}>
          <Row gutter={[16, 8]}>
            <Col span={12}>
              <Statistic 
                title="Agentes" 
                value={agents.length} 
                valueStyle={{ color: '#4CAF50', fontSize: 16 }}
              />
            </Col>
            <Col span={12}>
              <Statistic 
                title="Eventos" 
                value={events.length} 
                valueStyle={{ color: '#F44336', fontSize: 16 }}
              />
            </Col>
            <Col span={12}>
              <Statistic 
                title="Cidadãos" 
                value={agents.filter(a => a.type === 'citizen').length} 
                valueStyle={{ color: '#4CAF50', fontSize: 14 }}
              />
            </Col>
            <Col span={12}>
              <Statistic 
                title="Empresas" 
                value={agents.filter(a => a.type === 'business').length} 
                valueStyle={{ color: '#2196F3', fontSize: 14 }}
              />
            </Col>
          </Row>
        </Card>
      </div>

      {/* Legenda */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        zIndex: 1000
      }}>
        <Card size="small" style={{ background: 'rgba(0,0,0,0.8)', color: 'white' }}>
          <div style={{ color: 'white', marginBottom: 8, fontWeight: 'bold' }}>Legenda:</div>
          <Space direction="vertical" size="small">
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: '#4CAF50', 
                borderRadius: '50%',
                marginRight: 8 
              }} />
              <span style={{ fontSize: 12 }}>Cidadãos</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: '#2196F3', 
                marginRight: 8 
              }} />
              <span style={{ fontSize: 12 }}>Empresas</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: '#9C27B0', 
                marginRight: 8 
              }} />
              <span style={{ fontSize: 12 }}>Governo</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: '#FF9800', 
                marginRight: 8 
              }} />
              <span style={{ fontSize: 12 }}>Infraestrutura</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: '#F44336', 
                borderRadius: '50%',
                marginRight: 8 
              }} />
              <span style={{ fontSize: 12 }}>Crise</span>
            </div>
          </Space>
        </Card>
      </div>
    </div>
  );
};

export default City3DVisualization;
