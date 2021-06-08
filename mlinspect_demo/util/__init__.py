from contextlib import redirect_stdout
from inspect import cleandoc
from io import StringIO

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import networkx as nx
import numpy as np
import plotly.graph_objects as go

from demo.feature_overview.no_missing_embeddings import NoMissingEmbeddings
from mlinspect import PipelineInspector
from mlinspect.checks import NoBiasIntroducedFor, NoIllegalFeatures
from mlinspect.inspections import HistogramForColumns, RowLineage, MaterializeFirstOutputRows

from ..globals import INSPECTOR_RESULT, POS_DICT


INSPECTION_SWITCHER = {
    "HistogramForColumns": HistogramForColumns,
    "RowLineage": RowLineage,
    "MaterializeFirstOutputRows": MaterializeFirstOutputRows,
}


CHECK_SWITCHER = {
    "NoBiasIntroducedFor": NoBiasIntroducedFor,
    "NoIllegalFeatures": NoIllegalFeatures,
    "NoMissingEmbeddings": NoMissingEmbeddings,
}


def execute_inspector_builder(pipeline, checks=None, inspections=None):
    """Extract DAG the original way, i.e. by creating a PipelineInspectorBuilder."""
    global INSPECTOR_RESULT

    builder = PipelineInspector.on_pipeline_from_string(pipeline)
    for inspection_name, (inspection_bool, inspection_args) in inspections.items():
        if inspection_bool:
            builder = builder.add_required_inspection(INSPECTION_SWITCHER[inspection_name](*inspection_args))
    for check_name, (check_bool, check_args) in checks.items():
        if check_bool:
            builder = builder.add_check(CHECK_SWITCHER[check_name](*check_args))

    output_file = StringIO()
    with redirect_stdout(output_file):
        INSPECTOR_RESULT = builder.execute()
    pipeline_output = output_file.getvalue()

    return pipeline_output


def _get_new_node_label(node):
    """From mlinspect.visualisation._visualisation."""
    label = cleandoc("""
            {} (L{})
            {}
            """.format(
                node.operator_type.value,
                node.code_reference.lineno,
                node.description or ""
            ))
    return label


def _get_pos(G):
    global POS_DICT
    POS_DICT = nx.nx_agraph.graphviz_layout(G, 'dot')

    nodes = G.nodes()
    edges = G.edges()

    Xn, Yn = [], []
    for node in nodes:
        x, y = POS_DICT[node]
        Xn += [x]
        Yn += [y]

    Xe, Ye = [], []
    from .addEdge import add_edge
    for edge0, edge1 in edges:
        Xe, Ye = add_edge(
            POS_DICT[edge0],
            POS_DICT[edge1],
            Xe,
            Ye,
            length_frac=1,
            # arrow_pos='end',
            arrow_length=130,
            arrow_angle=5,
            # dot_size=15,
        )

    labels = []
    annotations = []
    for node, pos in POS_DICT.items():
        labels += [_get_new_node_label(node)]
        annotations += [{
            'x': pos[0],
            'y': pos[1],
            'text': node.operator_type.short_value,
            'showarrow': False,
            'font': {
                "size": 16,
            },
        }]

    return Xn, Yn, Xe, Ye, labels, annotations


def build_graph_object(G):
    """
    Convert networkx.DiGraph to a plotly.graph_objects.Figure.

    Adapted from: https://chart-studio.plotly.com/~empet/14007/graphviz-networks-plotted-with-plotly/#/
    """
    Xn, Yn, Xe, Ye, labels, annotations = _get_pos(G)

    edges = go.Scatter(
        x=Xe, y=Ye, mode='lines', hoverinfo='none',
        line={
            'color': 'rgb(160,160,160)',
            'width': 0.75,
        },
    )
    nodes = go.Scatter(
        x=Xn, y=Yn, mode='markers', name='', hoverinfo='text', text=labels,
        marker={
            'size': 20,
            'color': 'rgb(200,200,200)',
            'line': {
                'color': 'black',
                'width': 0.5,
            },
        },
    )
    layout = go.Layout(
        font={'family': "Courier New"},
        font_color='black',
        width=500,
        height=500,
        showlegend=False,
        xaxis={'visible': False},
        yaxis={'visible': False},
        margin= {
            'l': 1,
            'r': 1,
            'b': 1,
            't': 1,
            'pad': 1,
        },
        hovermode='closest',
        plot_bgcolor='white',
    )
    layout.annotations = annotations

    fig = go.Figure(data=[edges, nodes], layout=layout)
    fig.update_layout(clickmode='event+select')

    return fig


