# recommender.py - Complete Recommendation Module (Optimized)
# Algorithms: Collaborative Filtering, Personalized PageRank, Hybrid (CF + PPR)
import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class MovieRecommender:
    """Movie recommendation system with multiple algorithms"""
    
    def __init__(self, data_path="data/processed/"):
        """
        Initialize the recommender and load graph once (cached)
        
        Args:
            data_path: Path to processed CSV files
        """
        self.data_path = Path(data_path)
        self.G = None
        self.movies_df = None
        self._load_data()
        self._build_graph()
        
    def _load_data(self):
        """Load CSV files from data/processed folder"""
        print("Loading data...")
        
        edges_path = self.data_path / "edges.csv"
        movies_path = self.data_path / "movies_clean.csv"
        ratings_path = self.data_path / "ratings_clean.csv"
        
        self.edges_df = pd.read_csv(edges_path)
        self.movies_df = pd.read_csv(movies_path)
        self.ratings_df = pd.read_csv(ratings_path)
        
        print(f"  - Loaded {len(self.edges_df):,} edges")
        print(f"  - Loaded {len(self.movies_df):,} movies")
        print(f"  - Loaded {len(self.ratings_df):,} ratings")
    
    def _build_graph(self):
        """Build bipartite graph from edges data"""
        print("Building graph...")
        
        self.G = nx.Graph()
        
        if 'userId' in self.edges_df.columns:
            user_col = 'userId'
            movie_col = 'movieId'
        else:
            user_col = 'user_id'
            movie_col = 'movie_id'
        
        for _, row in self.edges_df.iterrows():
            user_node = f"U{row[user_col]}"
            movie_node = f"M{row[movie_col]}"
            
            if user_node not in self.G:
                self.G.add_node(user_node, bipartite=0, type='user')
            
            if movie_node not in self.G:
                movie_info = self.movies_df[self.movies_df['movieId'] == row[movie_col]]
                title = movie_info['title'].values[0] if not movie_info.empty else f"Movie_{row[movie_col]}"
                self.G.add_node(movie_node, bipartite=1, type='movie', title=title)
            
            rating_row = self.ratings_df[
                (self.ratings_df['userId'] == row[user_col]) & 
                (self.ratings_df['movieId'] == row[movie_col])
            ]
            
            weight = rating_row['rating'].values[0] if not rating_row.empty else 1.0
            self.G.add_edge(user_node, movie_node, weight=weight)
        
        print(f"  - Graph built: {self.G.number_of_nodes():,} nodes, {self.G.number_of_edges():,} edges")
    
    # ==================== ALGORITHM 1: COLLABORATIVE FILTERING ====================
    
    def recommend_cf(self, user_id, top_n=10, min_similar_users=2):
        """
        Collaborative Filtering via Graph Neighborhood
        Returns movies based on similar users' preferences
        """
        user_node = f"U{user_id}"
        
        if user_node not in self.G:
            return []
        
        # Get watched movies
        watched_movies = set()
        for neighbor in self.G.neighbors(user_node):
            if self.G.nodes[neighbor].get('type') == 'movie':
                watched_movies.add(neighbor)
        
        # Find similar users
        similar_users = {}
        for movie in watched_movies:
            for neighbor in self.G.neighbors(movie):
                if self.G.nodes[neighbor].get('type') == 'user' and neighbor != user_node:
                    edge_weight = self.G[neighbor][movie].get('weight', 1.0)
                    similar_users[neighbor] = similar_users.get(neighbor, 0) + edge_weight
        
        similar_users = {u: score for u, score in similar_users.items() if score >= min_similar_users}
        
        # Get recommendations
        recommendations = {}
        for similar_user in similar_users.keys():
            for movie in self.G.neighbors(similar_user):
                if (self.G.nodes[movie].get('type') == 'movie' and movie not in watched_movies):
                    edge_weight = self.G[similar_user][movie].get('weight', 1.0)
                    
                    if movie in recommendations:
                        recommendations[movie]['score'] += edge_weight
                        recommendations[movie]['similar_users'].append(similar_user)
                        recommendations[movie]['count'] += 1
                    else:
                        recommendations[movie] = {
                            'score': edge_weight,
                            'similar_users': [similar_user],
                            'title': self.G.nodes[movie].get('title', movie),
                            'count': 1
                        }
        
        # Sort by average score
        sorted_recs = sorted(recommendations.items(), 
                            key=lambda x: x[1]['score'] / x[1]['count'], 
                            reverse=True)[:top_n]
        
        # Format output
        results = []
        for movie_node, data in sorted_recs:
            movie_id = int(movie_node.replace('M', ''))
            num_users = len(data['similar_users'])
            avg_score = data['score'] / data['count'] if data['count'] > 0 else data['score']
            reason = f"Recommended by {num_users} similar user" + ("s" if num_users != 1 else "")
            reason += f" (avg rating {avg_score:.1f})"
            
            results.append({
                "movie_id": movie_id,
                "title": data['title'],
                "score": round(avg_score, 2),
                "reasons": reason,
                "algorithm": "collaborative_filtering"
            })
        
        return results
    
    # ==================== ALGORITHM 2: PERSONALIZED PAGERANK ====================
    
    def recommend_pagerank(self, user_id, top_n=10, alpha=0.85):
        """
        Personalized PageRank algorithm
        Ranks movies by probability of reaching them from the user node
        """
        user_node = f"U{user_id}"
        
        if user_node not in self.G:
            return []
        
        # Get watched movies to exclude
        watched_movies = set()
        for neighbor in self.G.neighbors(user_node):
            if self.G.nodes[neighbor].get('type') == 'movie':
                watched_movies.add(neighbor)
        
        # Create personalization dict (user node gets high initial weight)
        personalization = {node: 0 for node in self.G.nodes()}
        personalization[user_node] = 1
        
        try:
            # Run personalized PageRank
            ppr = nx.pagerank(self.G, alpha=alpha, personalization=personalization)
        except:
            # Fallback for older networkx version
            ppr = nx.pagerank(self.G, alpha=alpha)
        
        # Filter movie nodes not watched
        movie_scores = []
        for node, score in ppr.items():
            if node.startswith('M') and node not in watched_movies:
                movie_id = int(node.replace('M', ''))
                title = self.G.nodes[node].get('title', node)
                movie_scores.append((movie_id, title, score))
        
        # Sort and return top N
        movie_scores.sort(key=lambda x: x[2], reverse=True)
        
        results = []
        for movie_id, title, score in movie_scores[:top_n]:
            results.append({
                "movie_id": movie_id,
                "title": title,
                "score": round(score, 6),
                "reasons": f"Personalized PageRank (alpha={alpha})",
                "algorithm": "pagerank"
            })
        
        return results

    # ==================== ALGORITHM 3: HYBRID RECOMMENDER  ====================
    
    def recommend_hybrid(self, user_id, top_n=10, cf_weight=0.5, ppr_weight=0.5):
        """
        Hybrid recommender combining CF and PageRank with proper normalization
        Both algorithms contribute equally to final recommendations
        """
        # Get recommendations from each algorithm (get more for better mixing)
        cf_recs = self.recommend_cf(user_id, top_n=top_n * 3)
        ppr_recs = self.recommend_pagerank(user_id, top_n=top_n * 3)
        
        # Create dictionaries for scores
        cf_scores = {rec['movie_id']: rec['score'] for rec in cf_recs}
        ppr_scores = {rec['movie_id']: rec['score'] for rec in ppr_recs}
        
        # Get all titles
        titles = {}
        for rec in cf_recs + ppr_recs:
            titles[rec['movie_id']] = rec['title']
        
        # Normalize CF scores to 0-1 scale
        if cf_scores:
            cf_min = min(cf_scores.values())
            cf_max = max(cf_scores.values())
            if cf_max > cf_min:
                cf_norm = {mid: (score - cf_min) / (cf_max - cf_min) for mid, score in cf_scores.items()}
            else:
                cf_norm = {mid: 0.5 for mid in cf_scores}
        else:
            cf_norm = {}
        
        # Normalize PageRank scores to 0-1 scale
        if ppr_scores:
            ppr_min = min(ppr_scores.values())
            ppr_max = max(ppr_scores.values())
            if ppr_max > ppr_min:
                ppr_norm = {mid: (score - ppr_min) / (ppr_max - ppr_min) for mid, score in ppr_scores.items()}
            else:
                ppr_norm = {mid: 0.5 for mid in ppr_scores}
        else:
            ppr_norm = {}
        
        # Combine all unique movie IDs
        all_movies = set(cf_norm.keys()) | set(ppr_norm.keys())
        
        # Calculate weighted scores
        combined = {}
        for movie_id in all_movies:
            cf_score = cf_norm.get(movie_id, 0) * cf_weight
            ppr_score = ppr_norm.get(movie_id, 0) * ppr_weight
            total_score = cf_score + ppr_score
            
            # Track which algorithms contributed
            algos = []
            if movie_id in cf_norm:
                algos.append('CF')
            if movie_id in ppr_norm:
                algos.append('PageRank')
            
            combined[movie_id] = {
                'title': titles.get(movie_id, f"Movie_{movie_id}"),
                'score': total_score,
                'algorithms': algos
            }
        
        # Sort by score and return top N
        sorted_recs = sorted(combined.items(), key=lambda x: x[1]['score'], reverse=True)[:top_n]
        
        results = []
        for movie_id, data in sorted_recs:
            results.append({
                "movie_id": movie_id,
                "title": data['title'],
                "score": round(data['score'], 4),
                "reasons": f"Hybrid: {' + '.join(data['algorithms'])}",
                "algorithm": "hybrid"
            })
        
        return results
    
    # ==================== MAIN RECOMMENDATION METHOD ====================
    
    def get_recommendations(self, user_id, top_n=10, algorithm="cf"):
        """
        Main recommendation method - supports multiple algorithms
        
        Args:
            user_id: User ID (1-610)
            top_n: Number of recommendations
            algorithm: One of 'cf', 'pagerank', 'hybrid'
        
        Returns:
            List of recommendations
        """
        algorithm = algorithm.lower()
        
        if algorithm == "cf" or algorithm == "collaborative_filtering":
            return self.recommend_cf(user_id, top_n)
        elif algorithm == "pagerank" or algorithm == "ppr":
            return self.recommend_pagerank(user_id, top_n)
        elif algorithm == "hybrid":
            return self.recommend_hybrid(user_id, top_n)
        else:
            return self.recommend_cf(user_id, top_n)
    
    def get_user_watched_movies(self, user_id):
        """Get list of movies a user has watched"""
        user_node = f"U{user_id}"
        
        if user_node not in self.G:
            return []
        
        watched = []
        for neighbor in self.G.neighbors(user_node):
            if self.G.nodes[neighbor].get('type') == 'movie':
                movie_id = int(neighbor.replace('M', ''))
                title = self.G.nodes[neighbor].get('title', neighbor)
                
                # Get rating if available
                rating = self.G[user_node][neighbor].get('weight', 1.0)
                
                watched.append({
                    "movie_id": movie_id, 
                    "title": title,
                    "rating": rating
                })
        
        return watched
    
    def compare_algorithms(self, user_id, top_n=10):
        """
        Compare all algorithms and return benchmark results
        """
        import time
        
        results = {}
        
        # Test CF
        start = time.time()
        cf_recs = self.recommend_cf(user_id, top_n)
        results['collaborative_filtering'] = {
            'time': round(time.time() - start, 4),
            'count': len(cf_recs),
            'sample': cf_recs[:2] if cf_recs else []
        }
        
        # Test PageRank
        start = time.time()
        ppr_recs = self.recommend_pagerank(user_id, top_n)
        results['pagerank'] = {
            'time': round(time.time() - start, 4),
            'count': len(ppr_recs),
            'sample': ppr_recs[:2] if ppr_recs else []
        }
        
        # Test Hybrid
        start = time.time()
        hybrid_recs = self.recommend_hybrid(user_id, top_n)
        results['hybrid'] = {
            'time': round(time.time() - start, 4),
            'count': len(hybrid_recs),
            'sample': hybrid_recs[:2] if hybrid_recs else []
        }
        
        return results


