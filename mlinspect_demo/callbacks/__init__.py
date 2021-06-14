import json

import dash
from dash.dependencies import Input, Output, State

from dataclasses_serialization.json import JSONSerializer

from example_pipelines import HEALTHCARE_DATA, ADULT_DATA
from ..layout import CODE_FONT, STYLE_HIDDEN, STYLE_SHOWN
from ..util import execute_inspector_builder, build_graph_object, highlight_problem_nodes, get_result_summary, get_result_details


def create_callbacks(app):
    _update_pipeline_text(app)
    _show_hide_elements(app)
    _execute(app)
    _interact_with_dag(app)


def _update_pipeline_text(app):
    app.clientside_callback(
        """
        function(n_clicks) {
            var editor = document.querySelector('#pipeline-textarea');
            return editor.value;
        }
        """,
        Output('clientside-pipeline-code', 'children'),
        Input("execute", "n_clicks")
    )

    app.clientside_callback(
        """
        function(healthcare_clicked, adult_clicked) {
            const ctx = dash_clientside.callback_context;
            if (ctx.triggered.length === 0) {
                return '';
            }
            const prop_id = ctx.triggered[0]["prop_id"];

            var text = '';
            if (prop_id.startsWith("healthcare")) {
                const healthcareElem = document.getElementById('healthcare-pipeline-text');
                text = healthcareElem.textContent;
            } else if (prop_id.startsWith("adult")) {
                const adultElem = document.getElementById('adult-pipeline-text');
                text = adultElem.textContent;
            }

            var editor = document.querySelector('.CodeMirror').CodeMirror;
            editor.setValue(text);

            return text;
        }
        """,
        Output("pipeline-textarea", "value"),
        [
            Input("healthcare-pipeline", "n_clicks"),
            Input("adult-pipeline", "n_clicks"),
        ]
    )

    @app.callback(
        [
            Output("histogram-sensitive-columns", "options"),
            Output("histogram-sensitive-columns", "value"),
            Output("nobiasintroduced-sensitive-columns", "options"),
            Output("nobiasintroduced-sensitive-columns", "value"),
        ],
        [
            Input("healthcare-pipeline", "n_clicks"),
            Input("adult-pipeline", "n_clicks"),
        ],
    )
    def on_sensitive_column_options_changed(healthcare_clicked, adult_clicked):
        if not healthcare_clicked and not adult_clicked:
            return [dash.no_update]*4

        ctx = dash.callback_context
        elem_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if elem_id == "healthcare-pipeline":
            columns = HEALTHCARE_DATA.columns
        elif elem_id == "adult-pipeline":
            columns = ADULT_DATA.columns
        else:
            columns = []

        options = [{"label": c, "value": c} for c in columns]
        return options, [], options, []


def _show_hide_elements(app):
    @app.callback(
        Output("histogram-sensitive-columns", "style"),
        Input("histogramforcolumns-checkbox", "checked"),
    )
    def on_histogramforcolumns_checked(checked):
        """Show checklist of sensitive columns if HistogramForColumns is selected."""
        if checked:
            return {**STYLE_SHOWN, **CODE_FONT}
        return STYLE_HIDDEN

    @app.callback(
        Output("rowlineage-num-rows", "style"),
        Input("rowlineage-checkbox", "checked"),
    )
    def on_rowlineage_checked(checked):
        """Show input for number of rows if RowLineage is selected."""
        if checked:
            return STYLE_SHOWN
        return STYLE_HIDDEN

    @app.callback(
        Output("materializefirstoutputrows-num-rows", "style"),
        Input("materializefirstoutputrows-checkbox", "checked"),
    )
    def on_materializefirstoutputrows_checked(checked):
        """Show input for number of rows if MaterializeFirstOutputRows is selected."""
        if checked:
            return STYLE_SHOWN
        return STYLE_HIDDEN

    @app.callback(
        [
            Output("nobiasintroduced-ratio-threshold", "style"),
            Output("nobiasintroduced-probability-threshold", "style"),
            Output("nobiasintroduced-sensitive-columns", "style"),
        ],
        Input("nobiasintroduced-checkbox", "checked"),
    )
    def on_nobiasintroduced_checked(checked):
        """Show checklist of sensitive columns if NoBiasIntroducedFor is selected."""
        if checked:
            return STYLE_SHOWN, STYLE_SHOWN, {**STYLE_SHOWN, **CODE_FONT}
        return STYLE_HIDDEN, STYLE_HIDDEN, STYLE_HIDDEN

    @app.callback(
        Output("noillegalfeatures-additionalnames", "style"),
        Input("noillegalfeatures-checkbox", "checked"),
    )
    def on_noillegalfeatures_checked(checked):
        if checked:
            return STYLE_SHOWN
        return STYLE_HIDDEN

    @app.callback(
        Output("nomissingembeddings-threshold", "style"),
        Input("nomissingembeddings-checkbox", "checked")
    )
    def on_nomissingembeddings_checked(checked):
        if checked:
            return STYLE_SHOWN
        return STYLE_HIDDEN


