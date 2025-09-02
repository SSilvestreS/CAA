import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import { Layout } from 'antd';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Analytics from './pages/Analytics';
import Scenarios from './pages/Scenarios';
import Settings from './pages/Settings';
import './App.css';

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider locale={ptBR}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Sidebar />
          <Layout>
            <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/agents" element={<Agents />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/scenarios" element={<Scenarios />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App;