# ==================== SINGLETON INSTANCE ====================

_recommender_instance = None

def get_recommender():
    """Get singleton recommender instance (cached in memory)"""
    global _recommender_instance
    if _recommender_instance is None:
        project_root = Path(__file__).parent.parent.parent
        data_path = project_root / "data" / "processed"
        _recommender_instance = MovieRecommender(data_path)
    return _recommender_instance


# ==================== TEST FUNCTIONS ====================

def test_all_algorithms():
    """Test all recommendation algorithms"""
    rec = get_recommender()
    
    print("\n" + "=" * 70)
    print("COMPLETE ALGORITHM TEST - USER 1")
    print("=" * 70)
    
    # Test CF
    print("\n1. COLLABORATIVE FILTERING:")
    print("-" * 50)
    cf_recs = rec.recommend_cf(1, top_n=5)
    for i, r in enumerate(cf_recs, 1):
        print(f"   {i}. {r['title']} (Score: {r['score']})")
        print(f"      {r['reasons']}")
    
    # Test PageRank
    print("\n2. PERSONALIZED PAGERANK:")
    print("-" * 50)
    ppr_recs = rec.recommend_pagerank(1, top_n=5)
    for i, r in enumerate(ppr_recs, 1):
        print(f"   {i}. {r['title']} (Score: {r['score']})")
        print(f"      {r['reasons']}")
    
    # Test Hybrid
    print("\n3. HYBRID (CF + PageRank):")
    print("-" * 50)
    hybrid_recs = rec.recommend_hybrid(1, top_n=5)
    for i, r in enumerate(hybrid_recs, 1):
        print(f"   {i}. {r['title']} (Score: {r['score']})")
        print(f"      {r['reasons']}")
    
    return cf_recs, ppr_recs, hybrid_recs


