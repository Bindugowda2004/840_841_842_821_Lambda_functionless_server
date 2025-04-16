import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None

def login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/auth/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            return True
        return False
    except:
        return False

def register(username: str, email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        return response.status_code == 200
    except:
        return False

def api_call(method: str, endpoint: str, **kwargs):
    if st.session_state.token:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers
    
    response = getattr(requests, method)(f"{API_URL}/{endpoint}", **kwargs)
    if response.status_code == 401:
        st.session_state.token = None
        st.error("Session expired. Please login again.")
        st.rerun()
    return response

st.title("Serverless Platform")

if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Register"):
                if register(new_username, new_email, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")
else:
    # Sidebar for navigation
    page = st.sidebar.selectbox("Select Page", ["Functions", "Create Function", "Metrics"])
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    if page == "Functions":
        st.header("Functions")
        
        # List all functions
        response = api_call("get", "functions/")
        if response.status_code == 200:
            functions = response.json()
            for func in functions:
                with st.expander(f"{func['name']} ({func['runtime']})"):
                    st.write(f"Route: {func['route']}")
                    st.write(f"Timeout: {func['timeout']} seconds")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Execute {func['name']}", key=f"exec_{func['id']}"):
                            execute_response = api_call("post", f"execute/{func['id']}")
                            if execute_response.status_code == 200:
                                result = execute_response.json()
                                st.success("Function executed successfully!")
                                st.json(result)
                            else:
                                st.error(f"Error executing function: {execute_response.text}")
                    with col2:
                        if st.button(f"Delete {func['name']}", key=f"del_{func['id']}"):
                            delete_response = api_call("delete", f"functions/{func['id']}")
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
                
                response = api_call("post", "functions/", json=data)
                if response.status_code == 200:
                    st.success("Function created successfully!")
                else:
                    st.error(f"Error creating function: {response.text}")

    elif page == "Metrics":
        st.header("Function Metrics")
        
        # Get list of functions
        response = api_call("get", "functions/")
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
                stats_response = api_call("get", f"metrics/stats/function/{selected_function['id']}")
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
                    
                    # Execute button
                    if st.button("Execute Function"):
                        execute_response = api_call("post", f"execute/{selected_function['id']}")
                        if execute_response.status_code == 200:
                            result = execute_response.json()
                            st.success("Function executed successfully!")
                            st.json(result)
                            st.rerun()  # Refresh metrics
                        else:
                            st.error(f"Error executing function: {execute_response.text}")
                    
                    # Get detailed metrics
                    metrics_response = api_call("get", f"metrics/function/{selected_function['id']}")
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