def _highlight_dag_node_in_figure(dag_node, figure):
    # Create scatter plot of this node
    Xn, Yn = POS_DICT[dag_node]
    label = _get_new_node_label(dag_node)
    nodes = go.Scatter(
        x=[Xn], y=[Yn], mode='markers', name='', hoverinfo='text', text=[label],
        marker={
            'size': 20,
            'color': 'red',
            'line': {
                'color': 'red',
                'width': 0.5,
            },
        },
    )

    # Append scatter plot to figure
    if isinstance(figure, dict):
        figure['data'].append(nodes)
    else:
        figure.add_trace(nodes)

    return figure


def highlight_problem_nodes(fig_dict, sensitive_columns):
    """From mlinspect.checks._no_bias_introduced_for:NoBiasIntroducedFor.plot_distribution_change_histograms."""
    try:
        no_bias_check_result = INSPECTOR_RESULT.check_to_check_results[NoBiasIntroducedFor(sensitive_columns)]
    except (KeyError, TypeError):
        pass
    else:
        for node_dict in no_bias_check_result.bias_distribution_change.values():
            for distribution_change in node_dict.values():
                # Check if distribution change is acceptable
                if distribution_change.acceptable_change and distribution_change.acceptable_probability_difference:
                    continue

                # Highlight this node in figure
                fig_dict = _highlight_dag_node_in_figure(distribution_change.dag_node, fig_dict)

    # highlight embeddings operator if there are missing embeddings
    try:
        embedding_check_result = INSPECTOR_RESULT.check_to_check_results[NoMissingEmbeddings()]
    except (KeyError, TypeError):
        pass
    else:
        for dag_node, missing_embeddings_info in embedding_check_result.dag_node_to_missing_embeddings.items():
            # Check if there are any missing embeddings examples
            if not missing_embeddings_info.missing_embeddings_examples:
                continue

            # Highlight this node in figure
            fig_dict = _highlight_dag_node_in_figure(dag_node, fig_dict)

    return fig_dict


def _convert_dataframe_to_dash_table(df):
    columns = [{"name": i, "id": i} for i in df.columns]
    data = [
        {
            k: np.array2string(v, precision=2, threshold=2)
            if isinstance(v, np.ndarray) else str(v)
            for k, v in record.items()
        }
        for record in df.to_dict('records')
    ]

    return dash_table.DataTable(
        columns=columns,
        data=data,
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
    )


def get_result_summary():
    check_results = INSPECTOR_RESULT.check_to_check_results
    check_result_df = PipelineInspector.check_results_as_data_frame(check_results)
    return _convert_dataframe_to_dash_table(check_result_df)


def _create_distribution_histogram(column, distribution_dict):
    keys = list(distribution_dict.keys())
    counts = list(distribution_dict.values())
    data = go.Bar(x=keys, y=counts, text=counts, hoverinfo="text")
    title = {
        "text": f"Column '{column}' Distribution",
        "font_size": 12,
    }
    margin = {"l": 20, "r": 20, "t": 20, "b": 20}

    layout = go.Layout(title=title, margin=margin, hovermode="x",
                       autosize=False, width=380, height=300)
    figure = go.Figure(data=data, layout=layout)
    return dcc.Graph(figure=figure)


def _create_distribution_change_histograms(column, distribution_change):
    keys = distribution_change.before_and_after_df["sensitive_column_value"]
    keys = [str(key) for key in keys]  # Necessary because of null values
    before_values = distribution_change.before_and_after_df["count_before"]
    after_values = distribution_change.before_and_after_df["count_after"]
    before_text = distribution_change.before_and_after_df["ratio_before"]
    after_text = distribution_change.before_and_after_df["ratio_after"]
    before = go.Bar(x=keys, y=before_values, name="before", text=before_text, hoverinfo="text")
    after = go.Bar(x=keys, y=after_values, name="after", text=after_text, hoverinfo="text")

    data = [before, after]
    title = {
        "text": f"Column '{column}' Distribution Change",
        "font_size": 12,
    }
    margin = {"l": 20, "r": 20, "t": 20, "b": 20}

    layout = go.Layout(title=title, margin=margin, hovermode="x",
                       autosize=False, width=380, height=300)
    figure = go.Figure(data=data, layout=layout)
    figure.update_traces(hovertemplate="%{text:.2f}")
    return dcc.Graph(figure=figure)


