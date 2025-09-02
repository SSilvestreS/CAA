import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  TeamOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/agents',
      icon: <TeamOutlined />,
      label: 'Agentes',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
    {
      key: '/scenarios',
      icon: <ExperimentOutlined />,
      label: 'Cenários',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Configurações',
    },
  ];

  return (
    <Sider
      width={250}
      style={{
        background: '#fff',
        boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ 
        padding: '24px 16px', 
        borderBottom: '1px solid #f0f0f0',
        textAlign: 'center'
      }}>
        <h2 style={{ margin: 0, color: '#1890ff' }}>
          Cidade Inteligente
        </h2>
        <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '12px' }}>
          v1.1 - Simulação Multi-Agente
        </p>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ border: 'none', marginTop: '16px' }}
      />
    </Sider>
  );
};

export default Sidebar;
