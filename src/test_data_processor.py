import pytest
import pandas as pd
from unittest.mock import patch
import os
import tempfile
import shutil

from data_processor import DataProcessor, LEGISLATORS_CSV


class TestDataProcessor:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        self.processor = DataProcessor(data_dir=self.temp_dir, output_dir=self.output_dir)
        
        # Sample data for testing
        self.sample_legislators = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Rep. Jair', 'Rep. Jane Doe', 'Rep. John Doe']
        })
        
        self.sample_bills = pd.DataFrame({
            'id': [100, 101],
            'title': ['Test Bill 1', 'Test Bill 2'],
            'sponsor_id': [1, 2]
        })
        
        self.sample_votes = pd.DataFrame({
            'id': [200, 201],
            'bill_id': [100, 101]
        })
        
        self.sample_vote_results = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6],
            'legislator_id': [1, 2, 1, 3, 2, 3],
            'vote_id': [200, 200, 201, 201, 201, 200],
            'vote_type': [1, 2, 2, 1, 1, 2]
        })
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.output_dir)
    
    def test_init(self):
        """Test DataProcessor initialization"""
        assert self.processor.data_dir == self.temp_dir
        assert self.processor.output_dir == self.output_dir
        assert os.path.exists(self.output_dir)
    
    @patch('pandas.read_csv')
    def test_load_csv(self, mock_read_csv):
        """Test _load_csv method"""
        mock_read_csv.return_value = self.sample_legislators
        
        result = self.processor._load_csv(LEGISLATORS_CSV)
        
        mock_read_csv.assert_called_once_with(f"{self.temp_dir}/{LEGISLATORS_CSV}")
        pd.testing.assert_frame_equal(result, self.sample_legislators)
    
    def test_add_vote_indicators(self):
        """Test _add_vote_indicators method"""
        test_df = pd.DataFrame({
            'id': [1, 2, 3],
            'vote_type': [1, 2, 1]
        })
        
        result = self.processor._add_vote_indicators(test_df)
        
        expected_df = pd.DataFrame({
            'id': [1, 2, 3],
            'vote_type': [1, 2, 1],
            'is_support': [1, 0, 1],
            'is_oppose': [0, 1, 0]
        })
        
        pd.testing.assert_frame_equal(result, expected_df)
    
    def test_write_output(self):
        """Test _write_output method"""
        test_df = pd.DataFrame({
            'id': [1, 2],
            'name': ['Test1', 'Test2']
        })
        
        result_path = self.processor._write_output(test_df, "test_output.csv")
        
        expected_path = f"{self.output_dir}/test_output.csv"
        assert result_path == expected_path
        assert os.path.exists(expected_path)
        
        written_df = pd.read_csv(expected_path)
        pd.testing.assert_frame_equal(written_df, test_df)
    
    @patch.object(DataProcessor, '_load_csv')
    def test_generate_legislators_support_oppose_count(self, mock_load_csv):
        """Test generate_legislators_support_oppose_count method"""
        mock_load_csv.side_effect = [
            self.sample_legislators,
            self.sample_vote_results
        ]
        
        result_path = self.processor.generate_legislators_support_oppose_count()
        
        assert os.path.exists(result_path)
        
        result_df = pd.read_csv(result_path)
        expected_columns = ['id', 'name', 'num_supported_bills', 'num_opposed_bills']
        assert list(result_df.columns) == expected_columns
        
        assert len(result_df) == 3
        assert result_df[result_df['id'] == 1]['num_supported_bills'].iloc[0] == 1
        assert result_df[result_df['id'] == 1]['num_opposed_bills'].iloc[0] == 1
    
    @patch.object(DataProcessor, '_load_csv')
    def test_generate_bills_csv(self, mock_load_csv):
        """Test generate_bills_csv method"""
        mock_load_csv.side_effect = [
            self.sample_legislators,
            self.sample_bills,
            self.sample_votes,
            self.sample_vote_results
        ]
        
        result_path = self.processor.generate_bills_csv()
        
        assert os.path.exists(result_path)
        
        result_df = pd.read_csv(result_path)
        expected_columns = ['id', 'title', 'primary_sponsor', 'supporter_count', 'opposer_count']
        assert list(result_df.columns) == expected_columns
        
        assert len(result_df) == 2
        assert result_df[result_df['id'] == 100]['supporter_count'].iloc[0] == 1
        assert result_df[result_df['id'] == 100]['opposer_count'].iloc[0] == 2
    
    @patch.object(DataProcessor, '_load_csv')
    def test_generate_bills_csv_with_unknown_sponsor(self, mock_load_csv):
        """Test generate_bills_csv handles unknown sponsors"""
        bills_unknown_sponsor = pd.DataFrame({
            'id': [100],
            'title': ['Test Bill'],
            'sponsor_id': [999]
        })
        
        votes_data = pd.DataFrame({
            'id': [200],
            'bill_id': [100]
        })
        
        vote_results_data = pd.DataFrame({
            'id': [1],
            'legislator_id': [1],
            'vote_id': [200],
            'vote_type': [1]
        })
        
        mock_load_csv.side_effect = [
            self.sample_legislators,
            bills_unknown_sponsor,
            votes_data,
            vote_results_data
        ]
        
        result_path = self.processor.generate_bills_csv()
        result_df = pd.read_csv(result_path)

        assert result_df['primary_sponsor'].iloc[0] == 'Unknown'
    
    def test_add_vote_indicators_with_empty_dataframe(self):
        """Test _add_vote_indicators with empty DataFrame"""
        empty_df = pd.DataFrame(columns=['vote_type'])
        result = self.processor._add_vote_indicators(empty_df)
        
        expected_columns = ['vote_type', 'is_support', 'is_oppose']
        assert list(result.columns) == expected_columns
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 