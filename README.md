# Social Media Posting Behavior Analysis

This project analyzes posting behavior and engagement patterns across different Facebook pages, with a focus on traffic police accounts, e-commerce brands, and other organization types. The analysis helps identify optimal posting times and engagement patterns.

## Project Overview

This analysis explores:
- Posting patterns of traffic police Facebook pages
- User reaction patterns to posts
- E-commerce brand posting behavior vs. engagement
- Content analysis through word clouds for different organization types
- Comparative analysis of posting times vs. engagement metrics

## Dataset

The analysis uses two primary datasets:
- `data/Post-Summary.csv`: Contains post metadata including posting time, page name, and engagement metrics
- `data/Comments.csv`: Contains comment data related to the posts

## Project Structure

```
├── analyze_posting_behavior.py      # Analysis script for traffic police posting patterns
├── analyze_user_reactions.py        # Analysis of user engagement with posts
├── category_analysis_wordcloud.py   # Word cloud generation by organization category
├── extract_times.py                 # Helper script for time extraction and analysis
├── Social_Media_Posting_Analysis.ipynb  # Jupyter notebook with comprehensive analysis
├── data/                            # Dataset directory
│   ├── Comments.csv                 # Comment data
│   ├── Post-Summary.csv             # Post metadata
│   └── ...
├── images/                          # Generated visualizations
│   ├── posting_patterns.png         # Traffic police posting pattern visualization
│   ├── user_reaction_patterns.png   # User reaction analysis
│   ├── ecommerce_posting_patterns.png  # E-commerce posting patterns
│   └── ...
└── word_clouds/                     # Generated word clouds by organization
    ├── Aircel India_wordcloud.png
    ├── Amazon India_wordcloud.png
    └── ...
```

## Key Visualizations

The project generates several visualizations:
- Posting frequency by time of day
- User engagement patterns
- Comparative analysis between posting time and engagement
- Word clouds showing key topics by organization
- Recommended posting windows based on historical engagement

## How to Run

### Prerequisites
- Python 3.6+
- Required packages: pandas, matplotlib, numpy, wordcloud

### Setup
```bash
# Clone the repository
git clone <repository-url>

# Install required packages
pip install pandas matplotlib numpy wordcloud
```

### Running the Analysis
```bash
# Run the traffic police posting analysis
python analyze_posting_behavior.py

# Run the user reaction analysis
python analyze_user_reactions.py

# Generate word clouds
python category_analysis_wordcloud.py
```

Alternatively, you can explore the comprehensive analysis in the Jupyter notebook:
```bash
jupyter notebook Social_Media_Posting_Analysis.ipynb
```

## Key Findings

- Traffic police pages show distinct posting patterns with peaks during [specific times]
- E-commerce brands tend to post more frequently during [specific times] but receive higher engagement during [other times]
- User engagement is highest during [specific periods]
- Content analysis shows different themes across organization types
- There's a correlation between posting frequency and engagement metrics

## Future Work

- Expand analysis to include more organization types
- Incorporate sentiment analysis of comments
- Build predictive models for optimal posting times
- Analyze seasonal variations in posting patterns and engagement

## License

[Specify your license here]