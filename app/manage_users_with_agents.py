#!/usr/bin/env python
"""
Script to filter and display users with agent codes
Usage: python manage_users_with_agents.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from dashboard.models import Agent
from django.db.models import Count

def filter_users_with_agents():
    """Filter and display users with agent codes"""
    print("=" * 60)
    print("USERS WITH AGENT CODES REPORT")
    print("=" * 60)
    
    # Get all users with agent codes
    users_with_agents = User.objects.filter(
        agent_code__isnull=False
    ).exclude(
        agent_code=''
    ).order_by('-created_at')
    
    total_users = User.objects.count()
    total_with_agents = users_with_agents.count()
    
    print(f"Total Users: {total_users}")
    print(f"Users with Agent Codes: {total_with_agents}")
    print(f"Conversion Rate: {(total_with_agents/total_users*100):.1f}%" if total_users > 0 else "0%")
    print()
    
    if users_with_agents.exists():
        print("USERS WITH AGENT CODES:")
        print("-" * 60)
        
        for user in users_with_agents:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Phone: {user.phone}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Agent Code: {user.agent_code}")
            print(f"Registration Date: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Active: {'Yes' if user.is_active else 'No'}")
            print("-" * 40)
    else:
        print("No users found with agent codes.")
    
    print()
    
    # Group by agent code
    agent_stats = users_with_agents.values('agent_code').annotate(
        user_count=Count('id')
    ).order_by('-user_count')
    
    if agent_stats:
        print("USERS BY AGENT CODE:")
        print("-" * 60)
        
        for stat in agent_stats:
            agent_code = stat['agent_code']
            user_count = stat['user_count']
            
            # Try to get agent details
            try:
                agent = Agent.objects.get(agent_code=agent_code)
                agent_name = agent.name
                agent_phone = agent.phone
            except Agent.DoesNotExist:
                agent_name = "Unknown Agent"
                agent_phone = "N/A"
            
            print(f"Agent Code: {agent_code}")
            print(f"Agent Name: {agent_name}")
            print(f"Agent Phone: {agent_phone}")
            print(f"Referred Users: {user_count}")
            print("-" * 40)

def filter_by_agent_code(agent_code):
    """Filter users by specific agent code"""
    print(f"=" * 60)
    print(f"USERS REFERRED BY AGENT: {agent_code}")
    print("=" * 60)
    
    users = User.objects.filter(agent_code=agent_code).order_by('-created_at')
    
    if users.exists():
        print(f"Found {users.count()} users referred by agent {agent_code}:")
        print("-" * 60)
        
        for user in users:
            print(f"Username: {user.username}")
            print(f"Phone: {user.phone}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Registration Date: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Active: {'Yes' if user.is_active else 'No'}")
            print("-" * 40)
    else:
        print(f"No users found referred by agent {agent_code}")

def get_agent_performance():
    """Get performance statistics for all agents"""
    print("=" * 60)
    print("AGENT PERFORMANCE REPORT")
    print("=" * 60)
    
    agents = Agent.objects.filter(is_active=True).order_by('-total_referrals')
    
    if agents.exists():
        for agent in agents:
            print(f"Agent: {agent.name} ({agent.agent_code})")
            print(f"Phone: {agent.phone}")
            print(f"Total Referrals: {agent.total_referrals}")
            print(f"Total Deposits Referred: {agent.total_deposits_referred} ETB")
            print(f"Total Earnings: {agent.total_earnings} ETB")
            print(f"Commission Rate: {agent.commission_rate}%")
            print(f"Telegram Link: {agent.telegram_bot_link}")
            print("-" * 40)
    else:
        print("No active agents found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--agent":
            if len(sys.argv) > 2:
                filter_by_agent_code(sys.argv[2])
            else:
                print("Please provide an agent code. Usage: python manage_users_with_agents.py --agent AGENT001")
        elif sys.argv[1] == "--performance":
            get_agent_performance()
        else:
            print("Usage:")
            print("  python manage_users_with_agents.py                    # Show all users with agent codes")
            print("  python manage_users_with_agents.py --agent AGENT001   # Show users for specific agent")
            print("  python manage_users_with_agents.py --performance      # Show agent performance")
    else:
        filter_users_with_agents()
