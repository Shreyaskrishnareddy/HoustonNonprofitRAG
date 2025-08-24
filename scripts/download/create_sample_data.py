#!/usr/bin/env python3
"""
Create sample Houston nonprofit data for demonstration
"""

import json
import random
from datetime import datetime, date
from pathlib import Path

# NTEE codes and descriptions
NTEE_CODES = {
    'A20': 'Arts, Culture & Humanities - Visual Arts',
    'A23': 'Arts, Culture & Humanities - Cultural/Ethnic Awareness',
    'A25': 'Arts, Culture & Humanities - Arts Education',
    'B21': 'Education - Elementary & Secondary Schools',
    'B24': 'Education - Higher Education',
    'B25': 'Education - Graduate/Professional Schools',
    'B28': 'Education - Libraries',
    'E20': 'Health - Hospitals',
    'E21': 'Health - Community Health Centers',
    'E22': 'Health - Rehabilitation Services',
    'P20': 'Human Services - Housing & Shelter',
    'P21': 'Human Services - Youth Development',
    'P22': 'Human Services - Family Services',
    'P23': 'Human Services - Human Service Organizations',
    'P24': 'Human Services - Emergency Aid',
    'P30': 'Human Services - Children & Youth Services',
    'X20': 'Religion Related - Christian',
    'X21': 'Religion Related - Jewish',
    'X22': 'Religion Related - Islamic',
    'C30': 'Environment - Land Resources Conservation',
    'C32': 'Environment - Water Resources Conservation',
    'D20': 'Animal-Related - Animal Protection',
    'T20': 'Public/Society Benefit - Nonprofit Management',
    'T30': 'Public/Society Benefit - Military/Veterans',
    'N20': 'Recreation & Sports - Camps',
    'N21': 'Recreation & Sports - Community Recreation'
}

