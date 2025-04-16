import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1"

st.title("Serverless Platform")

# Sidebar for navigation
page = st.sidebar.selectbox("Select Page", ["Functions", "Create Function", "Metrics"])

if page == "Functions":
    st.header("Functions")
    
    # List all functions
    response = requests.get(f"{API_URL}/functions/")
    if response.status_code == 200:
        functions = response.json()
        for func in functions:
            with st.expander(f"{func['name']} ({func['runtime']})"):
                st.write(f"Route: {func['route']}")
                st.write(f"Timeout: {func['timeout']} seconds")
                if st.button(f"Delete {func['name']}", key=func['id']):
                    delete_response = requests.delete(f"{API_URL}/functions/{func['id']}")
                    if delete_response.status_code == 200:
                        st.success("Function deleted!")
                        st.rerun()
    else:
        st.error("Failed to fetch functions")

elif page == "Create Function":
    st.header("Create Function")
    
    with st.form("create_function"):
        name = st.text_input("Function Name")
        runtime = st.selectbox("Runtime", ["python", "javascript"])
        route = st.text_input("Route")
        timeout = st.number_input("Timeout (seconds)", min_value=1.0, value=30.0)
        code = st.text_area("Code")
        
        if st.form_submit_button("Create"):
            data = {
                "name": name,
                "runtime": runtime,
                "route": route,
                "timeout": timeout,
                "code": code
            }
            
            response = requests.post(f"{API_URL}/functions/", json=data)
            if response.status_code == 200:
                st.success("Function created successfully!")
            else:
                st.error(f"Error creating function: {response.text}")

elif page == "Metrics":
    st.header("Function Metrics")
    
    # Get list of functions
    response = requests.get(f"{API_URL}/functions/")
    if response.status_code == 200:
        functions = response.json()
        
        # Function selector
        selected_function = st.selectbox(
            "Select Function",
            options=functions,
            format_func=lambda x: x['name']
        )
        
        if selected_function:
            # Get function stats
            stats_response = requests.get(f"{API_URL}/metrics/stats/function/{selected_function['id']}")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                # Display stats in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Executions", stats['total_executions'])
                with col2:
                    st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
                with col3:
                    st.metric("Avg Execution Time", f"{stats['avg_execution_time']:.2f}s")
                
                # Get detailed metrics
                metrics_response = requests.get(f"{API_URL}/metrics/function/{selected_function['id']}")
                if metrics_response.status_code == 200:
                    metrics = metrics_response.json()
                    if metrics:
                        # Convert to DataFrame
                        df = pd.DataFrame(metrics)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        
                        # Execution time chart
                        st.subheader("Execution Time History")
                        fig = px.line(df, x='timestamp', y='execution_time',
                                    title="Function Execution Time")
                        st.plotly_chart(fig)
                        
                        # Memory usage chart
                        st.subheader("Memory Usage History")
                        fig = px.line(df, x='timestamp', y='memory_usage',
                                    title="Function Memory Usage (MB)")
                        st.plotly_chart(fig)
                        
                        # Status distribution
                        st.subheader("Status Distribution")
                        status_counts = df['status'].value_counts()
                        fig = px.pie(values=status_counts.values,
                                   names=status_counts.index,
                                   title="Execution Status Distribution")
                        st.plotly_chart(fig)
                    else:
                        st.info("No metrics data available for this function yet.")