def test_benchmark():
    """Run benchmark comparing all algorithms"""
    rec = get_recommender()
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPARISON")
    print("=" * 70)
    
    benchmark = rec.compare_algorithms(1, top_n=10)
    
    print("\n| Algorithm | Time (seconds) | Recommendations |")
    print("|-----------|---------------|-----------------|")
    for algo, data in benchmark.items():
        print(f"| {algo:20} | {data['time']:12} | {data['count']:15} |")
    
    return benchmark


def test_performance():
    """Test performance for multiple users"""
    import time
    
    rec = get_recommender()
    test_users = [1, 5, 10, 15, 20]
    
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST - MULTIPLE USERS")
    print("=" * 70)
    
    print("\n| User | CF (s) | PageRank (s) | Hybrid (s) |")
    print("|------|--------|--------------|------------|")
    
    for user_id in test_users:
        # Test CF
        start = time.time()
        rec.recommend_cf(user_id, top_n=10)
        cf_time = time.time() - start
        
        # Test PageRank
        start = time.time()
        rec.recommend_pagerank(user_id, top_n=10)
        ppr_time = time.time() - start
        
        # Test Hybrid
        start = time.time()
        rec.recommend_hybrid(user_id, top_n=10)
        hybrid_time = time.time() - start
        
        print(f"| {user_id:4} | {cf_time:.4f} | {ppr_time:.4f} | {hybrid_time:.4f} |")


def test_user_watched(user_id=1):
    """Test getting watched movies for a user"""
    rec = get_recommender()
    
    print("\n" + "=" * 70)
    print(f"WATCHED MOVIES FOR USER {user_id}")
    print("=" * 70)
    
    watched = rec.get_user_watched_movies(user_id)
    
    for i, movie in enumerate(watched[:10], 1):
        print(f"   {i}. {movie['title']} (Rating: {movie['rating']})")
    
    print(f"\n   Total: {len(watched)} movies watched")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MOVIE RECOMMENDATION SYSTEM")
    print("Algorithms: CF | PageRank | Hybrid")
    print("=" * 70)
    
    # Run all tests
    test_all_algorithms()
    test_benchmark()
    test_performance()
    test_user_watched(1)
    
    print("\n" + "=" * 70)
    print("✅ ALL ALGORITHMS COMPLETE AND READY FOR BACKEND")
    print("=" * 70)
    print("\nUsage in backend:")
    print("  from src.algorithms.recommender import get_recommender")
    print("  rec = get_recommender()")
    print("  rec.get_recommendations(1, algorithm='cf')")
    print("  rec.get_recommendations(1, algorithm='pagerank')")
    print("  rec.get_recommendations(1, algorithm='hybrid')")