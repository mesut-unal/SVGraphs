import json
import itertools  # itertools.combinations may be useful
import networkx as nx
import matplotlib.pyplot as plt
import scipy
import pandas as pd
import streamlit as st
import pickle
import plotly.graph_objects as go
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

# Cache the dataframe so it's only loaded once
@st.experimental_memo
def load_data():
    lg = pickle.load(open('tmp/graph.txt','rb'))
    df = pickle.load(open('tmp/dataframe.txt','rb')) # big dataframe
    df = df.sort_values(by=['Source'])
    return lg,df


def main():

    lg,data = load_data()

    edge_x = []
    edge_y = []
    for edge in lg.edges():
        x0, y0 = lg.nodes[edge[0]]['pos']
        x1, y1 = lg.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = [] # position
    node_y = [] # copy number
    node_id = [] # node id
    for node in lg.nodes():
        x, y = lg.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_id.append(node)

    # print(node_x)
    # print(node_y)
    # print(node_id)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=y,
            size=10,
            colorbar=dict(
                thickness=15,
                title='Copy Number',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_trace.text = node_id
    node_trace.marker.color = node_y


    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Network graph of the longest chain',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=15,r=5,t=40),
                annotations=[ dict(
                    text=f"Length of the chain: {len(node_y)}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.1, y=1 ) ],
                xaxis=dict(showgrid=False, zeroline=True, showticklabels=True),
                yaxis=dict(showgrid=False, zeroline=True, showticklabels=True))
                )
    #fig.show()

    st.plotly_chart(fig, use_container_width=True)

    with st.sidebar:



        # Style and Printing
        st.subheader('SV Graph Network Connections')
        st.write('M.Unal, MD Anderson Cancer Center')
        st.write('January 2023')
        st.write('This plot shows the longest stractural variants chain found. Networkx is used for the network.')

        st.subheader("All Nodes")

        # Prepare data
        # AgGrid(df)
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            #theme='blue', #Add theme color to the table
            enable_enterprise_modules=True,
            height=350, 
            width='100%',
            reload_data=True,
        )

        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df

        # Boolean to resize the dataframe, stored as a session state variable
        st.dataframe(df, use_container_width=False)

if __name__ == '__main__':
    main()