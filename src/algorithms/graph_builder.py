# graph_builder.py - UPDATED FOR CORRECT COLUMN NAMES
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import os

print("=" * 60)
print("MOVIE RECOMMENDATION SYSTEM - GRAPH CONSTRUCTION")
print("=" * 60)

# Step 1: Load the data
print("\n1. Loading data files...")
start_time = time.time()

try:
    edges = pd.read_csv('edges.csv')
    movies = pd.read_csv('movies_clean.csv')
    load_time = time.time() - start_time
    
    print(f"   [OK] Successfully loaded in {load_time:.2f} seconds")
    print(f"   - edges.csv: {len(edges):,} user-movie connections")
    print(f"   - movies_clean.csv: {len(movies):,} movies")
    
    # SHOW ACTUAL COLUMN NAMES
    print(f"\n   Actual columns in edges.csv: {edges.columns.tolist()}")
    print(f"   Actual columns in movies_clean.csv: {movies.columns.tolist()}")
    
except FileNotFoundError as e:
    print(f"   [ERROR] {e}")
    print("   Make sure files are in the same folder as this script!")
    print("   Current files:", [f for f in os.listdir('.') if f.endswith('.csv')])
    exit()

# Step 2: Show data structure
print("\n2. Data structure analysis:")
print(f"   Edges columns: {edges.columns.tolist()}")
print(f"   Movies columns: {movies.columns.tolist()}")

# Show sample of edges
print("\n   First 3 edges:")
print(edges.head(3))

# Step 3: Build the graph (SAMPLE - first 5000 edges for speed)
print("\n3. Building bipartite graph (using first 5000 edges for speed)...")
graph_start = time.time()

# Create empty graph
G = nx.Graph()

# Take smaller sample for development
edges_sample = edges.head(5000)

print("   Adding users and movies as nodes...")

# Check which column names we actually have
print(f"   Detected columns: {edges_sample.columns.tolist()}")

# Use correct column names based on what we have
if 'userId' in edges_sample.columns and 'movieId' in edges_sample.columns:
    user_col = 'userId'
    movie_col = 'movieId'
elif 'user_id' in edges_sample.columns and 'movie_id' in edges_sample.columns:
    user_col = 'user_id'
    movie_col = 'movie_id'
else:
    print("   [ERROR] Could not find user and movie columns!")
    print(f"   Available columns: {edges_sample.columns.tolist()}")
    exit()

for _, row in edges_sample.iterrows():
    user_node = f"U{row[user_col]}"
    movie_node = f"M{row[movie_col]}"
    
    # Add nodes with attributes
    if user_node not in G:
        G.add_node(user_node, bipartite=0, type='user')
    if movie_node not in G:
        # Get movie title if available
        # Check movie ID column name in movies dataframe
        movie_id_col = 'movieId' if 'movieId' in movies.columns else 'movie_id'
        movie_info = movies[movies[movie_id_col] == row[movie_col]]
        title = movie_info['title'].values[0] if not movie_info.empty else f"Movie_{row[movie_col]}"
        G.add_node(movie_node, bipartite=1, type='movie', title=title)
    
    # Add edge (check if weight column exists)
    if 'weight' in edges_sample.columns:
        weight = row['weight']
        G.add_edge(user_node, movie_node, weight=weight)
    else:
        G.add_edge(user_node, movie_node)

graph_time = time.time() - graph_start
print(f"   [OK] Graph built in {graph_time:.2f} seconds")
print(f"   - Total nodes: {G.number_of_nodes():,}")
print(f"   - Total edges: {G.number_of_edges():,}")

# Count user and movie nodes
user_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'user']
movie_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'movie']
print(f"   - User nodes: {len(user_nodes)}")
print(f"   - Movie nodes: {len(movie_nodes)}")

# Step 4: Calculate basic graph metrics
print("\n4. Graph metrics:")
print(f"   Is bipartite: {nx.is_bipartite(G)}")