def _execute(app):
    @app.callback(
        [
            # Output("inspector-result", "data"),
            # Output("pos-dict", "data"),
            Output("dag", "figure"),
            Output("pipeline-output", "children"),
            Output("pipeline-output-container", "hidden"),
            Output("dag", "selectedData"),
            Output("results-summary", "children"),
        ],
        Input("execute", "n_clicks"),
        Input("clientside-pipeline-code", "children"),
        state=[
            # HistogramForColumns
            State("histogramforcolumns-checkbox", "checked"),
            State("histogram-sensitive-columns", "value"),
            # RowLineage
            State("rowlineage-checkbox", "checked"),
            State("rowlineage-num-rows", "value"),
            # MaterializeFirstOutputRows
            State("materializefirstoutputrows-checkbox", "checked"),
            State("materializefirstoutputrows-num-rows", "value"),
            # NoBiasIntroducedFor
            State("nobiasintroduced-checkbox", "checked"),
            State("nobiasintroduced-sensitive-columns", "value"),
            State("nobiasintroduced-ratio-threshold", "value"),
            State("nobiasintroduced-probability-threshold", "value"),
            # NoIllegalFeatures
            State("noillegalfeatures-checkbox", "checked"),
            State("noillegalfeatures-additionalnames", "value"),
            # NoMissingEmbeddings
            State("nomissingembeddings-checkbox", "checked"),
            State("nomissingembeddings-threshold", "value"),
        ]
    )
    def on_execute(execute_clicks, pipeline,
                   # Inspections
                   histogramforcolumns, histogramforcolumns_sensitive_columns,
                   rowlineage, rowlineage_num_rows,
                   materializefirstoutputrows, materializefirstoutputrows_num_rows,
                   # Checks
                   nobiasintroduced, nobiasintroduced_sensitive_columns,
                   nobiasintroduced_ratio_threshold, nobiasintroduced_probability_threshold,
                   noillegalfeatures, noillegalfeatures_additional_names,
                   nomissingembeddings, nomissingembeddings_threshold):
        """
        When user clicks 'execute' button, show extracted DAG including potential
        problem nodes in red.
        """
        if not execute_clicks or not pipeline:
            return [dash.no_update]*5

        ### Execute pipeline and inspections
        # [RowLineage, MaterializeFirstOutputRows] set default num rows to 5
        rowlineage_num_rows = rowlineage_num_rows or 5
        materializefirstoutputrows_num_rows = materializefirstoutputrows_num_rows or 5
        # [RowLineage, MaterializeFirstOutputRows] if both enabled, display the higher number of rows
        if materializefirstoutputrows and rowlineage:
            rowlineage_num_rows = max(rowlineage_num_rows, materializefirstoutputrows_num_rows)
        # [RowLineage, MaterializeFirstOutputRows] don't include MaterializeFirstOutputRows if RowLineage also checked
        materializefirstoutputrows = materializefirstoutputrows and not rowlineage
        # [NoBiasIntroducedFor]
        if nobiasintroduced_ratio_threshold:
            # convert percentage to decimal
            nobiasintroduced_ratio_threshold = nobiasintroduced_ratio_threshold/100.
        else:
            # use default value if None
            nobiasintroduced_ratio_threshold = -0.3
        if nobiasintroduced_probability_threshold:
            # convert percentage to decimal
            nobiasintroduced_probability_threshold = nobiasintroduced_probability_threshold/100.
        else:
            # use default value if None
            nobiasintroduced_probability_threshold = 2.0
        # [NoIllegalFeatures]
        noillegalfeatures_additional_names = noillegalfeatures_additional_names.split(",") \
                                             if noillegalfeatures_additional_names else []
        # [NoMissingEmbeddings]
        nomissingembeddings_threshold = nomissingembeddings_threshold or 10
        # construct arguments for inspector builder
        inspections = {
            "HistogramForColumns": (histogramforcolumns, [histogramforcolumns_sensitive_columns]),
            "RowLineage": (rowlineage, [rowlineage_num_rows or 5]),
            "MaterializeFirstOutputRows": (materializefirstoutputrows,
                                        [materializefirstoutputrows_num_rows or 5]),
        }
        checks = {
            "NoBiasIntroducedFor": (nobiasintroduced, [
                nobiasintroduced_sensitive_columns,
                nobiasintroduced_ratio_threshold,
                nobiasintroduced_probability_threshold,
            ]),
            "NoIllegalFeatures": (noillegalfeatures, [noillegalfeatures_additional_names]),
            "NoMissingEmbeddings": (nomissingembeddings, [nomissingembeddings_threshold]),
        }
        pipeline_output = execute_inspector_builder(pipeline, checks, inspections)
        hide_output = False

        ### Convert extracted DAG into plotly figure
        from ..util import INSPECTOR_RESULT
        figure = build_graph_object(INSPECTOR_RESULT.dag)

        ### Highlight problematic nodes
        figure = highlight_problem_nodes(figure, nobiasintroduced_sensitive_columns)

        ### De-select any DAG nodes and trigger callback to reset details div
        selected_data = {}

        ### Summary check results
        if INSPECTOR_RESULT.check_to_check_results:
            summary = get_result_summary()
        else:
            summary = dash.no_update

        # TODO: inspector_result = JSONSerializer.serialize(inspector_result)
        # TODO: serialize and store POS_DICT as well

        return figure, pipeline_output, hide_output, selected_data, summary


