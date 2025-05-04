import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import re
import os
import hashlib
from collections import Counter

# Set the style for plots
plt.style.use('ggplot')
sns.set_palette("Set2")

def load_data():
    """Load the Post Summary data"""
    # Read the CSV file
    post_summary = pd.read_csv('data/Post-Summary.csv')
    # Convert likesCount to numeric, handling empty strings
    post_summary['likesCount'] = pd.to_numeric(post_summary['likesCount'], errors='coerce')
    # Fill NaN values with 0
    post_summary['likesCount'] = post_summary['likesCount'].fillna(0)
    return post_summary

def analyze_likes_by_category(post_summary):
    """Calculate average likes per post for each category"""
    # List of categories to include in the analysis
    target_categories = [
        'Politician', 
        'Media/News/Publishing', 
        'Telecommunication', 
        'Product/Service', 
        'Website', 
        'Retail and Consumer Merchandise', 
        'Clothing', 
        'Hospital/Clinic', 
        'Government Organization', 
        'Health/Medical/Pharmaceuticals'
    ]
    
    # Filter the data to include only the specified categories
    filtered_data = post_summary[post_summary['category'].isin(target_categories)]
    
    # Group by category and calculate average likes
    category_likes = filtered_data.groupby('category')['likesCount'].agg(['mean', 'sum', 'count']).reset_index()
    # Rename columns for clarity
    category_likes.columns = ['Category', 'Average Likes', 'Total Likes', 'Post Count']
    # Sort by average likes in descending order
    category_likes = category_likes.sort_values('Average Likes', ascending=False)
    
    # Print the results
    print("\nCategory Analysis Results:")
    print("=" * 50)
    for _, row in category_likes.iterrows():
        print(f"{row['Category']}: {row['Average Likes']:.2f} avg likes across {row['Post Count']} posts (Total: {row['Total Likes']})")
    
    return category_likes

def create_category_bar_chart(category_likes):
    """Create a bar chart showing average likes per category"""
    # Filter out categories with excessively long names for better plotting
    filtered_likes = category_likes[category_likes['Category'].str.len() < 30]
    
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    ax = sns.barplot(x='Category', y='Average Likes', data=filtered_likes)
    
    # Add post count as text on each bar
    for i, row in enumerate(filtered_likes.itertuples()):
        ax.text(i, row._2 / 2, f'n={row._3}', 
                horizontalalignment='center', 
                color='white', 
                fontweight='bold')
    
    # Add labels and title
    plt.title('Average Number of Likes per Post by Category', fontsize=16)
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Average Likes', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('category_likes_analysis.png', dpi=300)
    plt.close()

def save_to_excel(category_likes):
    """Save category analysis results to Excel"""
    # Create a Excel writer object
    writer = pd.ExcelWriter('category_analysis.xlsx', engine='xlsxwriter')
    
    # Write the dataframe to excel
    category_likes.to_excel(writer, sheet_name='Category Analysis', index=False)
    
    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Category Analysis']
    
    # Add a format for the header
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # Write the column headers with the defined format
    for col_num, value in enumerate(category_likes.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Set the column width
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:C', 15)
    
    # Close the Pandas Excel writer and save the Excel file
    writer._save()

def preprocess_text(text):
    """Preprocess text for word cloud generation"""
    if pd.isna(text) or text == "":
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove URLs, mentions, hashtags, and special characters
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove non-ASCII characters
    text = ''.join(c for c in text if ord(c) < 128)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_word_clouds(post_summary):
    """Generate word clouds for each organization based on post messages"""
    # Add custom stopwords
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(['will', 'now', 'get', 'one', 'like', 'shop', 'offers', 
                            'available', 'check', 'new', 'today', 'facebook', 'make',
                            'offer', 'limited', 'time', 'can', 'also', 'discount',
                            'just', 'buy', 'shopping', 'day', 'know', 'use'])
    
    # Get unique organizations
    organizations = post_summary['postedBy'].unique()
    
    # Create a directory for word cloud images if it doesn't exist
    if not os.path.exists('word_clouds'):
        os.makedirs('word_clouds')
    
    # Generate word cloud for each organization
    for org in organizations:
        if pd.isna(org) or org == "":
            continue
            
        # Filter posts by organization
        org_posts = post_summary[post_summary['postedBy'] == org]
        
        # Combine all messages
        all_text = ' '.join(org_posts['message'].apply(preprocess_text))
        
        if all_text.strip():  # Check if there's text to process
            # Create the word cloud
            wordcloud = WordCloud(
                background_color='white',
                max_words=100,
                max_font_size=40,
                width=800,
                height=400,
                stopwords=custom_stopwords,
                random_state=42
            ).generate(all_text)
            
            # Create a safe filename using a hash for long organization names
            if len(str(org)) > 30:
                # Hash the organization name for consistency
                hashed_name = hashlib.md5(str(org).encode('utf-8')).hexdigest()[:10]
                safe_filename = f"org_{hashed_name}_wordcloud.png"
                
                # Create a mapping file to track hashed names
                with open("word_clouds/org_mapping.txt", "a") as f:
                    f.write(f"{safe_filename}: {org}\n")
            else:
                safe_filename = f"{org}_wordcloud.png"
                
            # Plot the word cloud
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud: {str(org)[:30]}{"..." if len(str(org)) > 30 else ""}', fontsize=16)
            plt.tight_layout()
            
            # Save the word cloud image
            plt.savefig(f'word_clouds/{safe_filename}', dpi=300)
            plt.close()
            
            print(f"Generated word cloud for {str(org)[:30]}...")
        else:
            print(f"No text available to generate word cloud for {str(org)[:30]}...")

def main():
    print("Starting Category Analysis and Word Cloud Generation...")
    
    # Load data
    post_summary = load_data()
    
    # Analyze likes by category
    category_likes = analyze_likes_by_category(post_summary)
    
    # Create bar chart
    create_category_bar_chart(category_likes)
    print("Bar chart created and saved as 'category_likes_analysis.png'")
    
    # Save to Excel
    save_to_excel(category_likes)
    print("Category analysis saved to 'category_analysis.xlsx'")
    
    # Generate word clouds
    print("\nGenerating word clouds for each organization...")
    generate_word_clouds(post_summary)
    print("\nWord clouds have been saved to the 'word_clouds' directory")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()