# Step 5: Create and save visualization
print("\n5. Creating visualization...")
try:
    # Create a small subgraph for visualization (first 2 users + their movies)
    user_nodes_sample = user_nodes[:3]  # Take 3 users
    movie_nodes_sample = []
    for user in user_nodes_sample:
        user_movies = [n for n in G.neighbors(user) if n in movie_nodes]
        movie_nodes_sample.extend(user_movies[:5])  # Take first 5 movies per user
    
    # Remove duplicates and limit
    movie_nodes_sample = list(set(movie_nodes_sample))[:15]
    sample_nodes = user_nodes_sample + movie_nodes_sample
    sample_graph = G.subgraph(sample_nodes)
    
    # Draw
    plt.figure(figsize=(12, 8))
    
    # Position nodes: users on left, movies on right
    pos = {}
    
    # Position users (left side)
    for i, user in enumerate(user_nodes_sample):
        pos[user] = (0, i * 3)
    
    # Position movies (right side, staggered)
    for i, movie in enumerate(movie_nodes_sample):
        pos[movie] = (1, i * 1.5)
    
    # Draw nodes with different colors
    nx.draw_networkx_nodes(sample_graph, pos, nodelist=user_nodes_sample, 
                          node_color='lightblue', node_size=800, 
                          edgecolors='darkblue', linewidths=2, label='Users')
    nx.draw_networkx_nodes(sample_graph, pos, nodelist=movie_nodes_sample, 
                          node_color='lightgreen', node_size=600,
                          edgecolors='darkgreen', linewidths=2, label='Movies')
    
    # Draw edges
    nx.draw_networkx_edges(sample_graph, pos, width=1.5, alpha=0.7, edge_color='gray')
    
    # Add labels
    labels = {}
    for node in sample_graph.nodes():
        if node in user_nodes_sample:
            labels[node] = node.replace('U', 'User ')
        else:
            # Get shortened movie title
            title = sample_graph.nodes[node].get('title', node)
            # Extract year if present
            import re
            match = re.search(r'(.+?)\(\d{4}\)', title)
            if match:
                short_title = match.group(1).strip()
            else:
                short_title = title
            # Truncate if too long
            if len(short_title) > 20:
                short_title = short_title[:17] + "..."
            labels[node] = short_title
    
    nx.draw_networkx_labels(sample_graph, pos, labels, font_size=9, font_weight='bold')
    
    plt.title("Sample User-Movie Bipartite Graph", fontsize=14, fontweight='bold')
    plt.legend(loc='upper left')
    plt.axis('off')
    
    # Add grid lines for better visualization
    plt.grid(True, alpha=0.3, linestyle='--', which='both')
    
    # Save
    plt.savefig('graph_sample.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("   [OK] Visualization saved as 'graph_sample.png'")
    
    # Also show the image
    plt.show()
    
except Exception as e:
    print(f"   [NOTE] Visualization issue: {e}")
    import traceback
    traceback.print_exc()

# Step 6: Generate sample recommendation
print("\n6. Sample recommendation test:")
if user_nodes:
    sample_user = user_nodes[0]
    user_movies = [n for n in G.neighbors(sample_user) if n in movie_nodes]
    
    print(f"   Testing user: {sample_user}")
    print(f"   Movies watched: {len(user_movies)}")
    
    if user_movies:
        print(f"   First 3 movies watched:")
        for i, movie in enumerate(user_movies[:3], 1):
            title = G.nodes[movie].get('title', movie)
            print(f"     {i}. {title}")
        
        # Simple collaborative filtering: find users with similar tastes
        print(f"\n   Finding similar users...")
        similar_users = set()
        for movie in user_movies[:2]:  # Check first 2 movies
            for neighbor in G.neighbors(movie):
                if G.nodes[neighbor]['type'] == 'user' and neighbor != sample_user:
                    similar_users.add(neighbor)
        
        print(f"   Found {len(similar_users)} users with similar tastes")
        
        # Get recommendations from similar users
        recommendations = {}
        for similar_user in list(similar_users)[:5]:  # Check first 5 similar users
            for movie in G.neighbors(similar_user):
                if (G.nodes[movie]['type'] == 'movie' and 
                    movie not in user_movies):
                    if movie in recommendations:
                        recommendations[movie] += 1
                    else:
                        recommendations[movie] = 1
        
        # Sort by frequency (most recommended first)
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n   Top 5 recommended movies:")
        for i, (movie, count) in enumerate(sorted_recs[:5], 1):
            title = G.nodes[movie].get('title', movie)
            print(f"     {i}. {title} (recommended by {count} similar users)")

print("\n" + "=" * 60)
print(" Graph construction and sample recommendations complete")
print("=" * 60)


# Additional metrics for report
print("\nADDITIONAL METRICS FOR REPORT:")
print(f"- Total possible user-movie pairs: {len(user_nodes)} * {len(movie_nodes)} = {len(user_nodes) * len(movie_nodes):,}")
print(f"- Actual connections (edges): {G.number_of_edges():,}")
print(f"- Graph density: {(G.number_of_edges() / (len(user_nodes) * len(movie_nodes))):.6f}")
print(f"- Average movies per user: {G.number_of_edges() / len(user_nodes):.2f}")
print(f"- Average users per movie: {G.number_of_edges() / len(movie_nodes):.2f}")