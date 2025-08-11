
# streamlit_spider_map_filtered.py

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

@st.cache_data
def load_data(filepath):
    return pd.read_csv(filepath)

def build_filtered_graph(df, focus_account):
    G = nx.DiGraph()
    filtered_df = df[(df['from_account'] == focus_account) | (df['to_account'] == focus_account)]

    for _, row in filtered_df.iterrows():
        G.add_edge(row['from_account'], row['to_account'],
                   amount=row['amount'],
                   timestamp=row['timestamp'],
                   ip=row['ip'],
                   email=row['email'],
                   phone=row['phone'],
                   from_holder=row['from_holder'],
                   from_bank=row['from_bank'],
                   to_holder=row['to_holder'],
                   to_bank=row['to_bank'])
    return G, filtered_df

def visualize_spider_map(G, focus_account):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))

    node_colors = ['red' if n == focus_account else 'skyblue' for n in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=1500, node_color=node_colors, font_size=8, arrows=True)

    edge_labels = {(u, v): f"{d['amount']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    st.pyplot(plt)

# Streamlit UI
st.title("Filtered Spider Graph - Direct Transactions Only")

account_input = st.text_input("Enter Bank Account ID (e.g., ACC1350):")

if account_input:
    df = load_data("detailed_transaction_data.csv")

    if (df['from_account'] == account_input).any() or (df['to_account'] == account_input).any():
        st.subheader(f"🕸️ Spider Map for Direct Transactions: {account_input}")
        G, filtered = build_filtered_graph(df, account_input)
        visualize_spider_map(G, account_input)

        st.subheader("📄 Related Transactions (Only Direct)")
        display_df = filtered[[
            'from_holder', 'from_account', 'from_bank',
            'to_holder', 'to_account', 'to_bank',
            'amount', 'timestamp', 'ip', 'email', 'phone'
        ]].rename(columns={
            'from_holder': 'Sender Name',
            'from_account': 'Sender Account',
            'from_bank': 'Sender Bank',
            'to_holder': 'Receiver Name',
            'to_account': 'Receiver Account',
            'to_bank': 'Receiver Bank',
            'timestamp': 'Transaction Date'
        })

        st.dataframe(display_df)
    else:
        st.warning("Account not found in the dataset.")
