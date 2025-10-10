"""
Contract tests for Ready for Production list filtering functionality.

Tests verify that systems with existing PROD_SETUP jobs (queued or running) 
are excluded from the Ready list to prevent duplicate production setups.
"""

import os
import json
import tempfile
import pytest
from backend.app import create_app
from backend.app.services import get_existing_prod_database_names


class TestReadyListFiltering:
    """Test filtering of Ready for Production list based on existing jobs."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with temporary directories."""
        app = create_app()
        app.config['TESTING'] = True
        
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.queue_dir = os.path.join(self.temp_dir, 'queue')
        self.running_dir = os.path.join(self.temp_dir, 'running')
        
        os.makedirs(self.queue_dir, exist_ok=True)
        os.makedirs(self.running_dir, exist_ok=True)
        
        app.config['QUEUE_FOLDER'] = self.queue_dir
        app.config['RUNNING_FOLDER'] = self.running_dir
        app.config['CONTROL_DB_CONNECTION'] = None  # Use stub data
        
        yield app
        
        # Cleanup after test
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.fixture  
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def create_prod_job_file(self, folder, database_name, filename=None):
        """Helper to create a PROD_SETUP job file in the specified folder."""
        if filename is None:
            filename = f"prod-test-{database_name}.json"
            
        payload = {
            "JobType": "PROD_SETUP",
            "DatabaseName": database_name,
            "WebServerCluster": "us-c1webx",
            "NewDatabaseServer": "us-clusdb1",
            "NewWebSiteDomain": f"prod-{database_name}.showare.net",
            "ShoWareControl": f"Test Show {database_name}",
            "Version": "1.0",
            "GeminiProjID": 1234
        }
        
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            
        return file_path

    def create_dev_job_file(self, folder, database_name, filename=None):
        """Helper to create a DEV_SETUP job file (should not affect filtering)."""
        if filename is None:
            filename = f"dev-test-{database_name}.json"
            
        payload = {
            "JobType": "DEV_SETUP",
            "DatabaseName": database_name,
            "NewShoWareControlName": f"Test Dev {database_name}",
            "NewWebSiteDomain": f"qa-{database_name}.showare.net"
        }
        
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            
        return file_path

    def test_get_existing_prod_database_names_empty_folders(self, app):
        """Test that empty folders return empty set."""
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == set()

    def test_get_existing_prod_database_names_with_queued_jobs(self, app):
        """Test detection of PROD_SETUP jobs in queue folder."""
        self.create_prod_job_file(self.queue_dir, "testdb1")
        self.create_prod_job_file(self.queue_dir, "testdb2")
        
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == {"testdb1", "testdb2"}

    def test_get_existing_prod_database_names_with_running_jobs(self, app):
        """Test detection of PROD_SETUP jobs in running folder."""
        self.create_prod_job_file(self.running_dir, "runningdb1")
        self.create_prod_job_file(self.running_dir, "runningdb2")
        
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == {"runningdb1", "runningdb2"}

    def test_get_existing_prod_database_names_mixed_folders(self, app):
        """Test detection across both queue and running folders."""
        self.create_prod_job_file(self.queue_dir, "queueddb")
        self.create_prod_job_file(self.running_dir, "runningdb")
        
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == {"queueddb", "runningdb"}

    def test_get_existing_prod_database_names_ignores_dev_jobs(self, app):
        """Test that DEV_SETUP jobs are ignored during filtering."""
        self.create_dev_job_file(self.queue_dir, "devdb")
        self.create_prod_job_file(self.queue_dir, "proddb")
        
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == {"proddb"}  # Only production job should be detected

    def test_get_existing_prod_database_names_handles_malformed_json(self, app):
        """Test that malformed JSON files are skipped gracefully."""
        # Create malformed JSON file
        malformed_path = os.path.join(self.queue_dir, "malformed.json")
        with open(malformed_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json ")
            
        # Create valid prod job
        self.create_prod_job_file(self.queue_dir, "validdb")
        
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == {"validdb"}  # Only valid job should be detected

    def test_get_existing_prod_database_names_handles_missing_database_name(self, app):
        """Test handling of PROD_SETUP jobs without DatabaseName field."""
        incomplete_payload = {
            "JobType": "PROD_SETUP",
            "WebServerCluster": "us-c1webx",
            # Missing DatabaseName
        }
        
        file_path = os.path.join(self.queue_dir, "incomplete.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(incomplete_payload, f, indent=2)
            
        result = get_existing_prod_database_names(self.queue_dir, self.running_dir)
        assert result == set()  # No database names should be detected

    def test_ready_list_filtering_integration(self, client):
        """Integration test: verify Ready list excludes systems with existing prod jobs."""
        # Create a production job for database "sampledb" (matches stub data)
        self.create_prod_job_file(self.queue_dir, "sampledb")
        
        # Get the main page
        response = client.get('/')
        
        # Should get 200 response
        assert response.status_code == 200
        
        # The response should not contain the sample system since it has an existing prod job
        response_text = response.get_data(as_text=True)
        
        # Check that the page loads but doesn't show the sample system with existing prod job
        assert "Sample Show" not in response_text or "sampledb" not in response_text

    def test_ready_list_includes_systems_without_existing_jobs(self, client):
        """Integration test: verify Ready list includes systems without existing prod jobs."""
        # Create a production job for a different database (not matching stub data)
        self.create_prod_job_file(self.queue_dir, "differentdb")
        
        # Get the main page
        response = client.get('/')
        
        # Should get 200 response
        assert response.status_code == 200
        
        # The response should contain the sample system since it doesn't have an existing prod job
        response_text = response.get_data(as_text=True)
        assert "Sample Show" in response_text

    def test_ready_list_filtering_with_running_jobs(self, client):
        """Integration test: verify filtering works for jobs in running folder."""
        # Create a production job in running folder for database "sampledb"
        self.create_prod_job_file(self.running_dir, "sampledb")
        
        # Get the main page
        response = client.get('/')
        
        # Should get 200 response
        assert response.status_code == 200
        
        # The response should not contain the sample system
        response_text = response.get_data(as_text=True)
        assert "Sample Show" not in response_text or "sampledb" not in response_text