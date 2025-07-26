#!/usr/bin/env python3
"""
Helper script to create a sample Excel file with team data for testing.
"""

import pandas as pd
from config import TEAM_NAME_COLUMN, LEADER_EMAIL_COLUMN

def create_sample_excel():
    """Create a sample Excel file with team data."""
    
    # Sample data
    sample_data = {
        TEAM_NAME_COLUMN: [
            "Team Alpha",
            "Team Beta", 
            "Team Gamma",
            "Team Delta",
            "Team Epsilon"
        ],
        LEADER_EMAIL_COLUMN: [
            "alpha.leader@example.com",
            "beta.leader@example.com",
            "gamma.leader@example.com", 
            "delta.leader@example.com",
            "epsilon.leader@example.com"
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to Excel
    excel_file = "teams_data.xlsx"
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Created sample Excel file: {excel_file}")
    print(f"📊 Contains {len(df)} teams")
    print("\nSample data:")
    print(df.to_string(index=False))
    print(f"\n📝 Please update the email addresses with real GitHub user emails before running the main script.")

if __name__ == "__main__":
    create_sample_excel() 