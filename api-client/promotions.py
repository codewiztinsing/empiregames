import requests
import json
from typing import Dict, Any, List, Optional


def get_promotions(base_url: str) -> Dict[str, Any]:
    """Get all promotions"""
    url = f"{base_url}/api/v1/promotions"
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Promotions fetched successfully"
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


def get_promotion_by_id(base_url: str, promotion_id: int) -> Dict[str, Any]:
    """Get promotion by ID"""
    url = f"{base_url}/api/v1/promotions/{promotion_id}"
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Promotion fetched successfully"
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


def create_promotion(base_url: str, title: str, description: str, type: str, value: int, 
                    value_type: str, min_deposit: Optional[int] = None, max_bonus: Optional[int] = None,
                    code: Optional[str] = None, start_date: str = None, end_date: Optional[str] = None,
                    usage_limit: Optional[int] = None, player_usage_limit: Optional[int] = None,
                    is_active: bool = True) -> Dict[str, Any]:
    """Create new promotion"""
    url = f"{base_url}/api/v1/promotions"
    payload = {
        "title": title,
        "description": description,
        "type": type,
        "value": value,
        "valueType": value_type,
        "isActive": is_active,
        "startDate": start_date,
        "endDate": end_date
    }
    
    # Add optional fields if provided
    if min_deposit is not None:
        payload["minDeposit"] = min_deposit
    if max_bonus is not None:
        payload["maxBonus"] = max_bonus
    if code is not None:
        payload["code"] = code
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date
    if usage_limit is not None:
        payload["usageLimit"] = usage_limit
    if player_usage_limit is not None:
        payload["playerUsageLimit"] = player_usage_limit

    try:
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Promotion created successfully"
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


def update_promotion(base_url: str, promotion_id: int, title: Optional[str] = None, 
                    description: Optional[str] = None, type: Optional[str] = None, 
                    value: Optional[int] = None, value_type: Optional[str] = None,
                    min_deposit: Optional[int] = None, max_bonus: Optional[int] = None,
                    code: Optional[str] = None, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, usage_limit: Optional[int] = None,
                    player_usage_limit: Optional[int] = None, is_active: Optional[bool] = None) -> Dict[str, Any]:
    """Update promotion"""
    url = f"{base_url}/api/v1/promotions/{promotion_id}"
    payload = {}
    
    # Only include fields that are provided
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if type is not None:
        payload["type"] = type
    if value is not None:
        payload["value"] = value
    if value_type is not None:
        payload["valueType"] = value_type
    if min_deposit is not None:
        payload["minDeposit"] = min_deposit
    if max_bonus is not None:
        payload["maxBonus"] = max_bonus
    if code is not None:
        payload["code"] = code
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date
    if usage_limit is not None:
        payload["usageLimit"] = usage_limit
    if player_usage_limit is not None:
        payload["playerUsageLimit"] = player_usage_limit
    if is_active is not None:
        payload["isActive"] = is_active

    try:
        response = requests.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "message": "Promotion updated successfully"
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


def delete_promotion(base_url: str, promotion_id: int) -> Dict[str, Any]:
    """Delete promotion"""
    url = f"{base_url}/api/v1/promotions/{promotion_id}"
    try:
        response = requests.delete(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json() if response.content else None,
            "message": "Promotion deleted successfully"
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
    
    # Get all promotions
    print("Getting all promotions:")
    promotions = get_promotions(base_url)
    print(promotions)
    
    # Create a new promotion
    print("\nCreating new promotion:")
    new_promotion = create_promotion(
        base_url=base_url,
        title="Welcome Bonus",
        description="100% deposit match up to $100",
        type="deposit_bonus",
        value=100,
        value_type="percentage",
        min_deposit=10,
        max_bonus=100,
        start_date="2025-08-27T00:00:00Z",
        end_date="2025-08-27T00:00:00Z"
    )
    print(new_promotion)
    
    # If creation was successful, test other operations
    if new_promotion["success"] and "data" in new_promotion:
        promotion_id = new_promotion["data"]["id"]
        
        # Get promotion by ID
        print(f"\nGetting promotion by ID {promotion_id}:")
        promotion = get_promotion_by_id(base_url, promotion_id)
        print(promotion)
        
        # Update promotion
        print(f"\nUpdating promotion {promotion_id}:")
        updated_promotion = update_promotion(
            base_url=base_url,
            promotion_id=promotion_id,
            description="Updated description: 100% deposit match up to $200",
            max_bonus=200
        )
        print(updated_promotion)
        
        # Delete promotion
        print(f"\nDeleting promotion {promotion_id}:")
        # deleted_promotion = delete_promotion(base_url, promotion_id)
        # print(deleted_promotion)
