import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Alert, Spin } from 'antd';
import { 
  UserOutlined, 
  ShopOutlined, 
  BankOutlined, 
  ThunderboltOutlined,
  TrendingUpOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useSimulationStore } from '../store/simulationStore';
import { apiService } from '../services/apiService';

const Dashboard: React.FC = () => {
  const { simulationData, isConnected } = useSimulationStore();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await apiService.getMetrics();
        setMetrics(data);
      } catch (error) {
        console.error('Erro ao buscar métricas:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Atualiza a cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p style={{ marginTop: '16px' }}>Carregando dashboard...</p>
      </div>
    );
  }

  const chartData = metrics?.performance_history || [];

  return (
    <div>
      <h1>Dashboard da Simulação</h1>
      
      {!isConnected && (
        <Alert
          message="Conexão Perdida"
          description="Não foi possível conectar ao servidor de simulação. Verifique se o backend está rodando."
          type="warning"
          showIcon
          style={{ marginBottom: '24px' }}
        />
      )}

      <Row gutter={[16, 16]}>
        {/* Estatísticas dos Agentes */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Cidadãos"
              value={simulationData?.agents?.citizens || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Empresas"
              value={simulationData?.agents?.businesses || 0}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Governo"
              value={simulationData?.agents?.government || 0}
              prefix={<BankOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Infraestrutura"
              value={simulationData?.agents?.infrastructure || 0}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        {/* Performance do Sistema */}
        <Col xs={24} lg={12}>
          <Card title="Performance do Sistema" extra={<TrendingUpOutlined />}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Throughput"
                  value={metrics?.system_throughput || 0}
                  suffix="ops/s"
                  precision={2}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Eficiência"
                  value={metrics?.efficiency || 0}
                  suffix="%"
                  precision={1}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <Progress
                percent={Math.round((metrics?.efficiency || 0) * 100)}
                status="active"
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
            </div>
          </Card>
        </Col>

        {/* Status da Simulação */}
        <Col xs={24} lg={12}>
          <Card title="Status da Simulação" extra={<ClockCircleOutlined />}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Ciclos Executados"
                  value={simulationData?.cycles || 0}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Tempo de Execução"
                  value={simulationData?.runtime || 0}
                  suffix="s"
                  precision={1}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <Alert
                message={`Status: ${simulationData?.status || 'Desconhecido'}`}
                type={simulationData?.status === 'running' ? 'success' : 'info'}
                showIcon
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* Gráfico de Performance */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="Histórico de Performance">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="throughput" 
                  stroke="#1890ff" 
                  strokeWidth={2}
                  name="Throughput"
                />
                <Line 
                  type="monotone" 
                  dataKey="efficiency" 
                  stroke="#52c41a" 
                  strokeWidth={2}
                  name="Eficiência"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
