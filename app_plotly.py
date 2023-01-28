import json
import itertools  # itertools.combinations may be useful
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scipy
import pandas as pd
import streamlit as st
import pickle
import plotly.graph_objects as go
import plotly.express as px
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

# Cache the dataframe so it's only loaded once
@st.experimental_memo
def load_data(dataset):
    G = pickle.load(open(f'saved_variables/graph_{dataset}.txt','rb'))
    lg = pickle.load(open(f'saved_variables/longest_chain_{dataset}.txt','rb'))
    cyc = pickle.load(open(f'saved_variables/simple_cycles_{dataset}.txt','rb'))
    df = pickle.load(open(f'saved_variables/dataframe_{dataset}.txt','rb')) # big dataframe
    df = df.sort_values(by=['Source'])
    return G,lg,cyc,df

def plotter(G,df,title):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
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
    node_chr = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_id.append(node)
        if df[df['Source']==node].Chromosome.values[0] == 'X':
            node_chr.append(23)
        elif df[df['Source']==node].Chromosome.values[0] == 'Y':
            node_chr.append(24)
        elif df[df['Source']==node].Chromosome.values[0] == 'M':
            node_chr.append(25)
        else:
            node_chr.append(int(df[df['Source']==node].Chromosome.values[0])) # item() returns numbers as str
    
    unique_values = len(set(df.Chromosome.to_list()))
    unique_values = len(set(node_chr))
    color_bar_values = [val for val in np.linspace(0, 1, unique_values+1) for _ in range(2)]
    discrete_colors = [val for val in px.colors.qualitative.Alphabet for _ in range(2)]
    colorscale = [[value, color] for value, color in zip(color_bar_values, discrete_colors[1:])]
    colorscale.pop(0)
    colorscale.pop(-1)

    ### Compile hover text for each node
    node_text = []
    for n,node in enumerate(G.nodes()):
        next_node='None' if n==len(G.nodes())-1 else ','.join(str(i) for i in df[df['Source']==node]['Sink'].to_list() if i!='loose')
        prev_node='None' if n==0 else ','.join(str(i) for i in df[df['Sink']==node]['Source'].to_list())
        if node_chr[n]==23:
            node_text.append(f'Prev: {prev_node}<br><b>-Node:{node}-</b><br>Next: {next_node}<br>Chromosome: X<br>CN: {node_y[n]}' )
        elif node_chr[n]==24:
            node_text.append(f'Prev: {prev_node}<br><b>-Node:{node}-</b><br>Next: {next_node}<br>Chromosome: Y<br>CN: {node_y[n]}')
        elif node_chr[n]==25:
            node_text.append(f'Prev: {prev_node}<br><b>-Node:{node}-</b><br>Next: {next_node}<br>Chromosome: M<br>CN: {node_y[n]}')
        else:
            node_text.append(f'Prev: {prev_node}<br><b>-Node:{node}-</b><br>Next: {next_node}<br>Chromosome: {node_chr[n]}<br>CN: {node_y[n]}')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            # colorscale=px.colors.qualitative.Light24,
            colorscale=colorscale,
            reversescale=True,
            color=node_chr,
            size=10,
            symbol=0,
            colorbar=dict(
                thickness=15,
                title='Chromosome Number',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Can also be assigned later like below
    # node_trace.text = node_id
    # node_trace.marker.color = node_chr

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=title,
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=15,r=5,t=40),
                    annotations=[ dict(
                        text=f"Number of nodes: {len(node_y)}",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.1, y=1 ) ],
                    xaxis=dict(showgrid=True, zeroline=True, showticklabels=True,showline=True,title_text = "Start Point"),
                    yaxis=dict(showgrid=True, zeroline=True, showticklabels=True,showline=True,title_text = "Copy Number"))
                    )

    return fig

def main():
    st.set_page_config(layout="wide")
    col1,col2 = st.columns([3,2])
    with col1:
        dataset = st.selectbox("Dataset", ['SM12_12','235884-WG01'], index=0)
        G,lg,cyc,df = load_data(dataset)
        fig_all = plotter(G,df,'Network graph of all the paths')
        st.plotly_chart(fig_all, use_container_width=True)
        fig_longest = plotter(lg,df,'Network graph of the longest chain')    
        st.plotly_chart(fig_longest, use_container_width=True)
    with col2:
        simple_cycles = plotter(cyc,df,'Network graph of the circular paths')
        st.plotly_chart(simple_cycles, use_container_width=True)
        st.write('PS: Individual nodes represent self loops')


    with st.sidebar:
        # Style and Printing
        st.subheader('SV Graph Network Connections')
        st.write('M.Unal, MD Anderson Cancer Center')
        st.write('January 2023')
        st.write('This plot shows the longest stractural variants chain found from a JaBba output file. Networkx is used for the network.')
        st.write('Hover through the nodes with your mouse to see the details of each node. Full screen and zooming is also possible on the graph. Moreover, the entire dataset is summarized in the table below.')


        st.subheader("All Nodes")

        # Prepare data
        # AgGrid(df)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            df,
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

        df = grid_response['data']
        selected = grid_response['selected_rows'] 
        df_f = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df

        # Boolean to resize the dataframe, stored as a session state variable
        st.dataframe(df_f, use_container_width=False)

if __name__ == '__main__':
    main()