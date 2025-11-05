
## Dashboard Visualizations & Metrics to Display

Based on your data structure (Product, Prompts, Rankings, Sources, Prices, Delivery) and the detailed spec you provided, here's what to show:

## **A. Home/Executive Dashboard (KPI Tiles)**

**Primary KPIs (as tiles with sparklines):**

1. **G-SoV (Generative Share of Voice)** - Overall and per platform (ChatGPT/Perplexity/Copilot)
   * Formula: `(# prompts where source appears at rank 1 or in results) / total prompts`
   * Show: Current value, trend arrow, 7-day/30-day comparison
2. **Average Rank Position** - By marketplace
   * Calculate: Mean rank for each source_normalized
   * Visualize: Horizontal bar chart showing Amazon vs competitors
3. **Rank Presence Score (0-10)** - Weighted visibility
   * 10 if rank=1, 7 if rank 2-3, 4 if mentioned inline, 0 otherwise
   * Show: Gauge chart with target threshold
4. **Price Competitiveness Rate** - % of times you have best price
   * Calculate: `COUNT(price <= MIN(price) per prompt_id) / total appearances`
   * Badge: "Price leader" if >70%
5. **Delivery Strength Score** - Average delivery performance
   * Bucket: 0-1 day=Strong (1.0), 2-3=Medium (0.7), 4-7=Weak (0.3)
   * Show: Stacked bar by delivery time ranges
6. **Prompt Coverage** - % of prompts where you appear
   * `Unique prompt_ids with your source / Total unique prompt_ids`

**Trend Visualizations:**

* **Line chart** : G-SoV over last 30 days (if you have timestamps)
* **Loss Reasons Bar** : Top 5 factors causing rank loss (price, delivery, missing data)

## **B. Explore/Drilldown View**

**Left Sidebar Filters:**

* Platform (from prompt metadata if available)
* Product category (using your Product column)
* Source/Marketplace (source_normalized)
* Date range
* Rank range (1-5)

**Main Visualizations:**

1. **Heatmap: Product × Source with Avg NRS**
   * Rows: Product categories (12 categories from your data)
   * Columns: Sources (Amazon, Flipkart, etc.)
   * Color intensity: Normalized Rank Score `(max_rank + 1 - rank) / max_rank * 10`
   * Tooltip: Show product_name, rank, price, delivery_days
2. **Table: Product Performance**
   * Columns: Product | G-SoV | Avg Rank | # Prompts | Price vs Best Competitor | Delivery Gap
   * Sortable, filterable, with CSV export
   * Color coding: Green if rank ≤2, Yellow if rank 3, Red if rank >3
3. **Scatter Plot: Price vs Rank**
   * X-axis: Price, Y-axis: Rank (inverted)
   * Bubble size: Delivery days
   * Color: Source
   * Shows price-rank correlation

## **C. Prompt Detail View**

**When clicking a prompt from Explore:**

1. **Prompt Metadata Card**
   * Prompt text (from Prompts column)
   * Product category
   * Run timestamp (if you add this)
2. **Ranked Results Cards**
   * Display each card_id with:
     * Rank badge
     * Product name
     * Source logo/name
     * Price (with currency)
     * Delivery fee & days
     * Extra info parsed from the 'extra' column
   * Visual: Vertical list, ranked 1→5
3. **Why Text Analysis (if you add this entity)**
   * Parse citations and justifications
   * Highlight when your source is mentioned
   * Sentiment snippets

## **D. Competitive Comparison View**

**Amazon vs Best Competitor Side-by-Side:**

