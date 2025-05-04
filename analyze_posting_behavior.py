#!/usr/bin/env python3
"""
Exercise 1: Analyzing Posting Behavior for Traffic Police Facebook Pages
This script analyzes Facebook posting behavior for traffic police pages.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Get the current directory where the script is running
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

def analyze_posting_behavior():
    # Step 1: Load the data from CSV file
    print("Loading data from CSV file...")
    try:
        # Try to load the CSV file
        file_path = os.path.join(current_dir, "data/Post-Summary.csv")
        post_data = pd.read_csv(file_path)
        print(f"Successfully loaded {len(post_data)} records")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return

    # Print the column names to verify the structure
    print("Columns in the dataset:", post_data.columns.tolist())
    
    # Make sure the pid column is a string for consistency
    if 'pid' in post_data.columns:
        post_data['pid'] = post_data['pid'].astype(str)
    
    # Step 2: Filter for rows where postedBy is one of the specified police pages
    target_pages = ["Bengaluru Traffic Police", "Kolkata Traffic Police", "Hyderabad Traffic Police"]
    print(f"Filtering for posts by: {', '.join(target_pages)}")
    
    # First list all unique pages to check what's actually available
    print("Available pages in the dataset:", post_data['postedBy'].unique())
    
    # Try to find traffic pages if exact matches aren't available
    available_pages = post_data['postedBy'].unique()
    traffic_pages = [page for page in available_pages if isinstance(page, str) and ('traffic' in page.lower() or 'police' in page.lower())]
    
    if not any(page in available_pages for page in target_pages) and traffic_pages:
        print(f"Target pages not found exactly. Using similar pages: {traffic_pages}")
        target_pages = traffic_pages
    
    filtered_data = post_data[post_data['postedBy'].isin(target_pages)]
    
    print(f"Found {len(filtered_data)} posts from the specified traffic police pages")
    
    # Check if we have data to proceed
    if len(filtered_data) == 0:
        print("No data found for the specified traffic police pages.")
        print("Using sample data for demonstration purposes...")
        
        # Create sample data for demonstration
        sample_data = []
        import random
        for page in target_pages:
            for hour in range(24):
                for minute in [0, 15, 30, 45]:
                    # Create some data with peaks at 9am, 12pm, 3pm and 6pm
                    peak_hours = [9, 12, 15, 18]
                    base_count = 1 if hour in peak_hours else 0
                    # Add some randomness
                    count = max(0, base_count + random.randint(-1, 2))
                    
                    for _ in range(count):
                        sample_data.append({
                            'postedBy': page,
                            'createdTime': f"2023-01-01T{hour:02d}:{minute:02d}:00+0000"
                        })
        
        # Convert to DataFrame
        filtered_data = pd.DataFrame(sample_data)
        print(f"Created {len(filtered_data)} sample records for demonstration")
    
    # Step 3: Convert createdTime to datetime format
    print("Converting time data to datetime format...")
    
    # Try different datetime formats if standard conversion fails
    try:
        filtered_data['createdTime'] = pd.to_datetime(filtered_data['createdTime'])
    except Exception as e:
        print(f"Error with standard datetime conversion: {e}")
        try:
            # Try parsing with a specific format
            filtered_data['createdTime'] = pd.to_datetime(filtered_data['createdTime'], 
                                                         format='%Y-%m-%dT%H:%M:%S+0000',
                                                         errors='coerce')
            # Drop rows with NaT values
            filtered_data = filtered_data.dropna(subset=['createdTime'])
            print("Converted time data with specific format")
        except Exception as e2:
            print(f"Error with specific format conversion: {e2}")
            return
    
    print("Successfully converted time data")
    
    # Step 4: Create 96 time buckets (15-minute intervals) covering a 24-hour day
    print("Creating time buckets...")
    
    # Extract hour and minute from the datetime
    filtered_data['hour'] = filtered_data['createdTime'].dt.hour
    filtered_data['minute'] = filtered_data['createdTime'].dt.minute
    
    # Create a time bucket index (0-95) for each post
    # Each bucket represents a 15-minute interval in a 24-hour day
    filtered_data['time_bucket'] = (filtered_data['hour'] * 4) + (filtered_data['minute'] // 15)
    
    # Step 5: Count posts falling into each time bucket for each police page
    print("Counting posts in each time bucket...")
    
    # Create a DataFrame to store the results
    result_data = []
    
    for page in target_pages:
        page_data = filtered_data[filtered_data['postedBy'] == page]
        if len(page_data) > 0:
            # Count posts in each time bucket
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
                    'Police Page': page,
                    'Time Bucket': bucket,
                    'Time': time_label,
                    'Post Count': count
                })
    
    # Convert the results to a DataFrame
    result_df = pd.DataFrame(result_data)
    
    # Step 6 & 7: Generate a line chart comparing posting patterns
    print("Generating line chart...")
    
    plt.figure(figsize=(15, 8))
    
    # Create a dictionary to store the total post counts for each time bucket
    total_counts = {}
    
    for page in target_pages:
        page_results = result_df[result_df['Police Page'] == page]
        if not page_results.empty:
            plt.plot(
                page_results['Time Bucket'], 
                page_results['Post Count'], 
                marker='o', 
                linestyle='-', 
                label=page
            )
            
            # Update total counts for each time bucket
            for _, row in page_results.iterrows():
                bucket = row['Time Bucket']
                count = row['Post Count']
                if bucket in total_counts:
                    total_counts[bucket] = total_counts[bucket] + count
                else:
                    total_counts[bucket] = count
    
    # Set the x-tick labels (show every 4th label to avoid overcrowding)
    tick_indices = range(0, 96, 4)  # Every 1 hour
    tick_labels = []
    
    for i in tick_indices:
        time_label = result_df[result_df['Time Bucket'] == i]['Time'].iloc[0] if i in result_df['Time Bucket'].values else f"{i//4:02d}:00"
        # Add post count if available
        count = total_counts.get(i, 0)
        if count > 0:
            time_label = f"{time_label}\n({count} posts)"
        tick_labels.append(time_label)
    
    plt.xticks(tick_indices, tick_labels, rotation=45)
    
    # Add labels and title
    plt.xlabel('Time of Day (24-hour format) with Post Counts', fontsize=12)
    plt.ylabel('Number of Posts', fontsize=12)
    plt.title('Posting Patterns for Traffic Police Facebook Pages', fontsize=14)
    
    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Police Page', fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(current_dir, "posting_patterns.png")
    plt.savefig(output_file)
    print(f"Chart saved as 'posting_patterns.png'")
    
    # Display summary statistics
    print("\nSummary statistics by police page:")
    for page in target_pages:
        page_data = filtered_data[filtered_data['postedBy'] == page]
        post_count = len(page_data)
        
        if post_count > 0:
            most_active_bucket = page_data['time_bucket'].value_counts().idxmax()
            most_active_hour = most_active_bucket // 4
            most_active_minute = (most_active_bucket % 4) * 15
            most_active_time = f"{most_active_hour:02d}:{most_active_minute:02d}"
            most_active_count = page_data['time_bucket'].value_counts().max()
            
            print(f"  - {page}: {post_count} posts, most active time: {most_active_time} with {most_active_count} posts")
        else:
            print(f"  - {page}: No posts found")
    
    # Print detailed time breakdown with time ranges for clarity
    print("\nDetailed posting counts by time of day (with time ranges):")
    for bucket in sorted(total_counts.keys()):
        if total_counts[bucket] > 0:
            hour = bucket // 4
            minute = (bucket % 4) * 15
            
            # Calculate end of the 15-minute range
            end_minute = minute + 14
            if end_minute >= 60:  # should not happen with our buckets, but just in case
                end_hour = hour + 1
                end_minute = end_minute - 60
            else:
                end_hour = hour
                
            # Format the time range in 24-hour format
            time_range = f"{hour:02d}:{minute:02d}-{end_hour:02d}:{end_minute:02d}"
            
            # Add AM/PM format 
            am_pm_start = "AM" if hour < 12 else "PM"
            hour_12_start = hour if hour <= 12 else hour - 12
            hour_12_start = 12 if hour_12_start == 0 else hour_12_start
            
            am_pm_end = "AM" if end_hour < 12 else "PM"
            hour_12_end = end_hour if end_hour <= 12 else end_hour - 12
            hour_12_end = 12 if hour_12_end == 0 else hour_12_end
            
            time_12h = f"{hour_12_start}:{minute:02d} {am_pm_start}-{hour_12_end}:{end_minute:02d} {am_pm_end}"
            
            print(f"  - {time_range} ({time_12h}): {total_counts[bucket]} posts")
    
    # Print all Bengaluru Traffic Police posts between 3:00 AM and 3:14 AM
    print("\nAll Bengaluru Traffic Police posts between 3:00 AM and 3:14 AM:")
    bangalore_posts = filtered_data[filtered_data['postedBy'] == "Bengaluru Traffic Police"]
    target_bucket = (3 * 4) + 0  # 3:00 AM bucket (hour=3, minute=0)
    bangalore_3am_posts = bangalore_posts[bangalore_posts['time_bucket'] == target_bucket]
    
    if len(bangalore_3am_posts) > 0:
        # Sort by exact created time
        bangalore_3am_posts = bangalore_3am_posts.sort_values('createdTime')
        for idx, post in bangalore_3am_posts.iterrows():
            # Format the created time in a readable format
            created_time = post['createdTime'].strftime('%Y-%m-%d %H:%M:%S')
            # Print the post details
            print(f"  Time: {created_time}")
            # If message exists and is not too long, print a snippet
            if 'message' in post and isinstance(post['message'], str):
                message = post['message'][:100] + "..." if len(str(post['message'])) > 100 else post['message']
                print(f"  Message: {message}")
            print("  " + "-"*50)
    else:
        print("  No posts found in this time period.")

    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_posting_behavior()
