# agents/tools/compute.py
# Smart compute routing to Bittensor subnets

import bittensor as bt

def get_compute_client(tool_name: str = "chutes"):
    """Returns the best compute client based on config"""
    if tool_name == "chutes":
        # Example: Chutes private inference
        print("🔗 Using Chutes subnet for inference")
        return "chutes_client"  # Replace with real Chutes SDK call in production
    
    elif tool_name == "targon":
        print("🔒 Using Targon TEE subnet for secure compute")
        return "targon_client"
    
    elif tool_name == "celium":
        print("⚡ Using Celium subnet for heavy parallel compute")
        return "celium_client"
    
    else:
        print("⚠️ Falling back to local compute")
        return "local"