1. **Comparison Table**
   * Price, Delivery Days, Delivery Fee
   * Appears in Results (Yes/No)
   * Average Rank
   * Frequency (# times appeared)
2. **Win/Lose Factor Chips**
   * Green chip: "Better Price (-12%)"
   * Red chip: "Slower Delivery (+3 days)"
   * Neutral: "Same availability"
3. **Head-to-Head Bar Chart**
   * Metrics: Price, Delivery, Rank, Frequency
   * Normalized 0-10 scale for comparison

## **E. Analytical Metrics (Combined Parameters)**

**1. Composite Rank Driver Score:**

<pre class="not-prose w-full rounded font-mono text-sm font-extralight"><div class="codeWrapper text-light selection:text-super selection:bg-super/10 my-md relative flex flex-col rounded font-mono text-sm font-normal bg-subtler"><div class="translate-y-xs -translate-x-xs bottom-xl mb-xl flex h-0 items-start justify-end md:sticky md:top-[100px]"><div class="overflow-hidden rounded-full border-subtlest ring-subtlest divide-subtlest bg-base"><div class="border-subtlest ring-subtlest divide-subtlest bg-subtler"><button data-testid="toggle-wrap-code-button" aria-label="No line wrap" type="button" class="focus-visible:bg-subtle hover:bg-subtle text-quiet  hover:text-foreground dark:hover:bg-subtle font-sans focus:outline-none outline-none outline-transparent transition duration-300 ease-out select-none items-center relative group/button font-semimedium justify-center text-center items-center rounded-full cursor-pointer active:scale-[0.97] active:duration-150 active:ease-outExpo origin-center whitespace-nowrap inline-flex text-sm h-8 aspect-square" data-state="closed"><div class="flex items-center min-w-0 gap-two justify-center"><div class="flex shrink-0 items-center justify-center size-4"><svg role="img" class="inline-flex fill-current" width="16" height="16"><use xlink:href="#pplx-icon-text-wrap-disabled"></use></svg></div></div></button><button data-testid="copy-code-button" aria-label="Copy code" type="button" class="focus-visible:bg-subtle hover:bg-subtle text-quiet  hover:text-foreground dark:hover:bg-subtle font-sans focus:outline-none outline-none outline-transparent transition duration-300 ease-out select-none items-center relative group/button font-semimedium justify-center text-center items-center rounded-full cursor-pointer active:scale-[0.97] active:duration-150 active:ease-outExpo origin-center whitespace-nowrap inline-flex text-sm h-8 aspect-square" data-state="closed"><div class="flex items-center min-w-0 gap-two justify-center"><div class="flex shrink-0 items-center justify-center size-4"><svg role="img" class="inline-flex fill-current" width="16" height="16"><use xlink:href="#pplx-icon-copy"></use></svg></div></div></button></div></div></div><div class="-mt-xl"><div><div data-testid="code-language-indicator" class="text-quiet bg-subtle py-xs px-sm inline-block rounded-br rounded-tl-[3px] font-thin">text</div></div><div><span><code><span><span>Predicted_NRS = 10 * (
</span></span><span>  0.25 * Has_Valid_Price +
</span><span>  0.20 * Delivery_Strength +
</span><span>  0.15 * (1 - normalized_price) +
</span><span>  0.15 * Frequency_Score +
</span><span>  0.25 * (max_rank - rank + 1)/max_rank
</span><span>)
</span><span></span></code></span></div></div></div></pre>

**2. Marketplace Share Metrics:**

* **Dominance Score** per Product: `SUM(NRS for source) / SUM(all NRS for product)`
* **Consistency Score** : Standard deviation of ranks (lower = more consistent)

**3. Time-Based Metrics (when you add timestamps):**

* Rank trend over time (improving/declining)
* Day-of-week patterns
* Response freshness

**4. Gap Analysis:**

* **Rank Gap** : Your rank - Competitor's best rank (per prompt)
* **Price Gap %** : `(Your price - Min price) / Min price * 100`
* **Delivery Gap** : Your delivery_days - Fastest delivery

## **F. Specific Visualizations for Your Data**

From your 99-row sample:

1. **Stacked Bar: Source Distribution by Product**
   * Shows which marketplaces appear most for each product category
   * Data: Group by Product + source_normalized, count occurrences
2. **Box Plot: Price Distribution by Source**
   * Identifies price outliers
   * Shows median, quartiles for each marketplace
   * Filter out price=-1 values
3. **Funnel Chart: Rank Distribution**
   * Shows how many results at rank 1, 2, 3, etc.
   * Your data: 45 at rank 1, 30 at rank 2, 22 at rank 3
4. **Treemap: Product Category Coverage**
   * Size = # of prompts per category
   * Color = Average rank performance
   * From your data: Microwave Oven (15), Ironing Boards (13), Irons (13), etc.
5. **Calendar Heatmap** (when you have timestamps)
   * Shows daily G-SoV or rank performance
   * Helps identify patterns

## **G. Key Calculated Columns to Add**

Create these in your backend before sending to frontend:

<pre class="not-prose w-full rounded font-mono text-sm font-extralight"><div class="codeWrapper text-light selection:text-super selection:bg-super/10 my-md relative flex flex-col rounded font-mono text-sm font-normal bg-subtler"><div class="translate-y-xs -translate-x-xs bottom-xl mb-xl flex h-0 items-start justify-end md:sticky md:top-[100px]"><div class="overflow-hidden rounded-full border-subtlest ring-subtlest divide-subtlest bg-base"><div class="border-subtlest ring-subtlest divide-subtlest bg-subtler"><button data-testid="toggle-wrap-code-button" aria-label="Wrap lines" type="button" class="focus-visible:bg-subtle hover:bg-subtle text-quiet  hover:text-foreground dark:hover:bg-subtle font-sans focus:outline-none outline-none outline-transparent transition duration-300 ease-out select-none items-center relative group/button font-semimedium justify-center text-center items-center rounded-full cursor-pointer active:scale-[0.97] active:duration-150 active:ease-outExpo origin-center whitespace-nowrap inline-flex text-sm h-8 aspect-square" data-state="closed"><div class="flex items-center min-w-0 gap-two justify-center"><div class="flex shrink-0 items-center justify-center size-4"><svg role="img" class="inline-flex fill-current" width="16" height="16"><use xlink:href="#pplx-icon-text-wrap"></use></svg></div></div></button><button data-testid="copy-code-button" aria-label="Copy code" type="button" class="focus-visible:bg-subtle hover:bg-subtle text-quiet  hover:text-foreground dark:hover:bg-subtle font-sans focus:outline-none outline-none outline-transparent transition duration-300 ease-out select-none items-center relative group/button font-semimedium justify-center text-center items-center rounded-full cursor-pointer active:scale-[0.97] active:duration-150 active:ease-outExpo origin-center whitespace-nowrap inline-flex text-sm h-8 aspect-square" data-state="closed"><div class="flex items-center min-w-0 gap-two justify-center"><div class="flex shrink-0 items-center justify-center size-4"><svg role="img" class="inline-flex fill-current" width="16" height="16"><use xlink:href="#pplx-icon-copy"></use></svg></div></div></button></div></div></div><div class="-mt-xl"><div><div data-testid="code-language-indicator" class="text-quiet bg-subtle py-xs px-sm inline-block rounded-br rounded-tl-[3px] font-thin">python</div></div><div><span><code><span class="token token"># Normalized Rank Score</span><span>
</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'nrs'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span></span><span class="token token punctuation">(</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'rank'</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span class="token token">max</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span></span><span class="token token operator">+</span><span></span><span class="token token">1</span><span></span><span class="token token operator">-</span><span> df</span><span class="token token punctuation">[</span><span class="token token">'rank'</span><span class="token token punctuation">]</span><span class="token token punctuation">)</span><span></span><span class="token token operator">/</span><span> df</span><span class="token token punctuation">[</span><span class="token token">'rank'</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span class="token token">max</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span></span><span class="token token operator">*</span><span></span><span class="token token">10</span><span>
</span>
<span></span><span class="token token"># Has Valid Data flags</span><span>
</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'has_price'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span></span><span class="token token punctuation">(</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'price'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">></span><span></span><span class="token token">0</span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span>astype</span><span class="token token punctuation">(</span><span class="token token">int</span><span class="token token punctuation">)</span><span>
</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'has_delivery'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span></span><span class="token token punctuation">(</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'delivery_days'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">>=</span><span></span><span class="token token">0</span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span>astype</span><span class="token token punctuation">(</span><span class="token token">int</span><span class="token token punctuation">)</span><span>
</span>
<span></span><span class="token token"># Per-prompt metrics</span><span>
</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'best_price_in_prompt'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span> df</span><span class="token token punctuation">.</span><span>groupby</span><span class="token token punctuation">(</span><span class="token token">'prompt_id'</span><span class="token token punctuation">)</span><span class="token token punctuation">[</span><span class="token token">'price'</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span>transform</span><span class="token token punctuation">(</span><span>
</span><span></span><span class="token token">lambda</span><span> x</span><span class="token token punctuation">:</span><span> x</span><span class="token token punctuation">[</span><span>x </span><span class="token token operator">></span><span></span><span class="token token">0</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span class="token token">min</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span></span><span class="token token">if</span><span></span><span class="token token punctuation">(</span><span>x </span><span class="token token operator">></span><span></span><span class="token token">0</span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span class="token token">any</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span></span><span class="token token">else</span><span></span><span class="token token operator">-</span><span class="token token">1</span><span>
</span><span></span><span class="token token punctuation">)</span><span>
</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'is_cheapest'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span></span><span class="token token punctuation">(</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'price'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">==</span><span> df</span><span class="token token punctuation">[</span><span class="token token">'best_price_in_prompt'</span><span class="token token punctuation">]</span><span class="token token punctuation">)</span><span></span><span class="token token operator">&</span><span></span><span class="token token punctuation">(</span><span>df</span><span class="token token punctuation">[</span><span class="token token">'price'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">></span><span></span><span class="token token">0</span><span class="token token punctuation">)</span><span>
</span>
<span></span><span class="token token"># Delivery strength</span><span>
</span><span></span><span class="token token">def</span><span></span><span class="token token">delivery_strength</span><span class="token token punctuation">(</span><span>days</span><span class="token token punctuation">)</span><span class="token token punctuation">:</span><span>
</span><span></span><span class="token token">if</span><span> days </span><span class="token token operator"><</span><span></span><span class="token token">0</span><span class="token token punctuation">:</span><span></span><span class="token token">return</span><span></span><span class="token token">0</span><span>
</span><span></span><span class="token token">if</span><span> days </span><span class="token token operator"><=</span><span></span><span class="token token">1</span><span class="token token punctuation">:</span><span></span><span class="token token">return</span><span></span><span class="token token">1.0</span><span>
</span><span></span><span class="token token">if</span><span> days </span><span class="token token operator"><=</span><span></span><span class="token token">3</span><span class="token token punctuation">:</span><span></span><span class="token token">return</span><span></span><span class="token token">0.7</span><span>
</span><span></span><span class="token token">if</span><span> days </span><span class="token token operator"><=</span><span></span><span class="token token">7</span><span class="token token punctuation">:</span><span></span><span class="token token">return</span><span></span><span class="token token">0.3</span><span>
</span><span></span><span class="token token">return</span><span></span><span class="token token">0.1</span><span>
</span>
<span>df</span><span class="token token punctuation">[</span><span class="token token">'delivery_strength'</span><span class="token token punctuation">]</span><span></span><span class="token token operator">=</span><span> df</span><span class="token token punctuation">[</span><span class="token token">'delivery_days'</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span class="token token">apply</span><span class="token token punctuation">(</span><span>delivery_strength</span><span class="token token punctuation">)</span><span>
</span>
<span></span><span class="token token"># G-SoV per source</span><span>
</span><span>gsov </span><span class="token token operator">=</span><span> df</span><span class="token token punctuation">.</span><span>groupby</span><span class="token token punctuation">(</span><span class="token token">'source_normalized'</span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span class="token token">apply</span><span class="token token punctuation">(</span><span>
</span><span></span><span class="token token">lambda</span><span> x</span><span class="token token punctuation">:</span><span></span><span class="token token punctuation">(</span><span class="token token punctuation">(</span><span>x</span><span class="token token punctuation">[</span><span class="token token">'rank'</span><span class="token token punctuation">]</span><span></span><span class="token token operator"><=</span><span></span><span class="token token">2</span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span class="token token">sum</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span></span><span class="token token operator">/</span><span> df</span><span class="token token punctuation">[</span><span class="token token">'prompt_id'</span><span class="token token punctuation">]</span><span class="token token punctuation">.</span><span>nunique</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span class="token token punctuation">)</span><span>
</span><span></span><span class="token token punctuation">)</span><span class="token token punctuation">.</span><span>to_dict</span><span class="token token punctuation">(</span><span class="token token punctuation">)</span><span>
</span></code></span></div></div></div></pre>
