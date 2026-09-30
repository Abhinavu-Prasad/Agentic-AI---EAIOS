import pandas as pd
from sqlalchemy import create_engine
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.rag_agent import add_document

# Update these credentials to match your local PostgreSQL setup
DB_USER = "postgres"
DB_PASS = "Abhi" # Change if your password is different
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eaios" # Ensure you have created a database named 'eaios' in pgAdmin

def load_relational_data():
    """Transforms and loads M5 Forecasting CSVs into PostgreSQL."""
    print("Connecting to PostgreSQL...")
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    print("Loading calendar.csv...")
    df_calendar = pd.read_csv("data/calendar.csv")
    df_calendar.to_sql("calendar", engine, if_exists="replace", index=False)
    
    print("Loading sales_train_evaluation.csv (1500 row sample)...")
    # We load 1500 rows. Once melted, this generates ~2.91 million rows.
    df_sales_wide = pd.read_csv("data/sales_train_evaluation.csv", nrows=1500)
    
    print("Normalizing Wide Data (1947 columns) into Long Data...")
    df_sales_long = df_sales_wide.melt(
        id_vars=['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'],
        var_name='d',
        value_name='sales_volume'
    )
    
    print(f"Writing {len(df_sales_long):,} optimized rows to PostgreSQL (this will take a few minutes)...")
    # chunksize prevents Pandas from attempting to load all 2.9 million rows into memory at once
    df_sales_long.to_sql("sales", engine, if_exists="replace", index=False, chunksize=50000)
    print("Relational data successfully loaded into PostgreSQL.")

def load_synthetic_knowledge():
    """Generates and loads synthetic corporate policies into Qdrant."""
    print("\nGenerating synthetic corporate knowledge...")
    
    synthetic_docs = [
        {"title": "Store Management Roster", "text": "Store CA_1 is managed by Sarah Jenkins. Store CA_2 is managed by David Chen. Store WI_1 is managed by Robert Oppenheimer."},
        {"title": "Return Policy - Hobbies", "text": "Items in the 'Hobbies' category have a strict 14-day return window. Opened hobby kits are subject to a 15% restocking fee."},
        {"title": "Holiday Pay Structure", "text": "During major sporting events listed in the calendar (e.g., SuperBowl, NBA Finals), floor staff receive a 1.5x holiday pay multiplier."}
    ]
    
    for doc in synthetic_docs:
        add_document(doc["text"], {"doc_type": "policy", "title": doc["title"]})
        
    print("Synthetic knowledge successfully embedded into Qdrant.")

if __name__ == "__main__":
    print("Starting Enterprise Data Setup...")
    #load_relational_data()
    load_synthetic_knowledge()
    print("\nSetup Complete. System is ready for execution.")