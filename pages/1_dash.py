import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title="Mini Dashboard", layout="wide")

st.title('2. Sales Dashboard, Testing')
with st.sidebar:
    st.header('Filters')
    year = st.selectbox('Year' ,[2023 ,2024 ,2025])
    min_revenue = st.slider('Minimum revenue', 0, 100000, 20000, step = 5000)

np.random.seed(42)
df = pd.DataFrame({
    "year": np.random.choice([2023, 2024, 2025], size=200),
    "region": np.random.choice(["Europe", "Asia", "Americas"],size=200),
    "revenue": np.random.randint(5_000, 100_000, size=200)
})
filter = df[(df['year'] == year) & (df['revenue'] >= min_revenue)]
st.caption(f"Showing {len(filter)} rows for year {year} with revenue ≥ {min_revenue}")
col1, col2 = st.columns(2)

import altair as alt
# change color of graphs and opacity
# seperate image file using css injection, use web url

with col1:
    st.subheader("Revenue by Region")
    rev_by_region = filter.groupby('region')['revenue'].sum().reset_index()
    #st.bar_chart(rev_by_region)
    chart = alt.Chart(rev_by_region).mark_bar(
        opacity=0.6,
        color='red'
    ).encode(
        x='region:N',
        y='revenue:Q',
        tooltip=['region', 'revenue']
    ).properties(
        width=400,
        height=300
    )
    st.altair_chart(chart, use_container_width=True)


with col2:
    st.subheader("Revenue distribution")
    rev_tot = filter['revenue'].reset_index() #reset index after filtering
    chart = alt.Chart(rev_tot).mark_bar(
        opacity=0.7,
        color='blue'
    ).encode(
        x=alt.X('revenue:Q', bin=alt.Bin(extent=[20000, 100000], step=5000), title='Revenue'),
        y=alt.Y('count():Q', title='Frequency'),
        tooltip=['count():Q']
    ).properties(
        width=400,
        height=300
    )
    st.altair_chart(chart, use_container_width=True)

'''
with col2:
    st.subheader("Revenue Distribution")
    
    # DEBUG: Show what's actually in the data
    st.write(f"Debug - Total records: {len(filter)}")
    st.write(f"Debug - Revenue range: ${filter['revenue'].min():,} to ${filter['revenue'].max():,}")
    st.write(f"Debug - Revenue values sample: {sorted(filter['revenue'].unique())[:10]}")  # First 10 unique values
    
    rev_tot = filter['revenue'].reset_index()
    
    chart = alt.Chart(rev_tot).mark_bar(
        opacity=0.7,
        color='blue'
    ).encode(
        x=alt.X('revenue:Q', bin=alt.Bin(maxbins=20), title='Revenue'),
        y=alt.Y('count():Q', title='Frequency'),
        tooltip=['count():Q']
    ).properties(
        width=400,
        height=300
    )
    st.altair_chart(chart, use_container_width=True)
'''
with st.expander("See filtered data"):
    st.dataframe(filter)