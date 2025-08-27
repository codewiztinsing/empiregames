import requests
import json
from typing import Dict, Any, Optional

def get_dashboard_stats(base_url: str) -> Dict[str, Any]:
    """Get dashboard statistics"""
    url = f"{base_url}/api/v1/dashboard/stats"
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Dashboard stats fetched successfully"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}",
            "status_code": None
        }

def get_dashboard_recent_stats(base_url: str, time_range: str = "last30days") -> Dict[str, Any]:
    """Get dashboard recent statistics with time range filter"""
    url = f"{base_url}/api/v1/dashboard/stats/recent"
    params = {"timeRange": time_range}
    try:
        response = requests.get(url, params=params, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Dashboard recent stats fetched successfully"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}",
            "status_code": None
        }

if __name__ == "__main__":
    # Example usage
    base_url = "http://localhost:5000"
    
    # Get all dashboard stats
    print("Getting dashboard stats:")
    stats = get_dashboard_stats(base_url)
    print(stats)
    
    # Get recent stats for different time ranges
    time_ranges = ["today", "last7days", "last30days"]
    
    for time_range in time_ranges:
        print(f"\nGetting dashboard recent stats for {time_range}:")
        recent_stats = get_dashboard_recent_stats(base_url, time_range)
        print(recent_stats)
