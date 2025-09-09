"""
Dashboard interativo para visualização da simulação de cidade inteligente.
Usa Dash e Plotly para criar interface web em tempo real.
"""

# Imports de tipos não utilizados removidos

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# import plotly.express as px  # Não utilizado
import pandas as pd
import numpy as np
import asyncio
import threading


class CityDashboard:
    """
    Dashboard interativo para visualização da simulação de cidade inteligente.
    """

    def __init__(self, city_environment):
        self.city_environment = city_environment
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Configura o layout do dashboard"""
        self.app.layout = dbc.Container(
            [
                # Cabeçalho
                dbc.Row(
                    [dbc.Col([html.H1("🏙️ Cidade Inteligente - Dashboard", className="text-center mb-4"), html.Hr()])]
                ),
                # Controles
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Controles da Simulação"),
                                        dbc.CardBody(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "▶️ Iniciar",
                                                                    id="start-btn",
                                                                    color="success",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "⏸️ Pausar",
                                                                    id="pause-btn",
                                                                    color="warning",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "⏹️ Parar",
                                                                    id="stop-btn",
                                                                    color="danger",
                                                                    className="me-2",
                                                                ),
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                html.Br(),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.Label("Velocidade da Simulação:"),
                                                                dcc.Slider(
                                                                    id="speed-slider",
                                                                    min=0.1,
                                                                    max=5.0,
                                                                    step=0.1,
                                                                    value=1.0,
                                                                    marks={
                                                                        i: f"{i}x"
                                                                        for i in [0.1, 1.0, 2.0, 3.0, 4.0, 5.0]
                                                                    },
                                                                ),
                                                            ]
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # Métricas principais
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("📊 Métricas da Cidade"),
                                        dbc.CardBody(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.H4(
                                                                    id="population-metric", className="text-center"
                                                                ),
                                                                html.P("População", className="text-center text-muted"),
                                                            ],
                                                            width=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H4(
                                                                    id="satisfaction-metric", className="text-center"
                                                                ),
                                                                html.P(
                                                                    "Satisfação", className="text-center text-muted"
                                                                ),
                                                            ],
                                                            width=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H4(
                                                                    id="unemployment-metric", className="text-center"
                                                                ),
                                                                html.P(
                                                                    "Desemprego", className="text-center text-muted"
                                                                ),
                                                            ],
                                                            width=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H4(id="crime-metric", className="text-center"),
                                                                html.P(
                                                                    "Criminalidade", className="text-center text-muted"
                                                                ),
                                                            ],
                                                            width=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H4(id="economic-metric", className="text-center"),
                                                                html.P(
                                                                    "Saúde Econômica",
                                                                    className="text-center text-muted",
                                                                ),
                                                            ],
                                                            width=2,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H4(
                                                                    id="environmental-metric", className="text-center"
                                                                ),
                                                                html.P(
                                                                    "Saúde Ambiental",
                                                                    className="text-center text-muted",
                                                                ),
                                                            ],
                                                            width=2,
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # Gráficos principais
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("📈 Evolução das Métricas"),
                                        dbc.CardBody([dcc.Graph(id="metrics-evolution-graph")]),
                                    ]
                                )
                            ],
                            width=8,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("🎯 Distribuição de Agentes"),
                                        dbc.CardBody([dcc.Graph(id="agents-distribution-graph")]),
                                    ]
                                )
                            ],
                            width=4,
                        ),
                    ],
                    className="mb-4",
                ),
                # Mapa da cidade e eventos
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [dbc.CardHeader("🗺️ Mapa da Cidade"), dbc.CardBody([dcc.Graph(id="city-map-graph")])]
                                )
                            ],
                            width=8,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("⚡ Eventos Ativos"),
                                        dbc.CardBody([html.Div(id="active-events-list")]),
                                    ]
                                )
                            ],
                            width=4,
                        ),
                    ],
                    className="mb-4",
                ),
                # Análise de mercado
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("💰 Análise de Mercado"),
                                        dbc.CardBody([dcc.Graph(id="market-analysis-graph")]),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("🏢 Performance das Empresas"),
                                        dbc.CardBody([dcc.Graph(id="business-performance-graph")]),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                # Log de eventos
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("📝 Log de Eventos"),
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    id="events-log",
                                                    style={
                                                        "height": "300px",
                                                        "overflow-y": "scroll",
                                                        "border": "1px solid #dee2e6",
                                                        "padding": "10px",
                                                        "background-color": "#f8f9fa",
                                                    },
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ]
                ),
                # Intervalo para atualização automática
                dcc.Interval(id="interval-component", interval=2000, n_intervals=0),  # Atualiza a cada 2 segundos
            ],
            fluid=True,
        )

    def setup_callbacks(self):
        """Configura os callbacks do dashboard"""

        @self.app.callback(
            [
                Output("population-metric", "children"),
                Output("satisfaction-metric", "children"),
                Output("unemployment-metric", "children"),
                Output("crime-metric", "children"),
                Output("economic-metric", "children"),
                Output("environmental-metric", "children"),
            ],
            [Input("interval-component", "n_intervals")],
        )
        def update_metrics(n):
            """Atualiza métricas principais"""
            status = self.city_environment.get_city_status()
            metrics = status["metrics"]

            return (
                f"{metrics['population']:,}",
                f"{metrics['citizen_satisfaction']:.1%}",
                f"{metrics['unemployment_rate']:.1%}",
                f"{metrics['crime_rate']:.1%}",
                f"{metrics['economic_health']:.1%}",
                f"{metrics['environmental_health']:.1%}",
            )

        @self.app.callback(Output("metrics-evolution-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_metrics_evolution(n):
            """Atualiza gráfico de evolução das métricas"""
            history = self.city_environment.get_metrics_history()

            if not history:
                return go.Figure()

            df = pd.DataFrame(history)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            fig = go.Figure()

            # Adiciona linhas para cada métrica
            metrics_to_plot = [
                "citizen_satisfaction",
                "economic_health",
                "infrastructure_health",
                "environmental_health",
            ]

            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

            for i, metric in enumerate(metrics_to_plot):
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df[metric],
                        mode="lines",
                        name=metric.replace("_", " ").title(),
                        line=dict(color=colors[i]),
                    )
                )

            fig.update_layout(
                title="Evolução das Métricas da Cidade",
                xaxis_title="Tempo",
                yaxis_title="Valor (0-1)",
                hovermode="x unified",
            )

            return fig

        @self.app.callback(Output("agents-distribution-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_agents_distribution(n):
            """Atualiza gráfico de distribuição de agentes"""
            status = self.city_environment.get_city_status()
            agents_count = status["agents_count"]

            labels = list(agents_count.keys())[1:]  # Remove 'total'
            values = list(agents_count.values())[1:]

            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])

            fig.update_layout(title="Distribuição de Agentes", showlegend=True)

            return fig

        @self.app.callback(Output("city-map-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_city_map(n):
            """Atualiza mapa da cidade"""
            agent_data = self.city_environment.get_agent_data()

            fig = go.Figure()

            # Cidadãos
            if agent_data["citizens"]:
                citizens_df = pd.DataFrame(agent_data["citizens"])
                fig.add_trace(
                    go.Scatter(
                        x=citizens_df["position"].apply(lambda x: x[0]),
                        y=citizens_df["position"].apply(lambda x: x[1]),
                        mode="markers",
                        marker=dict(size=6, color="blue", opacity=0.6),
                        name="Cidadãos",
                        text=citizens_df["name"],
                        hovertemplate="<b>%{text}</b><br>Satisfação: %{customdata:.1%}<extra></extra>",
                        customdata=citizens_df["satisfaction"],
                    )
                )

            # Empresas
            if agent_data["businesses"]:
                businesses_df = pd.DataFrame(agent_data["businesses"])
                fig.add_trace(
                    go.Scatter(
                        x=businesses_df["position"].apply(lambda x: x[0]),
                        y=businesses_df["position"].apply(lambda x: x[1]),
                        mode="markers",
                        marker=dict(size=10, color="green", symbol="square", opacity=0.8),
                        name="Empresas",
                        text=businesses_df["name"],
                        hovertemplate="<b>%{text}</b><br>Tipo: %{customdata}<extra></extra>",
                        customdata=businesses_df["business_type"],
                    )
                )

            # Infraestrutura
            if agent_data["infrastructure"]:
                infra_df = pd.DataFrame(agent_data["infrastructure"])
                fig.add_trace(
                    go.Scatter(
                        x=infra_df["position"].apply(lambda x: x[0]),
                        y=infra_df["position"].apply(lambda x: x[1]),
                        mode="markers",
                        marker=dict(size=12, color="red", symbol="diamond", opacity=0.8),
                        name="Infraestrutura",
                        text=infra_df["name"],
                        hovertemplate="<b>%{text}</b><br>Tipo: %{customdata}<extra></extra>",
                        customdata=infra_df["infrastructure_type"],
                    )
                )

            fig.update_layout(
                title="Mapa da Cidade", xaxis_title="Coordenada X", yaxis_title="Coordenada Y", showlegend=True
            )

            return fig

        @self.app.callback(Output("active-events-list", "children"), [Input("interval-component", "n_intervals")])
        def update_active_events(n):
            """Atualiza lista de eventos ativos"""
            active_events = self.city_environment.active_events

            if not active_events:
                return html.P("Nenhum evento ativo", className="text-muted")

            event_cards = []
            for event in active_events:
                event_cards.append(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(event.description, className="card-title"),
                                    html.P(f"Duração restante: {event.duration} ciclos"),
                                    html.Small(f"Tipo: {event.event_type}", className="text-muted"),
                                ]
                            )
                        ],
                        className="mb-2",
                    )
                )

            return event_cards

        @self.app.callback(Output("market-analysis-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_market_analysis(n):
            """Atualiza análise de mercado"""
            agent_data = self.city_environment.get_agent_data()

            if not agent_data["businesses"]:
                return go.Figure()

            businesses_df = pd.DataFrame(agent_data["businesses"])

            # Agrupa por tipo de negócio
            business_metrics = (
                businesses_df.groupby("business_type")
                .agg(
                    {
                        "current_price": "mean",
                        "business_metrics": lambda x: np.mean([m.get("profit_margin", 0) for m in x]),
                    }
                )
                .reset_index()
            )

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=business_metrics["business_type"],
                    y=business_metrics["current_price"],
                    name="Preço Médio",
                    yaxis="y",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=business_metrics["business_type"],
                    y=business_metrics["business_metrics"],
                    mode="markers+lines",
                    name="Margem de Lucro",
                    yaxis="y2",
                    marker=dict(size=10),
                )
            )

            fig.update_layout(
                title="Análise de Mercado por Setor",
                xaxis_title="Tipo de Negócio",
                yaxis=dict(title="Preço Médio", side="left"),
                yaxis2=dict(title="Margem de Lucro", side="right", overlaying="y"),
                hovermode="x unified",
            )

            return fig

        @self.app.callback(Output("business-performance-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_business_performance(n):
            """Atualiza performance das empresas"""
            agent_data = self.city_environment.get_agent_data()

            if not agent_data["businesses"]:
                return go.Figure()

            businesses_df = pd.DataFrame(agent_data["businesses"])

            # Extrai métricas de negócio
            business_metrics = []
            for _, business in businesses_df.iterrows():
                metrics = business["business_metrics"]
                business_metrics.append(
                    {
                        "name": business["name"],
                        "revenue": metrics.get("revenue", 0),
                        "profit_margin": metrics.get("profit_margin", 0),
                        "market_share": metrics.get("market_share", 0),
                        "customer_satisfaction": metrics.get("customer_satisfaction", 0),
                    }
                )

            metrics_df = pd.DataFrame(business_metrics)

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=metrics_df["revenue"],
                    y=metrics_df["profit_margin"],
                    mode="markers",
                    marker=dict(
                        size=metrics_df["market_share"] * 50,
                        color=metrics_df["customer_satisfaction"],
                        colorscale="Viridis",
                        showscale=True,
                        colorbar=dict(title="Satisfação do Cliente"),
                    ),
                    text=metrics_df["name"],
                    hovertemplate="<b>%{text}</b><br>Receita: %{x:,.0f}<br>Margem: %{y:.1%}<br>Participação: %{marker.size:.1%}<extra></extra>",
                )
            )

            fig.update_layout(
                title="Performance das Empresas",
                xaxis_title="Receita",
                yaxis_title="Margem de Lucro",
                hovermode="closest",
            )

            return fig

        @self.app.callback(Output("events-log", "children"), [Input("interval-component", "n_intervals")])
        def update_events_log(n):
            """Atualiza log de eventos"""
            event_history = self.city_environment.event_history

            if not event_history:
                return html.P("Nenhum evento registrado", className="text-muted")

            # Mostra últimos 10 eventos
            recent_events = event_history[-10:]

            log_entries = []
            for event in reversed(recent_events):
                timestamp = event.timestamp.strftime("%H:%M:%S")
                log_entries.append(
                    html.Div(
                        [
                            html.Small(f"[{timestamp}] ", className="text-muted"),
                            html.Strong(event.description),
                            html.Br(),
                            html.Small(f"Tipo: {event.event_type}", className="text-muted"),
                        ],
                        className="mb-2",
                    )
                )

            return log_entries

        # Callbacks para controles
        @self.app.callback(Output("start-btn", "disabled"), [Input("start-btn", "n_clicks")])
        def start_simulation(n_clicks):
            """Inicia a simulação"""
            if n_clicks:
                # Inicia simulação em thread separada
                def run_simulation():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.city_environment.start_simulation())

                thread = threading.Thread(target=run_simulation)
                thread.daemon = True
                thread.start()

                return True
            return False

        @self.app.callback(Output("pause-btn", "disabled"), [Input("pause-btn", "n_clicks")])
        def pause_simulation(n_clicks):
            """Pausa a simulação"""
            if n_clicks:
                self.city_environment.simulation_speed = 0.1  # Velocidade muito baixa
                return True
            return False

        @self.app.callback(Output("stop-btn", "disabled"), [Input("stop-btn", "n_clicks")])
        def stop_simulation(n_clicks):
            """Para a simulação"""
            if n_clicks:
                asyncio.create_task(self.city_environment.stop_simulation())
                return True
            return False

        @self.app.callback(Output("city_environment", "simulation_speed"), [Input("speed-slider", "value")])
        def update_simulation_speed(speed):
            """Atualiza velocidade da simulação"""
            self.city_environment.simulation_speed = speed
            return speed

    def run(self, host="127.0.0.1", port=8050, debug=True):
        """Executa o dashboard"""
        print(f"Dashboard iniciado em http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)
