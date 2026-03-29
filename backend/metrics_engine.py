import pandas as pd
import numpy as np

def compute_metrics(json_data: str, metadata_columns: dict):
    # Load the cleaned JSON back into heavily optimized Pandas Dataframe
    df = pd.read_json(json_data, orient='records')

    # Basic baseline calculations
    total_orders = int(len(df))
    total_revenue = 0.0
    aov = 0.0
    
    top_products = []
    bottom_products = []
    insights = []
    
    rev_col = metadata_columns.get('Revenue')
    prod_col = metadata_columns.get('Product')
    
    # Mathematical Aggregations Using Numpy & Pandas
    if rev_col and rev_col in df.columns:
        # Force strict numerics and coerce errors to 0 using pandas
        df[rev_col] = pd.to_numeric(df[rev_col], errors='coerce').fillna(0)
        
        # Use underlying numpy C-bindings for blazing fast sum computation
        total_revenue = float(np.sum(df[rev_col].values))
        aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
        
        # Natural Language Data Engineering
        insights.append(f"Your business processed {total_orders} orders generating ${total_revenue:,.2f} in total revenue, averaging out to ${aov:,.2f} per transaction.")
        
    if prod_col and prod_col in df.columns:
        if rev_col and rev_col in df.columns:
            # Rank products by sum of revenue
            product_group = df.groupby(prod_col)[rev_col].sum().sort_values(ascending=False).head(5)
            
            for prod_name, rev in product_group.items():
                top_products.append({"name": str(prod_name), "revenue": round(float(rev), 2)})
                
            bottom_group = df.groupby(prod_col)[rev_col].sum().sort_values(ascending=True)
            # Filter out negative or zero to only get actual slow movers? 
            # Well, sorting ascending gives the lowest revenue items. Let's just grab the lowest 5.
            for prod_name, rev in bottom_group.head(5).items():
                bottom_products.append({"name": str(prod_name), "revenue": round(float(rev), 2)})
                
            if len(top_products) > 0:
                top_1_name = top_products[0]["name"]
                top_1_rev = top_products[0]["revenue"]
                percentage = round((top_1_rev / total_revenue) * 100, 1) if total_revenue > 0 else 0
                insights.append(f"Your #1 best-selling product is '{top_1_name}' which alone generated ${top_1_rev:,.2f}. This makes up roughly {percentage}% of your entire global revenue!")
        else:
            # Fallback to counts if no price/revenue exists
            product_group = df[prod_col].value_counts().head(5)
            for prod_name, count in product_group.items():
                top_products.append({"name": str(prod_name), "revenue": 0.0, "count": int(count)})
                
            bottom_group_count = df[prod_col].value_counts().sort_values(ascending=True).head(5)
            for prod_name, count in bottom_group_count.items():
                bottom_products.append({"name": str(prod_name), "revenue": 0.0, "count": int(count)})
                
            if len(top_products) > 0:
                top_1_name = top_products[0]["name"]
                first_count = top_products[0]["count"]
                insights.append(f"Your most frequently sold product is '{top_1_name}', being naturally ordered {first_count} times.")

    if len(insights) == 0:
        insights.append(f"We successfully analyzed {total_orders} rows of perfectly cleaned data! However, we could not auto-detect price or product columns. Make sure your headers feature keywords like 'price', 'sales', or 'item'.")

    return {
        "metrics": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "aov": aov
        },
        "top_products": top_products,
        "bottom_products": bottom_products,
        "insights": insights
    }
