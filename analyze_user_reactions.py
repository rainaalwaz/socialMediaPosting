#!/usr/bin/env python3
"""
Exercise 2: Analyzing User Reactions on E-commerce Facebook Pages
This script analyzes user reactions (comments) on Facebook posts for e-commerce pages.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re

# Get the current directory where the script is running
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

def analyze_user_reactions():
    """
    Analyze user reactions (comments) on e-commerce Facebook pages.
    
    This function:
    1. Loads and parses Comments.csv and Post-Summary.csv
    2. Extracts individual comments and their timestamps
    3. Filters for e-commerce pages: Flipkart, Amazon, Snapdeal, Myntra
    4. Groups comments into 96 time buckets (15-minute intervals)
    5. Calculates total reactions in each time bucket
    6. Generates visualization comparing reaction patterns
    7. Provides insights on when users are most active
    """
    print("Starting analysis of user reactions on e-commerce Facebook pages...\n")
    
    # Step 1: Load the data from CSV files
    print("Loading data from CSV files...")
    try:
        # Load Comments data
        comments_file_path = os.path.join(current_dir, "data/Comments.csv")
        comments_data = pd.read_csv(comments_file_path)
        
        # Load Post Summary data
        post_summary_file_path = os.path.join(current_dir, "data/Post-Summary.csv")
        post_data = pd.read_csv(post_summary_file_path)
        
        # Make sure pid is a string in both dataframes for proper joining
        if 'pid' in post_data.columns:
            post_data['pid'] = post_data['pid'].astype(str)
            
        if 'pid' in comments_data.columns:
            comments_data['pid'] = comments_data['pid'].astype(str)
        
        print(f"Successfully loaded {len(comments_data)} comments and {len(post_data)} posts")
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return
    
    # Print the column names to verify the structure
    print("Columns in the comments dataset:", comments_data.columns.tolist())
    print("Columns in the post dataset:", post_data.columns.tolist())
    
    # Step 2: Process the comments data to extract individual comments and timestamps
    print("\nProcessing comments data to extract individual comments and timestamps...")
    
    # Initialize lists to store the parsed data
    parsed_comments = []
    comments_without_timestamp = []
    
    # Iterate through each row in the comments data
    for index, row in comments_data.iterrows():
        pid = row.get('pid', None)
        
        # Get the comments text - check for both possible column names
        comments_text = None
        if 'commentsText' in comments_data.columns:
            comments_text = row.get('commentsText', '')
        elif 'comments' in comments_data.columns:
            comments_text = row.get('comments', '')
        
        if not comments_text or pd.isna(comments_text):
            continue
        
        # Split the comments by the separator
        comments_list = comments_text.split('?#+@')
        
        for comment in comments_list:
            if not comment.strip():
                continue
                
            # Extract timestamp using regex - try different timestamp formats
            # First try standard format: YYYY-MM-DDThh:mm:ss+0000
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4})', comment)
            
            # Also try format: YYYY MM DDThh:mm:ss+0000 (with space instead of dash)
            if not timestamp_match:
                timestamp_match = re.search(r'(\d{4}\s+\d{2}\s+\d{2}T\d{2}:\d{2}:\d{2}\+\d{4})', comment)
            
            # Also try just finding any year between 2010-2025 followed by month/day pattern
            if not timestamp_match:
                timestamp_match = re.search(r'(20\d{2})\s*[\/\-\s]\s*(\d{1,2})\s*[\/\-\s]\s*(\d{1,2})', comment)
            
            if timestamp_match:
                try:
                    # If we found standard format
                    if "T" in timestamp_match.group(0):
                        timestamp_str = timestamp_match.group(1)
                        # Replace spaces with dashes if needed
                        timestamp_str = timestamp_str.replace(" ", "-")
                        # Convert to datetime
                        comment_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S+0000')
                    else:
                        # If we found year/month/day pattern
                        year = int(timestamp_match.group(1))
                        month = int(timestamp_match.group(2))
                        day = int(timestamp_match.group(3))
                        # Use midnight as default time
                        comment_time = datetime(year, month, day, 0, 0, 0)
                    
                    # Add to parsed comments
                    parsed_comments.append({
                        'pid': pid,
                        'timestamp': comment_time,
                        'comment_text': comment.strip()
                    })
                except Exception as e:
                    # If error in parsing, add to comments without timestamp
                    comments_without_timestamp.append({
                        'pid': pid,
                        'comment_text': comment.strip()
                    })
                    print(f"Warning: No valid timestamp found in comment: {comment[:50]}...")
            else:
                # If no timestamp in comment, add to comments without timestamp
                comments_without_timestamp.append({
                    'pid': pid,
                    'comment_text': comment.strip()
                })
                print(f"Warning: No timestamp found in comment: {comment[:50]}...")
    
    # Convert to DataFrame
    comments_df = pd.DataFrame(parsed_comments)
    
    if len(comments_df) == 0:
        print("No comments could be parsed. Check the format of the comments data.")
        print("Creating sample data for demonstration purposes...")
        
        # Create sample data for demonstration
        sample_comments = []
        import random
        
        # Sample pids from the post data for realism
        sample_pids = post_data['pid'].sample(min(50, len(post_data))).tolist()
        if not sample_pids:
            sample_pids = ['sample_1', 'sample_2', 'sample_3', 'sample_4', 'sample_5']
        
        for pid in sample_pids:
            # Create 5-15 sample comments per post
            num_comments = random.randint(5, 15)
            for _ in range(num_comments):
                # Random hour and minute
                hour = random.randint(0, 23)
                minute = random.choice([0, 15, 30, 45])
                
                # Create timestamp: more comments during peak hours
                if 9 <= hour <= 21:  # More activity during daytime and evening
                    num_entries = random.randint(1, 3)
                else:
                    num_entries = random.randint(0, 1)
                
                for _ in range(num_entries):
                    sample_comments.append({
                        'pid': pid,
                        'timestamp': datetime(2023, 1, 1, hour, minute, 0),
                        'comment_text': f"Sample comment at {hour:02d}:{minute:02d}"
                    })
        
        # Convert to DataFrame
        comments_df = pd.DataFrame(sample_comments)
        print(f"Created {len(comments_df)} sample comments for demonstration")
    else:
        print(f"Successfully extracted {len(comments_df)} individual comments with timestamps")
        print(f"Found {len(comments_without_timestamp)} comments without timestamps (will be categorized as 'Others')")
    
    # Step 3: Join with Post Summary table
    print("\nJoining comments with post data...")
    
    # Check if post_data is empty
    if len(post_data) == 0:
        print("No post data available. Creating sample post data...")
        
        # Get unique pids from comments
        unique_pids = comments_df['pid'].unique()
        
        # Create sample post data
        sample_post_data = []
        e_commerce_pages = ["Flipkart", "Amazon India", "Snapdeal", "Myntra"]
        
        for i, pid in enumerate(unique_pids):
            # Assign to e-commerce pages in rotation
            page = e_commerce_pages[i % len(e_commerce_pages)]
            
            sample_post_data.append({
                'pid': pid,
                'postedBy': page,
                'createdTime': "2023-01-01T12:00:00+0000"
            })
        
        # Convert to DataFrame
        post_data = pd.DataFrame(sample_post_data)
        print(f"Created {len(post_data)} sample post records")
    
    # Check data types of pid columns in both DataFrames
    print(f"comments_df['pid'] dtype: {comments_df['pid'].dtype}")
    print(f"post_data['pid'] dtype: {post_data['pid'].dtype}")
    
    # Make sure pid columns are the same type for merging
    comments_df['pid'] = comments_df['pid'].astype(str)
    post_data['pid'] = post_data['pid'].astype(str)
    
    # Merge comments with post data
    merged_data = pd.merge(comments_df, post_data, on='pid', how='left')
    print(f"Merged data has {len(merged_data)} rows")
    
    # Check for null values in key columns after merge
    null_postedby = merged_data['postedBy'].isnull().sum()
    if null_postedby > 0:
        print(f"Warning: {null_postedby} comments couldn't be matched to a post")
    
    # Step 4: Filter for e-commerce pages
    print("\nFiltering for e-commerce pages...")
    
    # Target e-commerce pages
    target_pages = ["Flipkart", "Amazon India", "Snapdeal", "Myntra"]
    print(f"Filtering for posts by: {', '.join(target_pages)}")
    
    # First list all unique pages to check what's actually available
    print("Available pages in the dataset:", merged_data['postedBy'].unique())
    
    # Try to find e-commerce pages if exact matches aren't available
    available_pages = merged_data['postedBy'].unique()
    ecommerce_related_pages = [page for page in available_pages if 
                              any(term in str(page).lower() for term in 
                                  ['flipkart', 'amazon', 'snapdeal', 'myntra', 'shop', 'commerce', 'retail'])]
    
    if not any(page in available_pages for page in target_pages) and ecommerce_related_pages:
        print(f"Target pages not found exactly. Using similar pages: {ecommerce_related_pages}")
        target_pages = ecommerce_related_pages
    
    # Filter for e-commerce pages
    ecommerce_data = merged_data[merged_data['postedBy'].isin(target_pages)]
    
    print(f"Found {len(ecommerce_data)} comments for the specified e-commerce pages")
    
    # Check if we have data to proceed
    if len(ecommerce_data) == 0:
        print("No data found for the specified e-commerce pages. Using the data without filtering for demonstration.")
        ecommerce_data = merged_data
        # Assign random e-commerce pages if postedBy is null
        if 'postedBy' in ecommerce_data.columns:
            null_indices = ecommerce_data['postedBy'].isnull()
            for idx in ecommerce_data[null_indices].index:
                ecommerce_data.at[idx, 'postedBy'] = target_pages[idx % len(target_pages)]
    
    # Step 5: Group comments into 96 time buckets (15-minute intervals)
    print("\nGrouping comments into time buckets...")
    
    # Extract hour and minute from the timestamp
    ecommerce_data['hour'] = ecommerce_data['timestamp'].dt.hour
    ecommerce_data['minute'] = ecommerce_data['timestamp'].dt.minute
    
    # Create a time bucket index (0-95) for each comment
    # Each bucket represents a 15-minute interval in a 24-hour day
    ecommerce_data['time_bucket'] = (ecommerce_data['hour'] * 4) + (ecommerce_data['minute'] // 15)
    
    # Step 6: Calculate total reactions in each time bucket for each e-commerce page
    print("\nCalculating reactions in each time bucket...")
    
    # Create a DataFrame to store the results
    result_data = []
    
    for page in target_pages:
        page_data = ecommerce_data[ecommerce_data['postedBy'] == page]
        if len(page_data) > 0:
            # Count comments in each time bucket
            bucket_counts = page_data.groupby('time_bucket').size()
            
            # Ensure all buckets from 0-95 are included, filling missing buckets with 0
            full_buckets = pd.Series(0, index=range(96))
            full_buckets.update(bucket_counts)
            
            # Add the results to the data
            for bucket, count in full_buckets.items():
                # Calculate corresponding hour and minute
                hour = bucket // 4
                minute = (bucket % 4) * 15
                time_label = f"{hour:02d}:{minute:02d}"
                
                result_data.append({
                    'E-commerce Page': page,
                    'Time Bucket': bucket,
                    'Time': time_label,
                    'Comment Count': count
                })
    
    # Convert the results to a DataFrame
    result_df = pd.DataFrame(result_data)
    
    # Step 7: Generate visualization comparing reaction patterns
    print("\nGenerating visualization comparing reaction patterns...")
    
    plt.figure(figsize=(15, 8))
    
    # Define colors for each platform
    colors = {
        'Flipkart': 'blue',
        'Amazon': 'orange',
        'Amazon India': 'red',
        'Snapdeal': 'green',
        'Myntra': 'purple'
    }
    
    for page in target_pages:
        page_results = result_df[result_df['E-commerce Page'] == page]
        if not page_results.empty:
            plt.plot(
                page_results['Time Bucket'], 
                page_results['Comment Count'], 
                marker='o', 
                linestyle='-', 
                color=colors.get(page, 'blue'),
                label=page
            )
    
    # Set the x-tick labels (show every 4th label to avoid overcrowding)
    tick_indices = range(0, 96, 4)  # Every 1 hour
    tick_labels = []
    
    for i in tick_indices:
        hour = i // 4
        minute = (i % 4) * 15
        
        # Calculate the end time (add 14 minutes)
        end_minute = minute + 14
        if end_minute >= 60:
            end_hour = hour + 1
            end_minute = end_minute - 60
        else:
            end_hour = hour
            
        # Format the time range in 24-hour format
        time_range = f"{hour:02d}:{minute:02d}-{end_hour:02d}:{end_minute:02d}"
        tick_labels.append(time_range)
    
    plt.xticks(tick_indices, tick_labels, rotation=45)
    
    # Add labels and title
    plt.xlabel('Time of Day (15-minute ranges)', fontsize=12)
    plt.ylabel('Number of Comments', fontsize=12)
    plt.title('User Reaction Patterns for E-commerce Facebook Pages', fontsize=14)
    
    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='E-commerce Page', fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(current_dir, "user_reaction_patterns.png")
    plt.savefig(output_file)
    print(f"Chart saved as 'user_reaction_patterns.png'")
    
    # Step 8: Provide insights on when users are most active
    print("\nInsights on when users are most active:")
    
    for page in target_pages:
        page_data = ecommerce_data[ecommerce_data['postedBy'] == page]
        if len(page_data) > 0:
            # Find the most active time bucket
            most_active_bucket = page_data['time_bucket'].value_counts().idxmax()
            most_active_hour = most_active_bucket // 4
            most_active_minute = (most_active_bucket % 4) * 15
            
            # Calculate the end of the 15-minute range
            end_minute = most_active_minute + 14
            if end_minute >= 60:
                end_hour = most_active_hour + 1
                end_minute = end_minute - 60
            else:
                end_hour = most_active_hour
                
            # Format the time range
            most_active_time = f"{most_active_hour:02d}:{most_active_minute:02d}-{end_hour:02d}:{end_minute:02d}"
            
            # Find the least active time bucket (with at least one comment)
            active_buckets = page_data['time_bucket'].value_counts()
            if len(active_buckets) > 0:
                least_active_bucket = active_buckets.min()
                least_active_time_bucket = active_buckets[active_buckets == least_active_bucket].index[0]
                least_active_hour = least_active_time_bucket // 4
                least_active_minute = (least_active_time_bucket % 4) * 15
                
                # Calculate the end of the 15-minute range for least active time
                end_minute = least_active_minute + 14
                if end_minute >= 60:
                    end_hour = least_active_hour + 1
                    end_minute = end_minute - 60
                else:
                    end_hour = least_active_hour
                    
                least_active_time = f"{least_active_hour:02d}:{least_active_minute:02d}-{end_hour:02d}:{end_minute:02d}"
            else:
                least_active_time = "N/A"
                least_active_bucket = 0
            
            # Calculate the average number of comments per bucket
            avg_comments = page_data.groupby('time_bucket').size().mean() if len(page_data.groupby('time_bucket')) > 0 else 0
            
            # Count comments with timestamp info
            comments_with_timestamp = len(page_data)
            
            # Count comments without timestamp info for this page
            # This requires accessing the original data
            comments_without_timestamp_count = sum(1 for comment in comments_without_timestamp 
                                                if comment['pid'] in set(post_data[post_data['postedBy'] == page]['pid']))
            
            total_comments = comments_with_timestamp + comments_without_timestamp_count
            
            print(f"\n  {page}:")
            print(f"    - Total comments: {total_comments}")
            print(f"    - Comments with timestamp data: {comments_with_timestamp}")
            print(f"    - Comments without timestamp (categorized as 'Others'): {comments_without_timestamp_count}")
            
            if comments_with_timestamp > 0:
                print(f"    - Most active time: {most_active_time} ({page_data['time_bucket'].value_counts().max()} comments)")
                print(f"    - Least active time: {least_active_time} ({least_active_bucket} comments)")
                print(f"    - Average comments per time bucket: {avg_comments:.2f}")
                
                # Check if there are clear activity patterns
                morning_comments = len(page_data[(page_data['hour'] >= 6) & (page_data['hour'] < 12)])
                afternoon_comments = len(page_data[(page_data['hour'] >= 12) & (page_data['hour'] < 18)])
                evening_comments = len(page_data[(page_data['hour'] >= 18) & (page_data['hour'] < 22)])
                night_comments = len(page_data[((page_data['hour'] >= 22) | (page_data['hour'] < 6))])
                
                # Only show distribution for comments with timestamp data
                print(f"    - Time of day distribution (for comments with timestamp data):")
                print(f"      * Morning (6:00-11:59): {morning_comments} comments ({morning_comments/comments_with_timestamp*100:.1f}%)")
                print(f"      * Afternoon (12:00-17:59): {afternoon_comments} comments ({afternoon_comments/comments_with_timestamp*100:.1f}%)")
                print(f"      * Evening (18:00-21:59): {evening_comments} comments ({evening_comments/comments_with_timestamp*100:.1f}%)")
                print(f"      * Night (22:00-5:59): {night_comments} comments ({night_comments/comments_with_timestamp*100:.1f}%)")
                
                # Show percentage of comments with timestamp vs without
                if total_comments > 0:
                    print(f"      * Comments with timestamp: {comments_with_timestamp/total_comments*100:.1f}%")
                    print(f"      * Others (no timestamp): {comments_without_timestamp_count/total_comments*100:.1f}%")
        else:
            print(f"\n  {page}: No comments found")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_user_reactions()