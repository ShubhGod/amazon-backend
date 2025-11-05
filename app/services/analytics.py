import pandas as pd
from app.core.logger import logger

# EXCEL_PATH = "/home/mohit/Desktop/asvaai/amazon/backend/data/prod_source_scores_normalized.xlsx"
EXCEL_PATH = "./data/prod_source_scores_normalized.xlsx"


def get_category_winners():
    try:
        df = pd.read_excel(EXCEL_PATH)
        logger.info(f"Loaded Excel data with {len(df)} rows")
        
        # Drop rows with missing critical columns
        df = df.dropna(subset=["Product", "source_normalized", "score_norm"])
        
        # Compute rank of marketplaces by normalized score within each product category (1 = highest)
        df["rank"] = df.groupby("Product")["score_norm"].rank(method="dense", ascending=False)
        
        # Aggregate normalized scores per marketplace for overall "top 10" selection
        marketplace_totals = (
            df.groupby("source_normalized")["score_norm"].sum().reset_index().sort_values("score_norm", ascending=False)
        )
        top_10_marketplaces = marketplace_totals.head(10)["source_normalized"].tolist()
        
        # Filter df to keep only rows for top 10 marketplaces
        df = df[df["source_normalized"].isin(top_10_marketplaces)].copy()
        
        # Flags for heatmap
        df["is_rank1"] = df["rank"] == 1
        df["is_amazon"] = df["source_normalized"].str.lower() == "amazon"
        
        heatmap = df[["Product", "source_normalized", "score_norm", "rank", "is_rank1", "is_amazon"]]
        
        return {
            "heatmap": heatmap.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Error processing analytics excel: {e}")
        raise e


def get_marketplace_score_sum(product: str):
    try:
        df = pd.read_excel(EXCEL_PATH)
        logger.info(f"Loaded Excel data with {len(df)} rows")

        # Filter rows for the given product category
        product_df = df[df["Product"] == product].dropna(subset=["source_normalized", "score_sum"])

        # Aggregate score_sum by marketplace
        agg = product_df.groupby("source_normalized")["score_sum"].sum().reset_index()

        # Sort descending by score_sum
        sorted_agg = agg.sort_values("score_sum", ascending=False)

        # Mark if marketplace is amazon
        sorted_agg["is_amazon"] = sorted_agg["source_normalized"].str.lower() == "amazon"

        # Prepare JSON friendly data
        return sorted_agg.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error loading marketplace score sums for product '{product}': {e}")
        raise e
