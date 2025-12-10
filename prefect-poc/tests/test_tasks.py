"""Unit tests for Prefect tasks using unittest."""
import unittest
from unittest.mock import Mock, patch
import pandas as pd
import os

from prefect_poc.tasks import (
    fetch_data_from_api,
    transform_data,
    save_to_csv,
    generate_summary
)


class TestFetchDataFromAPI(unittest.TestCase):
    """Test cases for fetch_data_from_api task."""
    
    @patch('prefect_poc.tasks.requests.get')
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetching from API."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "John Doe"},
            {"id": 2, "name": "Jane Smith"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Execute - call the underlying function directly
        result = fetch_data_from_api.fn()
        
        # Assert
        self.assertIn("data", result)
        self.assertIn("source", result)
        self.assertEqual(len(result["data"]), 2)
        self.assertIn("jsonplaceholder", result["source"])
        
    @patch('prefect_poc.tasks.requests.get')
    def test_fetch_data_api_error(self, mock_get):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception):
            fetch_data_from_api.fn()


class TestTransformData(unittest.TestCase):
    """Test cases for transform_data task."""
    
    def test_transform_data_success(self):
        """Test successful data transformation."""
        # Mock input
        raw_data = {
            "data": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "username": "johndoe",
                    "email": "john@example.com",
                    "address": {"city": "New York"},
                    "company": {"name": "Acme Corp"}
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "username": "janesmith",
                    "email": "jane@example.com",
                    "address": {"city": "Los Angeles"},
                    "company": {"name": "Tech Inc"}
                }
            ],
            "source": "test"
        }
        
        # Execute - call the underlying function directly
        result = transform_data.fn(raw_data)
        
        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("id", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("email", result.columns)
        self.assertIn("city", result.columns)
        self.assertIn("company", result.columns)
        self.assertEqual(result.iloc[0]["name"], "John Doe")
        self.assertEqual(result.iloc[1]["city"], "Los Angeles")
    
    def test_transform_empty_data(self):
        """Test transformation with empty data."""
        raw_data = {"data": [], "source": "test"}
        result = transform_data.fn(raw_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)


class TestSaveToCSV(unittest.TestCase):
    """Test cases for save_to_csv task."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_df = pd.DataFrame({
            "id": [1, 2],
            "name": ["John", "Jane"],
            "email": ["john@example.com", "jane@example.com"]
        })
        
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists("output/prefect_users.csv"):
            os.remove("output/prefect_users.csv")
        if os.path.exists("output") and not os.listdir("output"):
            os.rmdir("output")
    
    def test_save_to_csv_success(self):
        """Test successful CSV file creation."""
        result = save_to_csv.fn(self.test_df)
        
        # Assert
        self.assertTrue(os.path.exists(result))
        self.assertEqual(result, "output/prefect_users.csv")
        
        # Verify content
        saved_df = pd.read_csv(result)
        self.assertEqual(len(saved_df), 2)
        self.assertEqual(list(saved_df.columns), ["id", "name", "email"])


class TestGenerateSummary(unittest.TestCase):
    """Test cases for generate_summary task."""
    
    def test_generate_summary(self):
        """Test summary generation."""
        test_df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"]
        })
        
        result = generate_summary.fn(test_df, "test_output.csv")
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_records"], 3)
        self.assertIn("id", result["columns"])
        self.assertIn("name", result["columns"])
        self.assertEqual(result["output_file"], "test_output.csv")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline."""
    
    @patch('prefect_poc.tasks.requests.get')
    def test_full_pipeline_flow(self, mock_get):
        """Test complete data extraction flow."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "name": "Test User",
                "username": "testuser",
                "email": "test@example.com",
                "address": {"city": "Test City"},
                "company": {"name": "Test Company"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Step 1: Fetch
        raw_data = fetch_data_from_api.fn()
        self.assertIn("data", raw_data)
        
        # Step 2: Transform
        df = transform_data.fn(raw_data)
        self.assertEqual(len(df), 1)
        
        # Step 3: Save
        file_path = save_to_csv.fn(df)
        self.assertTrue(os.path.exists(file_path))
        
        # Step 4: Summary
        summary = generate_summary.fn(df, file_path)
        self.assertEqual(summary["total_records"], 1)
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("output") and not os.listdir("output"):
            os.rmdir("output")


if __name__ == '__main__':
    unittest.main()
