"""
Pytest configuration and shared fixtures for StackExchange Parser tests.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config():
    """Sample table configuration for testing."""
    return {
        'tables': {
            'Posts': ['Id', 'PostTypeId', 'CreationDate', 'Score', 'Title', 'Body'],
            'Users': ['Id', 'DisplayName', 'CreationDate', 'Reputation'],
            'Comments': ['Id', 'PostId', 'UserId', 'CreationDate', 'Text']
        }
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config):
    """Create a temporary config file for testing."""
    config_path = os.path.join(temp_dir, "test_config.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def sample_xml_posts():
    """Sample Posts.xml content for testing."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<posts>
  <row Id="1" PostTypeId="1" CreationDate="2008-07-31T21:42:52.667" Score="25" 
       Title="How to use Git?" Body="&lt;p&gt;Learning Git basics&lt;/p&gt;" OwnerUserId="1" Tags="&lt;git&gt;&lt;version-control&gt;" />
  <row Id="2" PostTypeId="2" CreationDate="2008-07-31T21:43:25.983" Score="10" 
       Body="&lt;p&gt;Use git init to start&lt;/p&gt;" OwnerUserId="2" ParentId="1" />
  <row Id="3" PostTypeId="1" CreationDate="2008-07-31T22:17:57.920" Score="5" 
       Title="Python basics" Body="&lt;p&gt;Learning Python&lt;/p&gt;" OwnerUserId="1" Tags="&lt;python&gt;" />
</posts>'''


@pytest.fixture
def sample_xml_users():
    """Sample Users.xml content for testing."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<users>
  <row Id="1" DisplayName="JohnDoe" CreationDate="2008-07-31T14:22:31.317" 
       Reputation="101" Location="New York" />
  <row Id="2" DisplayName="JaneSmith" CreationDate="2008-07-31T14:25:23.113" 
       Reputation="250" Location="California" />
</users>'''


@pytest.fixture
def sample_xml_comments():
    """Sample Comments.xml content for testing."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<comments>
  <row Id="1" PostId="1" UserId="2" CreationDate="2008-07-31T22:47:23.200" 
       Text="Great question!" />
  <row Id="2" PostId="1" UserId="1" CreationDate="2008-07-31T23:15:42.567" 
       Text="Thanks for the feedback" />
</comments>'''


@pytest.fixture
def stackexchange_site_structure(temp_dir, sample_xml_posts, sample_xml_users, sample_xml_comments):
    """Create a complete StackExchange site structure for testing."""
    # Create site directories
    site_dir = os.path.join(temp_dir, "stackoverflow.com")
    meta_site_dir = os.path.join(temp_dir, "meta.stackoverflow.com")
    
    os.makedirs(site_dir)
    os.makedirs(meta_site_dir)
    
    # Create XML files for main site
    with open(os.path.join(site_dir, "Posts.xml"), 'w') as f:
        f.write(sample_xml_posts)
    with open(os.path.join(site_dir, "Users.xml"), 'w') as f:
        f.write(sample_xml_users)
    with open(os.path.join(site_dir, "Comments.xml"), 'w') as f:
        f.write(sample_xml_comments)
    
    # Create XML files for meta site (smaller dataset)
    meta_posts = '''<?xml version="1.0" encoding="utf-8"?>
<posts>
  <row Id="1" PostTypeId="1" CreationDate="2008-08-01T10:00:00.000" Score="5" 
       Title="Meta question" Body="&lt;p&gt;About the site&lt;/p&gt;" OwnerUserId="1" Tags="&lt;discussion&gt;" />
</posts>'''
    
    with open(os.path.join(meta_site_dir, "Posts.xml"), 'w') as f:
        f.write(meta_posts)
    
    return {
        'input_dir': temp_dir,
        'main_site': site_dir,
        'meta_site': meta_site_dir
    }


@pytest.fixture
def invalid_xml():
    """Invalid XML content for error testing."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<posts>
  <row Id="1" PostTypeId="1" CreationDate="2008-07-31T21:42:52.667" Score="25" 
       Title="Unclosed tag
  <row Id="2" PostTypeId="2" 
</posts>'''