def _interact_with_dag(app):
    @app.callback(
        Output("hovered-code-reference", "children"),
        Input("dag", "hoverData"),
        # state=[
        #     State("pos-dict", "data"),
        # ],
    )
    def on_dag_node_hover(hover_data):
        """
        When user hovers on DAG node, show node label and emphasize corresponding
        source code.
        """
        # Un-highlight source code
        if not hover_data:
            return []

        # Find DagNode object at this position
        point = hover_data['points'][0]
        x = point['x']
        y = point['y']
        try:
            from ..util import POS_DICT
            node = [node for node, pos in POS_DICT.items() if pos == (x, y)][0]
        except IndexError:
            print(f"[hover] Could not find node with pos {x} and {y}")
            return dash.no_update

        # Highlight source code
        code_ref = node.code_reference
        return json.dumps(code_ref.__dict__)

    @app.callback(
        [
            Output("selected-code-reference", "children"),
            Output("results-details", "children"),
            Output("results-details-header", "children"),
        ],
        [
            Input("dag", "selectedData"),
        ],
        state=[
            # State("inspector-result", "data"),
            # State("pos-dict", "data"),
            State("histogramforcolumns-checkbox", "checked"),
            State("rowlineage-checkbox", "checked"),
            State("materializefirstoutputrows-checkbox", "checked"),
            State("nobiasintroduced-checkbox", "checked"),
            State("noillegalfeatures-checkbox", "checked"),
            State("nomissingembeddings-checkbox", "checked"),
        ]
    )
    def on_dag_node_select(selected_data, *inspections_and_checks):
        """
        When user selects DAG node, show detailed check and inspection results
        and emphasize corresponding source code.
        """
        # Un-highlight source code
        if not selected_data:
            return [], "Select an operator in the DAG to see operator-specific details", "Details"

        # Find DagNode object at this position
        point = selected_data['points'][0]
        x = point['x']
        y = point['y']
        try:
            from ..util import POS_DICT
            node = [node for node, pos in POS_DICT.items() if pos == (x, y)][0]
        except IndexError:
            print(f"[select] Could not find node with pos {x} and {y}")
            return dash.no_update, dash.no_update, dash.no_update

        # Highlight source code
        code_ref = node.code_reference

        # Populate and show div(s)
        header = "Details: Operator '{operator}', Line {code_ref}".format(
            operator=node.operator_type.value,
            code_ref=node.code_reference.lineno,
        )
        # inspector_result = JSONSerializer.deserialize(inspector_result)
        operator_details = get_result_details(node, *inspections_and_checks)

        return json.dumps(code_ref.__dict__), operator_details, header
