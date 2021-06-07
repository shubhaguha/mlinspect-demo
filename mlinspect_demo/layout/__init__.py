import os

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from mlinspect.utils import get_project_root


CODE_FONT = {"fontFamily": "'Courier New', monospace"}
STYLE_HIDDEN = {"display": "none"}
STYLE_SHOWN = {"display": "block"}


healthcare_filename = os.path.join(get_project_root(), "example_pipelines",
                                   "healthcare", "healthcare.py")
adult_filename = os.path.join(get_project_root(), "example_pipelines",
                              "adult_demo", "adult_demo.py")
with open(healthcare_filename) as healthcare_file:
    healthcare_pipeline = healthcare_file.read()
with open(adult_filename) as adult_file:
    adult_pipeline = adult_file.read()


def create_layout():
    return dbc.Container([
        # Header and description
        dbc.Row([
            dbc.Col([
                html.H2("mlinspect"),
            ], width=4),
            dbc.Col([
                html.H2("Inspect ML Pipelines in Python in the form of a DAG.", style={"textAlign": "right"}),
            ], width=8),
        ], id="header-container", className="container", style=CODE_FONT),
        html.Hr(),

        dbc.Row([
            # Pipeline
            dbc.Col([
                # Pipeline definition
                html.Div([
                    html.H3("Pipeline Definition"),
                    dbc.FormGroup([
                        # Paste text from pipeline: Healthcare Adult
                        html.Div("Paste text from pipeline:"),
                        dbc.Button("Healthcare", id="healthcare-pipeline", color="secondary", size="lg", className="mr-1"),
                        dbc.Button("Adult Income", id="adult-pipeline", color="secondary", size="lg", className="mr-1"),
                        dbc.Textarea(id="pipeline-textarea", className="mb-3"),
                        html.Div(healthcare_pipeline, id="healthcare-pipeline-text", hidden=True),
                        html.Div(adult_pipeline, id="adult-pipeline-text", hidden=True),
                    ]),
                ], id="pipeline-definition-container", className="container"),
                # Pipeline execution output
                html.Div([
                    html.H3("Pipeline Output"),
                    html.Pre(html.Code(id="pipeline-output"), id="pipeline-output-cell"),
                ], id="pipeline-output-container", className="container", hidden=True),
            ], width=7, style={"minWidth": str(100*7/12.)+"%"}),
            # DAG
            dbc.Col([
                # Extracted DAG
                html.Div([
                    html.H3("Extracted DAG"),
                    dcc.Graph(
                        id="dag",
                        figure=go.Figure(
                            layout_width=500,
                            layout_height=500,
                            layout_showlegend=False,
                            layout_xaxis={'visible': False},
                            layout_yaxis={'visible': False},
                            layout_plot_bgcolor='rgb(255,255,255)',
                        ),
                    ),
                ], id="dag-container", className="container"),
                # Code references for highlighting source code (hidden)
                html.Div([
                    html.Div(id="hovered-code-reference"),
                    html.Div(id="selected-code-reference"),
                ], id="code-reference-container", className="container", hidden=True),
            ], width=5, style={"minWidth": str(100*5/12.)+"%"}),
        ], style={"minWidth": "100%"}),
        dbc.Row([
            # Inspections
            dbc.Col([
                dbc.FormGroup([
                    # Add inspections
                    html.H3("Inspections"),
                    html.Div([
                        html.Div([  # Histogram For Columns
                            dbc.Checkbox(id="histogramforcolumns-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("Histogram For Columns",
                                    html_for="histogramforcolumns-checkbox",
                                    className="custom-control-label"),
                            dbc.Checklist(id="histogram-sensitive-columns",
                                        options=[{"label": "label1", "value": "value1"},
                                                {"label": "label2", "value": "value2"}],
                                        style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                        html.Div([  # Row Lineage
                            dbc.Checkbox(id="rowlineage-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("Row Lineage",
                                    html_for="rowlineage-checkbox",
                                    className="custom-control-label"),
                            dbc.Input(id="rowlineage-num-rows", type="number",
                                    min=0, step=1, placeholder="Number of rows (default 5)",
                                    style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                        html.Div([  # Materialize First Output Rows
                            dbc.Checkbox(id="materializefirstoutputrows-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("Materialize First Output Rows",
                                    html_for="materializefirstoutputrows-checkbox",
                                    className="custom-control-label"),
                            dbc.Input(id="materializefirstoutputrows-num-rows", type="number",
                                    min=0, step=1, placeholder="Number of rows (default 5)",
                                    style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                    ]),
                ]),
            ], width=3, style={"minWidth": "25%"}),
            # Checks
            dbc.Col([
                dbc.FormGroup([
                    # Add checks
                    html.H3("Checks"),
                    html.Div([
                        html.Div([  # No Bias Introduced For
                            dbc.Checkbox(id="nobiasintroduced-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("No Bias Introduced For",
                                    html_for="nobiasintroduced-checkbox",
                                    className="custom-control-label"),
                            #   min_allowed_relative_ratio_change=-0.3
                            dbc.Input(id="nobiasintroduced-ratio-threshold", type="number",
                                    min=-100, max=0, step=1,
                                    placeholder="Min ratio change -30%",
                                    style=STYLE_HIDDEN, className="param"),
                            #   max_allowed_probability_difference=2.0
                            dbc.Input(id="nobiasintroduced-probability-threshold", type="number",
                                    min=0, step=1,
                                    placeholder="Max prob diff 200%",
                                    style=STYLE_HIDDEN, className="param"),
                            dbc.Checklist(id="nobiasintroduced-sensitive-columns",
                                        options=[{"label": "label1", "value": "value1"},
                                                {"label": "label2", "value": "value2"}],
                                        style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                        html.Div([  # No Illegal Features
                            dbc.Checkbox(id="noillegalfeatures-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("No Illegal Features",
                                    html_for="noillegalfeatures-checkbox",
                                    className="custom-control-label"),
                            dbc.Input(id="noillegalfeatures-additionalnames", type="text",
                                    placeholder="Optional additional features (comma-separated)",
                                    style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                        html.Div([  # No Missing Embeddings
                            dbc.Checkbox(id="nomissingembeddings-checkbox",
                                        className="custom-control-input"),
                            dbc.Label("No Missing Embeddings",
                                    html_for="nomissingembeddings-checkbox",
                                    className="custom-control-label"),
                            dbc.Input(id="nomissingembeddings-threshold", type="number",
                                    placeholder="Default threshold 10",
                                    style=STYLE_HIDDEN, className="param"),
                        ], className="custom-switch custom-control"),
                    ], id="checks"),
                ]),
            ], width=3, style={"minWidth": "25%"}),
            # Execute
            dbc.Col([
                # Execute inspection
                html.Br(),
                html.Br(),
                dbc.Button(id="execute", color="primary", size="lg", className="mr-1 play-button"),
            ], width=1, style={"minWidth": str(100*1/12.)+"%"}),
            # Details
            dbc.Col([
                # Summary
                html.Div([
                    html.H3("Summary of Checks", id="results-summary-header"),
                    html.Div("Enable checks and execute to see results", id="results-summary"),
                ], id="results-summary-container"),
                # Details
                html.Br(),
                html.Br(),
                html.Div([
                    html.H3("Details", id="results-details-header"),
                    html.Div("Select an operator in the DAG to see operator-specific details",
                            id="results-details"),
                ], id="results-details-container"),
            ], id="results-container", width=5, style={"minWidth": str(100*5/12.)+"%"}),
        ], id="inspector-definition-container", className="container", style={"minWidth": "100%"}),
        html.Div(id="clientside-pipeline-code", hidden=True)
    ], style={"fontSize": "14px"}, id="app-container")