# Sample organization names and descriptions
SAMPLE_ORGS = [
    {
        'name': 'Houston Food Bank',
        'ntee': 'P24',
        'mission': 'To lead the fight against hunger in Southeast Texas by providing food access, advocacy, education and disaster relief.',
        'programs': 'Food distribution, mobile food pantries, BackPack Buddy Program, disaster relief, nutrition education',
        'activities': 'Operates largest food bank in Texas serving 18 counties. Partners with 1,500+ food pantries, soup kitchens, and social service agencies.',
        'revenue': 425000000,
        'expenses': 398000000,
        'assets': 95000000
    },
    {
        'name': 'Houston Museum of Natural Science',
        'ntee': 'A20',
        'mission': 'To provide educational opportunities that enhance understanding and appreciation of natural science and astronomy.',
        'programs': 'Permanent exhibitions, planetarium shows, IMAX theater, educational programs, research',
        'activities': 'Museum operations, educational outreach, scientific research, community engagement programs',
        'revenue': 45000000,
        'expenses': 42000000,
        'assets': 280000000
    },
    {
        'name': 'Houston Symphony Society',
        'ntee': 'A20',
        'mission': 'To inspire and engage the diverse communities of Houston through exceptional musical performances and educational experiences.',
        'programs': 'Classical concerts, pops concerts, community engagement, music education, youth programs',
        'activities': 'Over 170 concerts annually, educational outreach to 150,000 students, community partnerships',
        'revenue': 35000000,
        'expenses': 33000000,
        'assets': 65000000
    },
    {
        'name': 'Houston Independent School District Foundation',
        'ntee': 'B21',
        'mission': 'To mobilize business and community support for Houston ISD students and schools.',
        'programs': 'College scholarships, teacher grants, school improvement projects, student support services',
        'activities': 'Fundraising for educational initiatives, scholarship distribution, community partnerships',
        'revenue': 12000000,
        'expenses': 11500000,
        'assets': 25000000
    },
    {
        'name': 'Memorial Hermann Foundation',
        'ntee': 'E20',
        'mission': 'To support Memorial Hermann Health System in delivering exceptional healthcare to Southeast Texas.',
        'programs': 'Healthcare facility improvements, medical equipment, patient care programs, community health',
        'activities': 'Hospital support, medical research funding, community health initiatives, patient assistance',
        'revenue': 85000000,
        'expenses': 78000000,
        'assets': 145000000
    },
    {
        'name': 'Boys & Girls Clubs of Greater Houston',
        'ntee': 'P21',
        'mission': 'To enable all young people to reach their full potential as productive, caring, responsible citizens.',
        'programs': 'After-school programs, summer camps, character development, academic support, sports',
        'activities': 'Operates 50+ club sites serving 34,000 youth annually throughout Greater Houston',
        'revenue': 28000000,
        'expenses': 26500000,
        'assets': 45000000
    },
    {
        'name': 'United Way of Greater Houston',
        'ntee': 'P23',
        'mission': 'To improve lives by mobilizing the caring power of our community.',
        'programs': 'Community investments, disaster relief, volunteer mobilization, nonprofit capacity building',
        'activities': 'Annual fundraising campaign, strategic grantmaking, community collaboration, volunteer coordination',
        'revenue': 75000000,
        'expenses': 72000000,
        'assets': 125000000
    },
    {
        'name': 'Houston Zoo',
        'ntee': 'D20',
        'mission': 'To provide leadership in the conservation of wildlife and the preservation of natural habitats.',
        'programs': 'Animal conservation, education programs, research, habitat preservation, visitor experiences',
        'activities': 'Zoo operations, conservation projects, educational outreach, research partnerships',
        'revenue': 65000000,
        'expenses': 62000000,
        'assets': 180000000
    },
    {
        'name': 'Houston Public Library Foundation',
        'ntee': 'B28',
        'mission': 'To ensure all residents have access to library services and programs that enrich their lives.',
        'programs': 'Digital literacy, early childhood programs, adult education, community programs, collections',
        'activities': 'Library support, program funding, technology initiatives, literacy programs',
        'revenue': 8500000,
        'expenses': 8000000,
        'assets': 15000000
    },
    {
        'name': 'Houston Methodist Hospital Foundation',
        'ntee': 'E20',
        'mission': 'To advance medical research, education, and patient care at Houston Methodist Hospital.',
        'programs': 'Medical research, physician education, patient care improvements, facility enhancements',
        'activities': 'Research funding, medical education support, hospital facility improvements, patient services',
        'revenue': 125000000,
        'expenses': 115000000,
        'assets': 285000000
    },
    {
        'name': 'Star of Hope Mission',
        'ntee': 'P20',
        'mission': 'To provide Christ-centered services to homeless and disadvantaged individuals and families.',
        'programs': 'Emergency shelter, transitional housing, addiction recovery, job training, family services',
        'activities': 'Operates multiple shelters and recovery centers serving over 60,000 people annually',
        'revenue': 18000000,
        'expenses': 17200000,
        'assets': 35000000
    },
    {
        'name': 'Harris County Public Library Foundation',
        'ntee': 'B28',
        'mission': 'To enhance library services and programs for Harris County residents.',
        'programs': 'Digital resources, community programs, literacy initiatives, technology access',
        'activities': 'Library system support, program funding, technology upgrades, community outreach',
        'revenue': 3500000,
        'expenses': 3200000,
        'assets': 8000000
    }
]

def generate_houston_address():
    """Generate realistic Houston addresses"""
    streets = [
        'Main St', 'Richmond Ave', 'Westheimer Rd', 'Kirby Dr', 'Memorial Dr',
        'Washington Ave', 'Fannin St', 'Montrose Blvd', 'Shepherd Dr', 'Heights Blvd',
        'Buffalo Speedway', 'Post Oak Blvd', 'Bellaire Blvd', 'Bissonnet St'
    ]
    
    return {
        'street_address': f"{random.randint(100, 9999)} {random.choice(streets)}",
        'city': 'Houston',
        'state': 'TX',
        'zip_code': f"770{random.randint(10, 99)}"
    }

