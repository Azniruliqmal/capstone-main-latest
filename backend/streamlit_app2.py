# Without human-in-the-loop (nodes.py/workflow.py/api.py/validators.py)

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your API URL

st.set_page_config(
    page_title="Script Analysis API Tester",
    page_icon="🎬",
    layout="wide"
)

def main():
    st.title("🎬 Script Analysis API Tester")
    st.markdown("---")
    
    # Show API status
    show_api_status()
    
    # Check if we should show script details
    if 'show_script_details' in st.session_state and st.session_state['show_script_details']:
        script_details_from_list()
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📤 Upload & Analyze", "💾 Save Analysis", "📋 View All Scripts", "🔍 View Script Details", "🗑️ Delete Script"]
    )
    
    # Add API URL configuration in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    new_api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)
    if new_api_url != API_BASE_URL:
        st.sidebar.warning("⚠️ Restart app to apply new URL")
    
    if page == "📤 Upload & Analyze":
        upload_and_analyze_page()
    elif page == "💾 Save Analysis":
        save_analysis_page()
    elif page == "📋 View All Scripts":
        view_all_scripts_page()
    elif page == "🔍 View Script Details":
        view_script_details_page()
    elif page == "🗑️ Delete Script":
        delete_script_page()

def view_all_scripts_page():
    st.header("📋 All Analyzed Scripts")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search by filename")
    with col2:
        status_filter = st.selectbox("Filter by status", ["All", "completed", "error", "pending_review"])
    with col3:
        limit = st.selectbox("Scripts per page", [10, 25, 50, 100], index=1)
    
    if st.button("🔄 Refresh", type="secondary"):
        st.rerun()
    
    try:
        # Build query parameters
        params = {"limit": limit}
        if search_term:
            params["search"] = search_term
        if status_filter != "All":
            params["status_filter"] = status_filter
        
        response = requests.get(f"{API_BASE_URL}/analyzed-scripts", params=params)
        
        if response.status_code == 200:
            result = response.json()
            scripts = result['data']
            pagination = result['pagination']
            
            st.info(f"Found {pagination['total']} scripts (showing {pagination['returned']})")
            
            if scripts:
                # Display scripts as cards
                for script in scripts:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.subheader(f"📄 {script['filename']}")
                            st.caption(f"ID: {script['id']}")
                        
                        with col2:
                            st.write(f"**Status:** {script['status']}")
                            st.write(f"**Scenes:** {script.get('total_scenes', 'N/A')}")
                        
                        with col3:
                            st.write(f"**Budget:** ${script.get('estimated_budget', 0):,.2f}")
                            st.write(f"**Category:** {script.get('budget_category', 'N/A')}")
                        
                        with col4:
                            # Fixed: Use session state instead of page switching
                            if st.button("👁️ View", key=f"view_{script['id']}"):
                                st.session_state['selected_script_id'] = script['id']
                                st.session_state['show_script_details'] = True
                                st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"delete_{script['id']}", type="secondary"):
                                if delete_script(script['id']):
                                    st.success(f"Deleted {script['filename']}")
                                    time.sleep(1)
                                    st.rerun()
                        
                        st.markdown("---")
            else:
                st.info("No scripts found.")
                
        else:
            st.error(f"❌ Failed to fetch scripts: {response.status_code}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def script_details_from_list():
    """Display script details when coming from the list view"""
    script_id = st.session_state.get('selected_script_id', '')
    
    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to List"):
            st.session_state['show_script_details'] = False
            if 'selected_script_id' in st.session_state:
                del st.session_state['selected_script_id']
            st.rerun()
    
    with col2:
        st.header(f"🔍 Script Details - {script_id}")
    
    if script_id:
        try:
            response = requests.get(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
            
            if response.status_code == 200:
                result = response.json()
                script_data = result['data']
                
                # Basic info
                st.subheader("📋 Basic Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Filename:** {script_data['filename']}")
                    st.write(f"**File Size:** {script_data['file_size_bytes']} bytes")
                    st.write(f"**Status:** {script_data['status']}")
                    st.write(f"**Processing Time:** {script_data.get('processing_time_seconds', 0):.2f}s")
                
                with col2:
                    st.write(f"**Total Scenes:** {script_data.get('total_scenes', 'N/A')}")
                    st.write(f"**Total Characters:** {script_data.get('total_characters', 'N/A')}")
                    st.write(f"**Total Locations:** {script_data.get('total_locations', 'N/A')}")
                    st.write(f"**Created:** {script_data.get('created_at', 'N/A')}")
                
                # Analysis data tabs
                if script_data.get('script_data'):
                    st.subheader("📊 Analysis Details")
                    
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Script Data", "Cast", "Costs", "Locations", "Props"])
                    
                    with tab1:
                        display_script_data(script_data.get('script_data', {}))
                    
                    with tab2:
                        display_cast_breakdown(script_data.get('cast_breakdown', {}))
                    
                    with tab3:
                        display_cost_breakdown(script_data.get('cost_breakdown', {}))
                    
                    with tab4:
                        display_location_breakdown(script_data.get('location_breakdown', {}))
                    
                    with tab5:
                        display_props_breakdown(script_data.get('props_breakdown', {}))
                
                # Raw data expander
                with st.expander("🔧 Raw JSON Data"):
                    st.json(script_data)
                    
            elif response.status_code == 404:
                st.error("❌ Script not found")
            else:
                st.error(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def upload_and_analyze_page():
    st.header("📤 Upload & Analyze Script")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF script file",
        type=['pdf'],
        help="Upload a PDF script file to analyze"
    )
    
    if uploaded_file is not None:
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("🔍 Analyze Script", type="primary"):
            with st.spinner("Analyzing script... This may take a few minutes."):
                try:
                    # Prepare the file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    
                    # Make API request
                    response = requests.post(f"{API_BASE_URL}/analyze-script", files=files, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis completed successfully!")
                        
                        # Display metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Processing Time", f"{result['metadata']['processing_time_seconds']:.2f}s")
                        with col2:
                            st.metric("API Calls Used", result['optimization_info']['actual_calls_used'])
                        with col3:
                            st.metric("File Size", f"{result['metadata']['file_size_bytes']} bytes")
                        
                        # Store result in session state for saving
                        st.session_state['analysis_result'] = result
                        st.session_state['save_request'] = result.get('save_request')
                        
                        # Display analysis summary
                        if 'analysis_data' in result:
                            display_analysis_summary(result['analysis_data'])
                        
                        st.info("💡 Go to 'Save Analysis' page to save this result to the database.")
                        
                    else:
                        st.error(f"❌ Analysis failed: {response.status_code}")
                        st.error(response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out. The script might be too large or complex.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def save_analysis_page():
    st.header("💾 Save Analysis to Database")
    
    if 'save_request' in st.session_state and st.session_state['save_request']:
        save_data = st.session_state['save_request']
        
        st.info(f"Ready to save analysis for: **{save_data['filename']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**File Size:** {save_data['file_size_bytes']} bytes")
            st.write(f"**Processing Time:** {save_data['processing_time_seconds']:.2f}s")
        with col2:
            st.write(f"**API Calls:** {save_data['api_calls_used']}")
            st.write(f"**Original Filename:** {save_data['original_filename']}")
        
        if st.button("💾 Save to Database", type="primary"):
            with st.spinner("Saving to database..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/save-analysis",
                        json=save_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.success("✅ Analysis saved successfully!")
                        st.info(f"Database ID: **{result['database_id']}**")
                        st.info(f"Saved at: {result['saved_at']}")
                        
                        # Clear session state
                        if 'save_request' in st.session_state:
                            del st.session_state['save_request']
                        if 'analysis_result' in st.session_state:
                            del st.session_state['analysis_result']
                            
                    else:
                        st.error(f"❌ Save failed: {response.status_code}")
                        st.error(response.text)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ No analysis data to save. Please analyze a script first.")
        if st.button("Go to Upload & Analyze"):
            st.rerun()

def view_script_details_page():
    st.header("🔍 Script Details")
    
    script_id = st.text_input("Enter Script ID", value=st.session_state.get('selected_script_id', ''))
    
    if script_id and st.button("📖 Load Script Details"):
        try:
            response = requests.get(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
            
            if response.status_code == 200:
                result = response.json()
                script_data = result['data']
                
                # Basic info
                st.subheader("📋 Basic Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Filename:** {script_data['filename']}")
                    st.write(f"**File Size:** {script_data['file_size_bytes']} bytes")
                    st.write(f"**Status:** {script_data['status']}")
                    st.write(f"**Processing Time:** {script_data.get('processing_time_seconds', 0):.2f}s")
                
                with col2:
                    st.write(f"**Total Scenes:** {script_data.get('total_scenes', 'N/A')}")
                    st.write(f"**Total Characters:** {script_data.get('total_characters', 'N/A')}")
                    st.write(f"**Total Locations:** {script_data.get('total_locations', 'N/A')}")
                    st.write(f"**Created:** {script_data.get('created_at', 'N/A')}")
                
                # Analysis data tabs
                if script_data.get('script_data'):
                    st.subheader("📊 Analysis Details")
                    
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Script Data", "Cast", "Costs", "Locations", "Props"])
                    
                    with tab1:
                        display_script_data(script_data.get('script_data', {}))
                    
                    with tab2:
                        display_cast_breakdown(script_data.get('cast_breakdown', {}))
                    
                    with tab3:
                        display_cost_breakdown(script_data.get('cost_breakdown', {}))
                    
                    with tab4:
                        display_location_breakdown(script_data.get('location_breakdown', {}))
                    
                    with tab5:
                        display_props_breakdown(script_data.get('props_breakdown', {}))
                
                # Raw data expander
                with st.expander("🔧 Raw JSON Data"):
                    st.json(script_data)
                    
            elif response.status_code == 404:
                st.error("❌ Script not found")
            else:
                st.error(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def delete_script_page():
    st.header("🗑️ Delete Script")
    
    script_id = st.text_input("Enter Script ID to delete")
    
    if script_id:
        st.warning(f"⚠️ You are about to delete script: **{script_id}**")
        st.error("This action cannot be undone!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Confirm Delete", type="primary"):
                if delete_script(script_id):
                    st.success("✅ Script deleted successfully!")
                    time.sleep(2)
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel"):
                st.rerun()

def delete_script(script_id: str) -> bool:
    """Helper function to delete a script"""
    try:
        response = requests.delete(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Delete failed: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Delete error: {str(e)}")
        return False

# Helper functions for displaying analysis data
def display_analysis_summary(analysis_data):
    """Display a summary of analysis results"""
    st.subheader("📊 Analysis Summary")
    
    if 'script_data' in analysis_data:
        script_data = analysis_data['script_data']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Scenes", len(script_data.get('scenes', [])))
        with col2:
            st.metric("Characters", len(script_data.get('total_characters', [])))
        with col3:
            st.metric("Locations", len(script_data.get('total_locations', [])))
        with col4:
            st.metric("Pages", script_data.get('total_pages', 0))
    
    if 'cost_breakdown' in analysis_data:
        cost_data = analysis_data['cost_breakdown']
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Budget", f"${cost_data.get('total_costs', 0):,.2f}")
        with col2:
            st.metric("Budget Category", cost_data.get('budget_category', 'N/A'))

def display_script_data(script_data):
    """Display script data details"""
    if not script_data:
        st.info("No script data available")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Total Pages:** {script_data.get('total_pages', 0)}")
        st.write(f"**Total Words:** {script_data.get('total_words', 0)}")
        st.write(f"**Languages:** {', '.join(script_data.get('languages', []))}")
    
    with col2:
        characters = script_data.get('total_characters', [])
        locations = script_data.get('total_locations', [])
        st.write(f"**Characters ({len(characters)}):** {', '.join(characters[:5])}{'...' if len(characters) > 5 else ''}")
        st.write(f"**Locations ({len(locations)}):** {', '.join(locations[:5])}{'...' if len(locations) > 5 else ''}")

def display_cast_breakdown(cast_data):
    """Display cast breakdown details"""
    if not cast_data:
        st.info("No cast data available")
        return
    
    main_chars = cast_data.get('main_characters', [])
    supporting_chars = cast_data.get('supporting_characters', [])
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Main Characters:**")
        for char in main_chars[:10]:  # Show first 10
            st.write(f"• {char}")
    
    with col2:
        st.write("**Supporting Characters:**")
        for char in supporting_chars[:10]:  # Show first 10
            st.write(f"• {char}")
    
    if cast_data.get('casting_requirements'):
        st.write("**Casting Requirements:**")
        for req in cast_data['casting_requirements'][:5]:
            st.write(f"• {req}")

def display_cost_breakdown(cost_data):
    """Display cost breakdown details"""
    if not cost_data:
        st.info("No cost data available")
        return
    
    # Total costs overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"${cost_data.get('total_costs', 0):,.2f}")
        st.metric("Cast Costs", f"${cost_data.get('total_cast_costs', 0):,.2f}")
    
    with col2:
        st.metric("Location Costs", f"${cost_data.get('total_location_costs', 0):,.2f}")
        st.metric("Props Costs", f"${cost_data.get('total_props_costs', 0):,.2f}")
    
    with col3:
        st.metric("Equipment Costs", f"${cost_data.get('total_equipment_costs', 0):,.2f}")
        st.metric("Budget Category", cost_data.get('budget_category', 'N/A'))
    
    # Scene costs table
    scene_costs = cost_data.get('scene_costs', [])
    if scene_costs:
        st.write("**Scene Costs:**")
        df_costs = pd.DataFrame(scene_costs)
        if not df_costs.empty:
            st.dataframe(df_costs, use_container_width=True)

def display_location_breakdown(location_data):
    """Display location breakdown details"""
    if not location_data:
        st.info("No location data available")
        return
    
    unique_locations = location_data.get('unique_locations', [])
    total_days = location_data.get('total_location_days', 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Unique Locations", len(unique_locations))
        st.metric("Total Shooting Days", total_days)
    
    with col2:
        st.write("**Locations:**")
        for loc in unique_locations[:10]:
            st.write(f"• {loc}")
    
    # Permit requirements
    permits = location_data.get('permit_requirements', [])
    if permits:
        st.write("**Permit Requirements:**")
        for permit in permits[:5]:
            st.write(f"• {permit}")
    
    # Scene locations table
    scene_locations = location_data.get('scene_locations', [])
    if scene_locations:
        st.write("**Scene Locations:**")
        df_locations = pd.DataFrame(scene_locations)
        if not df_locations.empty:
            st.dataframe(df_locations, use_container_width=True)

def display_props_breakdown(props_data):
    """Display props breakdown details"""
    if not props_data:
        st.info("No props data available")
        return
    
    master_props = props_data.get('master_props_list', [])
    budget_estimate = props_data.get('prop_budget_estimate', 'N/A')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Props", len(master_props))
        st.metric("Props Budget Category", budget_estimate)
    
    with col2:
        st.write("**Props List:**")
        for prop in master_props[:15]:
            st.write(f"• {prop}")
    
    # Props by category
    props_by_category = props_data.get('props_by_category', [])
    if props_by_category:
        st.write("**Props by Category:**")
        for category in props_by_category[:10]:
            st.write(f"• {category}")
    
    # Costume requirements
    costumes = props_data.get('costume_by_character', [])
    if costumes:
        st.write("**Costume Requirements:**")
        for costume in costumes[:10]:
            st.write(f"• {costume}")
    
    # Rental vs Purchase
    rental_info = props_data.get('rental_vs_purchase', [])
    if rental_info:
        st.write("**Rental vs Purchase Recommendations:**")
        for info in rental_info[:5]:
            st.write(f"• {info}")

# API health check and status functions
def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def show_api_status():
    """Show API connection status in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 API Status")
    
    if check_api_health():
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.sidebar.caption(f"Check if API is running at {API_BASE_URL}")

# Error handling wrapper
def safe_request(func, *args, **kwargs):
    """Wrapper for safe API requests"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please check if the API server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    main()