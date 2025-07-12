# With human-in-the-loop (nodes.py/workflow.py/api.py/validators.py)

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Script Analysis Tool",
    page_icon="🎬",
    layout="wide"
)

def main():
    st.title("🎬 Script Analysis Tool")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose action:",
        ["📤 Analyze Script", "📋 View Scripts", "💬 Provide Feedback", "🔍 Script Details"]
    )
    
    # API status
    show_api_status()
    
    if page == "📤 Analyze Script":
        analyze_script_page()
    elif page == "📋 View Scripts":
        view_scripts_page()
    elif page == "💬 Provide Feedback":
        feedback_page()
    elif page == "🔍 Script Details":
        script_details_page()

def analyze_script_page():
    st.header("📤 Analyze Script")
    
    uploaded_file = st.file_uploader("Choose PDF script", type=['pdf'])
    
    if uploaded_file:
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        col1, col2 = st.columns(2)
        with col1:
            analyze_only = st.button("🔍 Analyze Only", type="primary")
        with col2:
            analyze_and_save = st.button("💾 Analyze & Save", type="secondary")
        
        if analyze_only or analyze_and_save:
            with st.spinner("Analyzing script..."):
                try:
                    # Analyze
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{API_BASE_URL}/analyze-script", files=files, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis completed!")
                        
                        # Show summary
                        display_analysis_summary(result.get('analysis_data', {}))
                        
                        # Save if requested
                        if analyze_and_save and 'save_request' in result:
                            save_response = requests.post(
                                f"{API_BASE_URL}/save-analysis",
                                json=result['save_request']
                            )
                            if save_response.status_code == 201:
                                save_result = save_response.json()
                                st.success(f"💾 Saved to database! ID: {save_result['database_id']}")
                            else:
                                st.error("❌ Save failed")
                    else:
                        st.error(f"❌ Analysis failed: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def view_scripts_page():
    st.header("📋 All Scripts")
    
    # Simple filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search filename")
    with col2:
        status_filter = st.selectbox("Status", ["All", "completed", "awaiting_human_feedback", "error"])
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    try:
        # Get scripts
        params = {"limit": 50}
        if search:
            params["search"] = search
        if status_filter != "All":
            params["status_filter"] = status_filter
            
        response = requests.get(f"{API_BASE_URL}/analyzed-scripts", params=params)
        
        if response.status_code == 200:
            result = response.json()
            scripts = result['data']
            
            st.info(f"Found {result['pagination']['total']} scripts")
            
            # Display scripts
            for script in scripts:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**📄 {script['filename']}**")
                        st.caption(f"ID: {script['id'][:8]}...")
                    
                    with col2:
                        status = script['status']
                        if status == "awaiting_human_feedback":
                            st.warning(f"⏳ {status}")
                        elif status == "completed":
                            st.success(f"✅ {status}")
                        else:
                            st.info(f"📋 {status}")
                    
                    with col3:
                        st.write(f"Scenes: {script.get('total_scenes', 'N/A')}")
                        st.write(f"Budget: ${script.get('estimated_budget', 0):,.0f}")
                    
                    with col4:
                        # View button
                        if st.button("👁️ View", key=f"view_{script['id']}"):
                            st.session_state['selected_script'] = script['id']
                            st.rerun()
                        
                        # Feedback button
                        if script['status'] == "awaiting_human_feedback":
                            if st.button("💬 Feedback", key=f"feedback_{script['id']}", type="primary"):
                                st.session_state['feedback_script'] = script['id']
                                st.rerun()
                        
                        # FIXED: Quick delete with confirmation
                        delete_key = f"delete_{script['id']}"
                        confirm_key = f"confirm_delete_{script['id']}"
                        
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False
                        
                        if not st.session_state[confirm_key]:
                            if st.button("🗑️", key=delete_key, help="Delete script"):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            if st.button("⚠️ Confirm", key=f"confirm_{script['id']}", type="secondary"):
                                try:
                                    delete_response = requests.delete(f"{API_BASE_URL}/analyzed-scripts/{script['id']}")
                                    if delete_response.status_code == 200:
                                        st.success(f"✅ Deleted {script['filename']}")
                                        st.session_state[confirm_key] = False
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Delete failed")
                                        st.session_state[confirm_key] = False
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                    st.session_state[confirm_key] = False
                    
                    st.divider()
        else:
            st.error("❌ Failed to load scripts")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def feedback_page():
    st.header("💬 Provide Human Feedback")
    
    # Check if script selected from list
    if 'feedback_script' in st.session_state:
        script_id = st.session_state['feedback_script']
        st.info(f"Providing feedback for script: {script_id[:8]}...")
    else:
        script_id = st.text_input("Enter Script ID")
    
    if script_id:
        # Get script details first
        try:
            response = requests.get(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
            if response.status_code == 200:
                script_data = response.json()['data']
                
                st.subheader(f"📄 {script_data['filename']}")
                st.write(f"**Status:** {script_data['status']}")
                
                # Quick analysis overview
                if script_data.get('script_data'):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Scenes", script_data.get('total_scenes', 0))
                    with col2:
                        st.metric("Characters", script_data.get('total_characters', 0))
                    with col3:
                        st.metric("Budget", f"${script_data.get('estimated_budget', 0):,.0f}")
                
                st.divider()
                
                # Feedback form
                st.subheader("📝 Your Feedback")
                
                col1, col2 = st.columns(2)
                with col1:
                    approved = st.radio(
                        "Analysis Quality:",
                        ["✅ Approved", "❌ Needs Revision"],
                        index=0
                    )
                
                with col2:
                    request_reanalysis = st.checkbox("🔄 Request Re-analysis")
                
                feedback_text = st.text_area(
                    "Feedback Comments:",
                    placeholder="Provide specific feedback about the analysis...",
                    height=150
                )
                
                if st.button("📤 Submit Feedback", type="primary"):
                    if feedback_text.strip():
                        try:
                            feedback_data = {
                                "feedback_text": feedback_text,
                                "approved": approved == "✅ Approved",
                                "request_reanalysis": request_reanalysis
                            }
                            
                            response = requests.post(
                                f"{API_BASE_URL}/provide-feedback/{script_id}",
                                json=feedback_data
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.success("✅ Feedback submitted successfully!")
                                st.info(f"Action taken: {result['action_taken']}")
                                st.info(f"New status: {result['status']}")
                                
                                # Clear session state
                                if 'feedback_script' in st.session_state:
                                    del st.session_state['feedback_script']
                                
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Feedback submission failed: {response.status_code}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please provide feedback text")
            else:
                st.error("❌ Script not found")
                
        except Exception as e:
            st.error(f"❌ Error loading script: {str(e)}")

def script_details_page():
    st.header("🔍 Script Details")
    
    # Check if script selected from list
    if 'selected_script' in st.session_state:
        script_id = st.session_state['selected_script']
        if st.button("← Back to List"):
            del st.session_state['selected_script']
            # Clear any delete confirmation state
            if 'confirm_delete' in st.session_state:
                del st.session_state['confirm_delete']
            st.rerun()
    else:
        script_id = st.text_input("Enter Script ID")
    
    if script_id:
        try:
            response = requests.get(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
            
            if response.status_code == 200:
                script_data = response.json()['data']
                
                # Basic info
                st.subheader("📋 Basic Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Filename:** {script_data['filename']}")
                    st.write(f"**Status:** {script_data['status']}")
                    st.write(f"**File Size:** {script_data['file_size_bytes']} bytes")
                
                with col2:
                    st.write(f"**Scenes:** {script_data.get('total_scenes', 'N/A')}")
                    st.write(f"**Budget:** ${script_data.get('estimated_budget', 0):,.2f}")
                    st.write(f"**Created:** {script_data.get('created_at', 'N/A')[:10]}")
                
                # Analysis tabs (same as before)
                if script_data.get('script_data'):
                    st.subheader("📊 Analysis Details")
                    
                    tab1, tab2, tab3 = st.tabs(["📄 Script", "💰 Costs", "📍 Locations"])
                    
                    with tab1:
                        script_info = script_data.get('script_data', {})
                        st.write(f"**Pages:** {script_info.get('total_pages', 0)}")
                        st.write(f"**Words:** {script_info.get('total_words', 0)}")
                        
                        characters = script_info.get('total_characters', [])
                        if characters:
                            st.write("**Characters:**")
                            st.write(", ".join(characters[:10]))
                    
                    with tab2:
                        cost_info = script_data.get('cost_breakdown', {})
                        if cost_info:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Budget", f"${cost_info.get('total_costs', 0):,.2f}")
                                st.metric("Cast Costs", f"${cost_info.get('total_cast_costs', 0):,.2f}")
                            with col2:
                                st.metric("Location Costs", f"${cost_info.get('total_location_costs', 0):,.2f}")
                                st.metric("Equipment Costs", f"${cost_info.get('total_equipment_costs', 0):,.2f}")
                    
                    with tab3:
                        location_info = script_data.get('location_breakdown', {})
                        if location_info:
                            locations = location_info.get('unique_locations', [])
                            st.write(f"**Total Locations:** {len(locations)}")
                            st.write(f"**Shooting Days:** {location_info.get('total_location_days', 0)}")
                            
                            if locations:
                                st.write("**Locations:**")
                                for loc in locations[:10]:
                                    st.write(f"• {loc}")
                
                # Actions - FIXED DELETE FUNCTIONALITY
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if script_data['status'] == "awaiting_human_feedback":
                        if st.button("💬 Provide Feedback", type="primary"):
                            st.session_state['feedback_script'] = script_id
                            st.rerun()
                
                with col2:
                    # FIXED: Proper delete confirmation flow
                    if 'confirm_delete' not in st.session_state:
                        st.session_state['confirm_delete'] = False
                    
                    if not st.session_state['confirm_delete']:
                        if st.button("🗑️ Delete Script", type="secondary"):
                            st.session_state['confirm_delete'] = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Are you sure?")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("✅ Yes, Delete", type="primary"):
                                try:
                                    delete_response = requests.delete(f"{API_BASE_URL}/analyzed-scripts/{script_id}")
                                    if delete_response.status_code == 200:
                                        st.success("✅ Script deleted!")
                                        # Clear session state
                                        if 'selected_script' in st.session_state:
                                            del st.session_state['selected_script']
                                        if 'confirm_delete' in st.session_state:
                                            del st.session_state['confirm_delete']
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Delete failed: {delete_response.status_code}")
                                        st.session_state['confirm_delete'] = False
                                except Exception as e:
                                    st.error(f"❌ Delete error: {str(e)}")
                                    st.session_state['confirm_delete'] = False
                        
                        with col_no:
                            if st.button("❌ Cancel"):
                                st.session_state['confirm_delete'] = False
                                st.rerun()
                
                with col3:
                    # Download as JSON
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(script_data, indent=2),
                        file_name=f"{script_data['filename']}_analysis.json",
                        mime="application/json"
                    )
                
            else:
                st.error("❌ Script not found")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def display_analysis_summary(analysis_data):
    """Display quick analysis summary"""
    if not analysis_data:
        return
    
    st.subheader("📊 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    script_data = analysis_data.get('script_data', {})
    cost_data = analysis_data.get('cost_breakdown', {})
    
    with col1:
        st.metric("Scenes", len(script_data.get('scenes', [])))
    with col2:
        st.metric("Characters", len(script_data.get('total_characters', [])))
    with col3:
        st.metric("Locations", len(script_data.get('total_locations', [])))
    with col4:
        st.metric("Budget", f"${cost_data.get('total_costs', 0):,.0f}")

def show_api_status():
    """Show API status in sidebar"""
    st.sidebar.divider()
    st.sidebar.subheader("🔌 API Status")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ Connected")
        else:
            st.sidebar.error("❌ API Error")
    except:
        st.sidebar.error("❌ Disconnected")
        st.sidebar.caption(f"Check: {API_BASE_URL}")

def get_scripts_awaiting_feedback():
    """Get scripts that need human feedback"""
    try:
        response = requests.get(f"{API_BASE_URL}/scripts-awaiting-feedback")
        if response.status_code == 200:
            return response.json()['data']
        return []
    except:
        return []

# Add feedback notification in sidebar
def show_feedback_notifications():
    """Show pending feedback notifications"""
    pending_scripts = get_scripts_awaiting_feedback()
    
    if pending_scripts:
        st.sidebar.divider()
        st.sidebar.subheader("⏳ Pending Feedback")
        st.sidebar.warning(f"{len(pending_scripts)} scripts need review")
        
        for script in pending_scripts[:3]:  # Show first 3
            if st.sidebar.button(f"📄 {script['filename'][:20]}...", key=f"pending_{script['id']}"):
                st.session_state['feedback_script'] = script['id']
                st.rerun()
        
        if len(pending_scripts) > 3:
            st.sidebar.caption(f"...and {len(pending_scripts) - 3} more")

# Update main function to include notifications
def main():
    st.title("🎬 Script Analysis Tool")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose action:",
        ["📤 Analyze Script", "📋 View Scripts", "💬 Provide Feedback", "🔍 Script Details"]
    )
    
    # API status and notifications
    show_api_status()
    show_feedback_notifications()
    
    if page == "📤 Analyze Script":
        analyze_script_page()
    elif page == "📋 View Scripts":
        view_scripts_page()
    elif page == "💬 Provide Feedback":
        feedback_page()
    elif page == "🔍 Script Details":
        script_details_page()

if __name__ == "__main__":
    main()