def _create_removal_probability_histograms(column, distribution_change):
    keys = distribution_change.before_and_after_df["sensitive_column_value"]
    keys = [str(key) for key in keys]  # Necessary because of null values
    removal_probabilities = distribution_change.before_and_after_df["removal_probability"]
    data = go.Bar(
        x=keys, y=removal_probabilities,
        text=removal_probabilities,
        hoverinfo="text",
        hovertemplate="%{text:.2f}",
    )
    title = {
        "text": f"Column '{column}' Removal Probabilities",
        "font_size": 12,
    }
    margin = {"l": 20, "r": 20, "t": 20, "b": 20}

    layout = go.Layout(title=title, margin=margin, hovermode="x",
                       autosize=False, width=380, height=300)
    figure = go.Figure(data=data, layout=layout)
    return dcc.Graph(figure=figure)


def get_result_details(node,
                       histogramforcolumns, rowlineage, materializefirstoutputrows,
                       nobiasintroduced, noillegalfeatures, nomissingembeddings):
    details = []

    # Show inspection results
    for inspection, result_dict in INSPECTOR_RESULT.inspection_to_annotations.items():
        if (isinstance(inspection, RowLineage) and rowlineage) or \
            (isinstance(inspection, MaterializeFirstOutputRows) and materializefirstoutputrows):
            output_df = result_dict[node]
            output_table = _convert_dataframe_to_dash_table(output_df)
            input_tables = [
                _convert_dataframe_to_dash_table(result_dict[input_node])
                for input_node in INSPECTOR_RESULT.dag.predecessors(node)
            ]
            if input_tables:
                input_tables.insert(0, dbc.Label("Input Rows"))
            element = html.Div([
                html.H4(f"{inspection}", className="result-item-header"),
                *input_tables,
                dbc.Label("Output Rows"),
                output_table,
            ], className="result-item")
            details += [element]
        elif (isinstance(inspection, HistogramForColumns) and histogramforcolumns):
            if node not in result_dict:
                continue

            distribution_dicts = result_dict[node]
            graphs = []
            for column, distribution in distribution_dicts.items():
                graphs += [_create_distribution_histogram(column, distribution)]
            element = html.Div([
                html.H4(f"{inspection}", className="result-item-header"),
                html.Div(graphs, className="result-item-content"),
            ], className="result-item")
            details += [element]
        else:
            print("inspection not selected or not implemented:", inspection)

    # Show check results
    for check, result_obj in INSPECTOR_RESULT.check_to_check_results.items():
        if (isinstance(check, NoBiasIntroducedFor) and nobiasintroduced):
            if node not in result_obj.bias_distribution_change:
                continue
            dist_changes = result_obj.bias_distribution_change[node]
            graphs = []
            for column, distribution_change in dist_changes.items():
                graphs += [
                    _create_distribution_change_histograms(column, distribution_change),
                    _create_removal_probability_histograms(column, distribution_change),
                ]
            element = html.Div([
                html.H4(f"{check}", className="result-item-header"),
                html.Div(graphs, className="result-item-content"),
            ], className="result-item")
            details += [element]
        elif (isinstance(check, NoIllegalFeatures) and noillegalfeatures):
            # already shown in results summary
            pass
        elif (isinstance(check, NoMissingEmbeddings) and nomissingembeddings):
            if node not in result_obj.dag_node_to_missing_embeddings:
                continue
            info = result_obj.dag_node_to_missing_embeddings[node]
            element = html.Div([
                html.H4(f"{check}", className="result-item-header"),
                html.Div(info.missing_embeddings_examples,
                         className="result-item-content"),
            ], className="result-item")
            details += [element]
        else:
            print("check not selected or not implemented:", check)

    return details
