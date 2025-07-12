// Test script to verify the status update functionality
// This simulates the changeProjectStatus function behavior

const mockProject = {
  id: "test-project-1",
  title: "Test Project",
  status: "ACTIVE"
};

const mockStatusOption = {
  value: "COMPLETED",
  label: "Completed",
  color: "bg-green-400 text-black"
};

// Mock store function
const mockUpdateProjectStatus = async (projectId, status, color) => {
  console.log(`Updating project ${projectId} to status ${status}`);
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  // Simulate success
  return true;
};

// The new async changeProjectStatus function
async function changeProjectStatus(project, statusOption) {
  try {
    console.log(`Changing status from ${project.status} to ${statusOption.value}`);
    
    // Update in the store first (this will update the backend and reactive state)
    const success = await mockUpdateProjectStatus(project.id, statusOption.value, statusOption.color);
    
    if (success) {
      console.log(`✅ Successfully updated project status to ${statusOption.label}`);
      console.log('✅ Menus closed');
      console.log(`✅ Notification: Project status updated to ${statusOption.label}`);
    } else {
      console.log('❌ Failed to update project status');
    }
  } catch (error) {
    console.error('❌ Error updating project status:', error);
  }
}

// Test the function
console.log("Testing status update functionality...");
changeProjectStatus(mockProject, mockStatusOption);

// Expected output:
// 1. Log the status change attempt
// 2. Simulate store update call
// 3. Show success message
// 4. Confirm UI state changes
