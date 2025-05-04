import pandas as pd
data = pd.read_csv('Post-Summary.csv')
bangalore_posts = data[data['postedBy'] == 'Bengaluru Traffic Police']

# Filter posts made between 3:00-3:14 AM
early_morning_posts = []
for _, row in bangalore_posts.iterrows():
    time_str = row['createdTime']
    # Check if time is between 3:00-3:14 AM
    if 'T03:0' in time_str or ('T03:1' in time_str and time_str.split('T03:1')[1][0] in '0123'):
        early_morning_posts.append(time_str)

print('Original createdTime values for Bengaluru Traffic Police posts between 3:00-3:14 AM:')
for time in early_morning_posts:
    print(time)
