"""Unit tests for modular Prefect tasks."""
import unittest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import tasks to test
from prefect_poc.tasks.sources.api import fetch_users_task, fetch_posts_task
from prefect_poc.tasks.transforms.cleaning import clean_users_task, clean_posts_task, enrich_posts_task
from prefect_poc.tasks.analytics.stats import user_activity_task, top_authors_task, summary_task
from prefect_poc.tasks.exports.files import (
    export_users_task,
    export_posts_task,
    export_user_stats_task,
    export_top_authors_task,
    export_summary_task
)


class TestSourceTasks(unittest.TestCase):
    """Test source/extraction tasks."""
    
    @patch('prefect_poc.tasks.sources.api.requests.get')
    def test_fetch_users_task(self, mock_get):
        """Test fetching users from API."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Test User", "email": "test@example.com"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Run task
        result = fetch_users_task.fn()
        
        # Verify
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "Test User")
    
    @patch('prefect_poc.tasks.sources.api.requests.get')
    def test_fetch_posts_task(self, mock_get):
        """Test fetching posts from API."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "userId": 1, "title": "Test Post", "body": "Test content"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Run task
        result = fetch_posts_task.fn()
        
        # Verify
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["title"], "Test Post")


class TestTransformTasks(unittest.TestCase):
    """Test transformation tasks."""
    
    def test_clean_users_task(self):
        """Test cleaning users data."""
        # Prepare mock data
        users_raw = {
            "data": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "username": "johnd",
                    "email": "JOHN@EXAMPLE.COM",
                    "phone": "123-456-7890",
                    "website": "example.com",
                    "address": {"street": "Main St"}  # Extra field
                }
            ]
        }
        
        # Run task
        result = clean_users_task.fn(users_raw)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['email'], 'john@example.com')  # lowercase
        self.assertIn('full_name', result.columns)
        self.assertNotIn('address', result.columns)  # removed
    
    def test_clean_posts_task(self):
        """Test cleaning posts data."""
        # Prepare mock data
        posts_raw = {
            "data": [
                {
                    "id": 1,
                    "userId": 1,
                    "title": "  Test Post  ",
                    "body": "  Test content  "
                }
            ]
        }
        
        # Run task
        result = clean_posts_task.fn(posts_raw)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['title'], 'Test Post')  # stripped
        self.assertIn('title_length', result.columns)
        self.assertIn('body_length', result.columns)
    
    def test_enrich_posts_task(self):
        """Test enriching posts with user data."""
        # Prepare mock data
        posts = pd.DataFrame([
            {"id": 1, "userId": 1, "title": "Post 1", "body": "Content 1"}
        ])
        users = pd.DataFrame([
            {"id": 1, "name": "John Doe", "email": "john@example.com"}
        ])
        
        # Run task
        result = enrich_posts_task.fn(posts, users)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn('author_name', result.columns)
        self.assertIn('author_email', result.columns)
        self.assertEqual(result.iloc[0]['author_name'], 'John Doe')


class TestAnalyticsTasks(unittest.TestCase):
    """Test analytics tasks."""
    
    def test_user_activity_task(self):
        """Test calculating user activity statistics."""
        # Prepare mock data
        posts = pd.DataFrame([
            {"userId": 1, "body_length": 100},
            {"userId": 1, "body_length": 200},
            {"userId": 2, "body_length": 150}
        ])
        users = pd.DataFrame([
            {"id": 1, "name": "User 1", "email": "user1@example.com"},
            {"id": 2, "name": "User 2", "email": "user2@example.com"}
        ])
        
        # Run task
        result = user_activity_task.fn(posts, users)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('post_count', result.columns)
        self.assertIn('avg_post_length', result.columns)
        
        user1 = result[result['id'] == 1].iloc[0]
        self.assertEqual(user1['post_count'], 2)
        self.assertEqual(user1['avg_post_length'], 150.0)
    
    def test_top_authors_task(self):
        """Test identifying top authors."""
        # Prepare mock data
        user_stats = pd.DataFrame([
            {"id": 1, "name": "User 1", "post_count": 10},
            {"id": 2, "name": "User 2", "post_count": 5},
            {"id": 3, "name": "User 3", "post_count": 8}
        ])
        
        # Run task
        result = top_authors_task.fn(user_stats)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]['name'], 'User 1')  # Highest count
        self.assertEqual(result.iloc[0]['post_count'], 10)
    
    def test_summary_task(self):
        """Test generating data summary."""
        # Prepare mock data
        users = pd.DataFrame([{"id": 1}, {"id": 2}])
        posts = pd.DataFrame([
            {"id": 1, "title_length": 10, "body_length": 100},
            {"id": 2, "title_length": 20, "body_length": 200}
        ])
        posts_enriched = pd.DataFrame([{"id": 1}, {"id": 2}])
        
        # Run task
        result = summary_task.fn(users, posts, posts_enriched)
        
        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['total_users'], 2)
        self.assertEqual(result.iloc[0]['total_posts'], 2)
        self.assertEqual(result.iloc[0]['avg_posts_per_user'], 1.0)


class TestExportTasks(unittest.TestCase):
    """Test export tasks."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_export_users_task(self):
        """Test exporting users to CSV."""
        # Prepare mock data
        users = pd.DataFrame([
            {"id": 1, "name": "User 1", "email": "user1@example.com"}
        ])
        
        # Run task
        result = export_users_task.fn(users, self.temp_dir)
        
        # Verify
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith('.csv'))
        
        # Verify content
        loaded = pd.read_csv(result)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded.iloc[0]['name'], 'User 1')
    
    def test_export_posts_task(self):
        """Test exporting posts to CSV."""
        # Prepare mock data
        posts = pd.DataFrame([
            {"id": 1, "title": "Post 1", "body": "Content 1"}
        ])
        
        # Run task
        result = export_posts_task.fn(posts, self.temp_dir)
        
        # Verify
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith('.csv'))
    
    def test_export_user_stats_task(self):
        """Test exporting user stats to CSV."""
        # Prepare mock data
        stats = pd.DataFrame([
            {"id": 1, "name": "User 1", "post_count": 10}
        ])
        
        # Run task
        result = export_user_stats_task.fn(stats, self.temp_dir)
        
        # Verify
        self.assertTrue(os.path.exists(result))


if __name__ == '__main__':
    unittest.main()