def generate_additional_orgs(count=50):
    """Generate additional random organizations"""
    org_types = [
        ('Community Health Center', 'E21', 'To provide accessible healthcare services to underserved communities.'),
        ('Youth Development Center', 'P21', 'To provide safe spaces and programs for youth development.'),
        ('Arts Education Foundation', 'A25', 'To promote arts education in schools and communities.'),
        ('Environmental Conservation Group', 'C30', 'To protect and preserve local environmental resources.'),
        ('Senior Services Organization', 'P22', 'To provide support services for elderly community members.'),
        ('Cultural Heritage Center', 'A23', 'To preserve and celebrate cultural heritage and traditions.'),
        ('Community Recreation Center', 'N21', 'To provide recreational opportunities for all community members.'),
        ('Food Pantry', 'P24', 'To provide emergency food assistance to families in need.'),
        ('Literacy Program', 'B25', 'To improve literacy rates through education and support programs.'),
        ('Housing Assistance Organization', 'P20', 'To provide housing support and services to those in need.')
    ]
    
    additional_orgs = []
    for i in range(count):
        org_type, ntee, mission = random.choice(org_types)
        name = f"Houston {org_type} #{i+1}"
        
        # Generate realistic financial data
        revenue = random.randint(500000, 15000000)
        expenses = int(revenue * random.uniform(0.85, 0.95))
        assets = int(revenue * random.uniform(0.5, 2.5))
        
        org = {
            'name': name,
            'ntee': ntee,
            'mission': mission,
            'programs': f'{org_type} programs and services for the Houston community.',
            'activities': f'Community outreach, direct services, partnerships with local organizations.',
            'revenue': revenue,
            'expenses': expenses,
            'assets': assets
        }
        additional_orgs.append(org)
    
    return additional_orgs

def create_sample_data():
    """Create comprehensive sample data"""
    
    # Combine sample orgs with generated ones
    all_orgs = SAMPLE_ORGS + generate_additional_orgs(50)
    
    nonprofits_data = []
    
    for i, org in enumerate(all_orgs):
        # Generate EIN
        ein = f"74{random.randint(1000000, 9999999)}"
        
        # Generate address
        address = generate_houston_address()
        
        # Create nonprofit record
        nonprofit = {
            'ein': ein,
            'name': org['name'],
            'ntee_code': org['ntee'],
            'ntee_description': NTEE_CODES.get(org['ntee'], 'Other'),
            'mission_description': org['mission'],
            'program_description': org['programs'],
            'activities_description': org['activities'],
            'street_address': address['street_address'],
            'city': address['city'],
            'state': address['state'],
            'zip_code': address['zip_code'],
            'total_revenue': org['revenue'],
            'total_expenses': org['expenses'],
            'net_assets': org['assets'],
            'tax_year': 2023,
            'filing_type': '990',
            'website': f"https://www.{org['name'].lower().replace(' ', '').replace('&', 'and')}.org",
            'object_id': f"202340{random.randint(100000000, 999999999)}"
        }
        
        nonprofits_data.append(nonprofit)
    
    # Save to processed data directory
    output_dir = Path("/home/great/houston-nonprofit-rag/data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "houston_nonprofits_sample.json"
    with open(output_file, 'w') as f:
        json.dump(nonprofits_data, f, indent=2)
    
    print(f"Created sample data with {len(nonprofits_data)} Houston nonprofits")
    print(f"Saved to: {output_file}")
    
    # Create summary statistics
    total_revenue = sum(org['total_revenue'] for org in nonprofits_data)
    total_expenses = sum(org['total_expenses'] for org in nonprofits_data)
    total_assets = sum(org['net_assets'] for org in nonprofits_data)
    
    ntee_counts = {}
    for org in nonprofits_data:
        ntee = org['ntee_code']
        ntee_counts[ntee] = ntee_counts.get(ntee, 0) + 1
    
    summary = {
        'total_organizations': len(nonprofits_data),
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_assets': total_assets,
        'ntee_distribution': ntee_counts,
        'generated_at': datetime.now().isoformat()
    }
    
    summary_file = output_dir / "houston_nonprofits_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary statistics saved to: {summary_file}")
    
    return nonprofits_data

if __name__ == "__main__":
    create_sample_data()