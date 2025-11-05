from fastapi import APIRouter, HTTPException, Path
from datetime import datetime
from app.models.schemas import PromptDetailResponse, PromptCard, PriceStats
from app.services.data_loader import get_data
from app.services.analysis import generate_card_summaries
from app.utils.helpers import calculate_percentile, is_valid_price, round_to_decimals
from app.core.logger import logger

router = APIRouter(prefix="/prompt", tags=["Prompt Detail"])

@router.get("/{prompt_id}", response_model=PromptDetailResponse)
async def get_prompt_detail(
    prompt_id: str = Path(..., description="Prompt UUID")
):
    """
    Detailed view: prompt metadata + all cards + price analysis.
    """
    try:
        df = get_data()
        
        # Get prompt data
        prompt_data = df[df['prompt_id'] == prompt_id]
        
        if len(prompt_data) == 0:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")
        
        # Sort by rank
        prompt_data = prompt_data.sort_values('rank')
        
        # Prompt metadata
        first_row = prompt_data.iloc[0]
        prompt_text = df[df['prompt_id'] == prompt_id]['Prompts'].iloc[0] if 'Prompts' in df.columns else "N/A"
        product_name = first_row['product_name']
        
        # Cards
        cards_list = []
        for _, row in prompt_data.iterrows():
            extra_list = []
            if pd.notna(row.get('extra')):
                try:
                    import ast
                    extra_list = ast.literal_eval(str(row['extra']))
                except:
                    extra_list = []
            
            cards_list.append(PromptCard(
                card_id=row['card_id'],
                product_name=row['product_name'],
                rank=int(row['rank']),
                source=row['source_normalized'],
                price=float(row['price']) if is_valid_price(row['price']) else None,
                currency=row['price_currency'] if row['price_currency'] != '-1' else None,
                delivery_days=int(row['delivery_days']) if row['delivery_days'] >= 0 else None,
                delivery_fee=float(row['delivery_fee']) if row['delivery_fee'] > 0 else None,
                extra=extra_list,
            ))
        
        # Price stats
        valid_prices = [p for p in prompt_data['price'].tolist() if is_valid_price(p)]
        
        if valid_prices:
            import pandas as pd
            price_series = pd.Series(valid_prices)
            your_price = first_row['price'] if is_valid_price(first_row['price']) else None
            your_percentile = calculate_percentile(your_price, valid_prices) if your_price else None
            
            price_stats = PriceStats(
                min_price=round_to_decimals(price_series.min()),
                max_price=round_to_decimals(price_series.max()),
                median_price=round_to_decimals(price_series.median()),
                your_price=round_to_decimals(your_price) if your_price else None,
                your_percentile=your_percentile,
            )
        else:
            price_stats = PriceStats(
                min_price=0.0,
                max_price=0.0,
                median_price=0.0,
                your_price=None,
                your_percentile=None,
            )
        
        # Metadata
        metadata = {
            "total_cards": len(cards_list),
            "unique_sources": prompt_data['source_normalized'].nunique(),
            "retrieved_at": datetime.now().isoformat(),
        }
        
        response = PromptDetailResponse(
            prompt_id=prompt_id,
            product_name=product_name,
            prompt_text=prompt_text,
            cards=cards_list,
            price_stats=price_stats,
            metadata=metadata,
        )
        
        logger.info(f"Prompt detail retrieved: {prompt_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in prompt detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))
