import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SUPPORT_VOTE_TYPE = 1
OPPOSE_VOTE_TYPE = 2

LEGISLATORS_CSV = "legislators.csv"
BILLS_CSV = "bills.csv"
VOTES_CSV = "votes.csv"
VOTE_RESULTS_CSV = "vote_results.csv"

class DataProcessor:
    """Main data processor using efficient pandas operations."""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "output"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _load_csv(self, filename: str) -> pd.DataFrame:
        return pd.read_csv(f"{self.data_dir}/{filename}")
    
    def _add_vote_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['is_support'] = (df['vote_type'] == SUPPORT_VOTE_TYPE).astype(int)
        df['is_oppose'] = (df['vote_type'] == OPPOSE_VOTE_TYPE).astype(int)
        return df
    
    def _write_output(self, df: pd.DataFrame, filename: str) -> str:
        output_path = f"{self.output_dir}/{filename}"
        df.to_csv(output_path, index=False)
        logger.info(f"Generated {output_path} with {len(df)} records")
        return output_path
    
    def generate_legislators_support_oppose_count(self) -> str:
        """
        Generate legislators-support-oppose-count.csv using pandas operations.
        Analyzes voting patterns and counts support/oppose votes for each legislator.
        
        Assumes vote_type 1 = Support, vote_type 2 = Oppose
        """
        legislators_df = self._load_csv(LEGISLATORS_CSV)
        vote_results_df = self._load_csv(VOTE_RESULTS_CSV)
        
        legislator_votes = vote_results_df.merge(
            legislators_df, 
            left_on='legislator_id', 
            right_on='id', 
            how='inner'
        )
        
        legislator_votes = self._add_vote_indicators(legislator_votes)
        
        result_df = legislator_votes.groupby(['legislator_id', 'name']).agg({
            'is_support': 'sum',
            'is_oppose': 'sum'
        }).reset_index()
        
        result_df = result_df.rename(columns={
            'legislator_id': 'id',
            'is_support': 'num_supported_bills',
            'is_oppose': 'num_opposed_bills'
        })
        
        return self._write_output(result_df, "legislators-support-oppose-count.csv")
    
    def generate_bills_csv(self) -> str:
        """
        Generate bills.csv using pandas operations.
        Adds supporter_count and opposer_count to each bill.
        """
        legislators_df = self._load_csv(LEGISLATORS_CSV)
        bills_df = self._load_csv(BILLS_CSV)
        votes_df = self._load_csv(VOTES_CSV)
        vote_results_df = self._load_csv(VOTE_RESULTS_CSV)
        
        vote_chain = (vote_results_df
                     .merge(votes_df, left_on='vote_id', right_on='id', how='inner')
                     .merge(bills_df, left_on='bill_id', right_on='id', how='inner'))
        
        vote_chain = self._add_vote_indicators(vote_chain)
        
        bill_stats = vote_chain.groupby(['bill_id', 'title', 'sponsor_id']).agg({
            'is_support': 'sum',
            'is_oppose': 'sum'
        }).reset_index()
        
        result_df = bill_stats.merge(
            legislators_df,
            left_on='sponsor_id',
            right_on='id',
            how='left'
        )
        
        result_df['name'] = result_df['name'].fillna('Unknown')
        
        result_df = result_df[[
            'bill_id', 'title', 'name', 'is_support', 'is_oppose'
        ]].rename(columns={
            'bill_id': 'id',
            'name': 'primary_sponsor',
            'is_support': 'supporter_count',
            'is_oppose': 'opposer_count'
        })
        
        return self._write_output(result_df, "bills.csv")
