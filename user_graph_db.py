# from pymongo import MongoClient
# from typing import List, Set, Dict, Optional

# # --- MongoDB Setup ---
# MONGO_URI = "mongodb://localhost:27017/"
# client = MongoClient("mongodb+srv://purabray2:Ray2005@cluster0.xrjmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = client["social_app"]
# profiles_col = db["profiles"]     # { username, bio, tastes:list[str] }
# friends_col = db["friendships"]   # { username, friends:list[str] }

# # --- DSU for Taste Clusters --- #
# class DSU:
#     def __init__(self):
#         self.parent: Dict[str, str] = {}

#     def find(self, x: str) -> str:
#         if x not in self.parent:
#             self.parent[x] = x
#         if self.parent[x] != x:
#             self.parent[x] = self.find(self.parent[x])
#         return self.parent[x]

#     def union(self, x: str, y: str):
#         rx, ry = self.find(x), self.find(y)
#         if rx != ry:
#             self.parent[rx] = ry

#     def cluster_members(self, taste_list: List[str]) -> Set[str]:
#         roots = {self.find(t) for t in taste_list}
#         return {t for t in self.parent if self.find(t) in roots}

# # --- In-memory Graph Logic --- #
# class Graph:
#     def __init__(self):
#         self.adj: Dict[str, Set[str]] = {}
#         self.profile: Dict[str, Dict] = {}
#         self.taste_list = [
#             "Rock Music", "Classical Music", "Hip-Hop", "Jazz",
#             "Football", "Basketball", "Cricket", "Badminton",
#             "Science Fiction", "Fantasy", "Mystery", "Romance",
#             "Coding", "Gaming", "Cooking", "Travel"
#         ]
#         self.taste_dsu = DSU()

#     # DSU rebuild
#     def _rebuild_taste_dsu(self):
#         self.taste_dsu = DSU()
#         for t in self.taste_list:
#             self.taste_dsu.find(t)
#         for p in self.profile.values():
#             ts = p["tastes"]
#             if len(ts) > 1:
#                 for i in range(1, len(ts)):
#                     self.taste_dsu.union(ts[0], ts[i])

#     # Taste-cluster users
#     def users_in_same_taste_cluster(self, user: str) -> Set[str]:
#         if user not in self.profile: return set()
#         ut = self.profile[user]["tastes"]
#         if not ut: return set()
#         ct = self.taste_dsu.cluster_members(ut)
#         return {
#             o for o,p in self.profile.items()
#             if o!=user and set(p["tastes"]) & ct
#         }

#     # CRUD
#     def add_user(self, user: str, bio: str, tastes: List[str]):
#         user = user.strip()
#         if not user or user in self.adj: return
#         self.adj[user] = set()
#         self.profile[user] = {"bio": bio, "tastes": tastes}
#         self._rebuild_taste_dsu()

#     def edit_profile(self, user: str, bio: str, tastes: List[str]):
#         if user not in self.profile: return
#         self.profile[user] = {"bio": bio, "tastes": tastes}
#         self._rebuild_taste_dsu()

#     def remove_user(self, user: str):
#         if user in self.adj:
#             for f in list(self.adj[user]):
#                 self.adj[f].remove(user)
#             del self.adj[user]
#         if user in self.profile:
#             del self.profile[user]
#         self._rebuild_taste_dsu()

#     def add_friendship(self, u: str, v: str):
#         if u==v: return
#         for x in (u,v):
#             if x not in self.adj:
#                 self.add_user(x, "", [])
#         self.adj[u].add(v)
#         self.adj[v].add(u)

#     def remove_friendship(self, u: str, v: str):
#         if u in self.adj and v in self.adj[u]:
#             self.adj[u].remove(v)
#             self.adj[v].remove(u)

#     # BFS shortest path
#     def bfs_shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
#         if src not in self.adj or dst not in self.adj: return None
#         if src==dst: return [src]
#         from collections import deque
#         q = deque([src]); parent={src:None}
#         while q:
#             n=q.popleft()
#             for nei in self.adj[n]:
#                 if nei not in parent:
#                     parent[nei]=n
#                     if nei==dst:
#                         return self._recon(parent,dst)
#                     q.append(nei)
#         return None

#     def _recon(self,parent,node):
#         p=[] 
#         while node is not None:
#             p.append(node); node=parent[node]
#         return p[::-1]

#     def mutual_friends(self,u,v) -> Set[str]:
#         if u not in self.adj or v not in self.adj: return set()
#         return self.adj[u] & self.adj[v]

#     def recommend_friends(self,u:str) -> List[tuple]:
#         if u not in self.adj: return []
#         direct=self.adj[u]
#         ut=set(self.profile[u]["tastes"])
#         # FoF
#         fof=set()
#         for f in direct: fof |= self.adj[f]
#         fof.discard(u); fof-=direct
#         # Cluster users
#         cu=self.users_in_same_taste_cluster(u)
#         # Count shared tastes
#         sc={}
#         for other in cu|fof:
#             if other==u: continue
#             shared=len(ut & set(self.profile[other]["tastes"]))
#             sc[other]=shared
#         # Buckets
#         both=sorted(cu&fof, key=lambda x:(-sc.get(x,0),x))
#         clo=sorted(cu-{*both}-direct, key=lambda x:(-sc.get(x,0),x))
#         fofo=sorted(fof-{*both}, key=lambda x:(-sc.get(x,0),x))
#         return ([(n,2,sc[n]) for n in both]
#               +[(n,1,sc[n]) for n in clo]
#               +[(n,0,sc[n]) for n in fofo])

#     def adjacency_list(self) -> Dict[str,List[str]]:
#         return {u:sorted(v) for u,v in self.adj.items()}

#     def connected_components(self) -> List[Set[str]]:
#         vis=set(); comps=[]
#         def dfs(n,c):
#             vis.add(n); c.add(n)
#             for nei in self.adj[n]:
#                 if nei not in vis: dfs(nei,c)
#         for node in self.adj:
#             if node not in vis:
#                 c=set(); dfs(node,c); comps.append(c)
#         return comps

#     def get_profile(self,u:str):
#         return self.profile.get(u,{"bio":"","tastes":[]})

# # --- DB ↔ Graph Persistence --- #
# def load_graph_from_db() -> Graph:
#     g=Graph()
#     # load profiles
#     for doc in profiles_col.find():
#         g.add_user(doc["username"], doc["bio"], doc["tastes"])
#     # load friendships
#     for doc in friends_col.find():
#         g.adj[doc["username"]] = set(doc["friends"])
#     return g

# def save_user(user: str, bio: str, tastes: List[str]):
#     profiles_col.update_one(
#         {"username":user},
#         {"$set":{"bio":bio,"tastes":tastes}},
#         upsert=True
#     )

# def save_friends(user: str, friends: List[str]):
#     friends_col.update_one(
#         {"username":user},
#         {"$set":{"friends":friends}},
#         upsert=True
#     )

# def persist_graph(g: Graph):
#     # overwrite all
#     for u,p in g.profile.items():
#         save_user(u,p["bio"],p["tastes"])
#     for u,fr in g.adj.items():
#         save_friends(u,list(fr))

# # Added functions to fetch raw data for caching
# def load_profiles():
#     return list(profiles_col.find())

# def load_friendships():
#     return list(friends_col.find())

from pymongo import MongoClient
from typing import List, Set, Dict, Optional

# --- MongoDB Setup ---
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient("mongodb+srv://purabray2:Ray2005@cluster0.xrjmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["social_app"]
profiles_col = db["profiles"]     # { username, bio, tastes:list[str], password }
friends_col = db["friendships"]   # { username, friends:list[str] }

# --- DSU for Taste Clusters --- #
class DSU:
    def __init__(self):
        self.parent: Dict[str, str] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry

    def cluster_members(self, taste_list: List[str]) -> Set[str]:
        roots = {self.find(t) for t in taste_list}
        return {t for t in self.parent if self.find(t) in roots}

# --- In-memory Graph Logic --- #
class Graph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        self.profile: Dict[str, Dict] = {}
        self.taste_list = [
            "Rock Music", "Classical Music", "Hip-Hop", "Jazz",
            "Football", "Basketball", "Cricket", "Badminton",
            "Science Fiction", "Fantasy", "Mystery", "Romance",
            "Coding", "Gaming", "Cooking", "Travel"
        ]
        self.taste_dsu = DSU()

    # DSU rebuild
    def _rebuild_taste_dsu(self):
        self.taste_dsu = DSU()
        for t in self.taste_list:
            self.taste_dsu.find(t)
        for p in self.profile.values():
            ts = p["tastes"]
            if len(ts) > 1:
                for i in range(1, len(ts)):
                    self.taste_dsu.union(ts[0], ts[i])

    # Taste-cluster users
    def users_in_same_taste_cluster(self, user: str) -> Set[str]:
        if user not in self.profile: return set()
        ut = self.profile[user]["tastes"]
        if not ut: return set()
        ct = self.taste_dsu.cluster_members(ut)
        return {
            o for o,p in self.profile.items()
            if o!=user and set(p["tastes"]) & ct
        }

    # CRUD
    def add_user(self, user: str, bio: str, tastes: List[str], password: str = ""):
        user = user.strip()
        if not user or user in self.adj: return
        self.adj[user] = set()
        self.profile[user] = {"bio": bio, "tastes": tastes, "password": password}
        self._rebuild_taste_dsu()

    def edit_profile(self, user: str, bio: str, tastes: List[str], password: str = None):
        if user not in self.profile: return
        self.profile[user]["bio"] = bio
        self.profile[user]["tastes"] = tastes
        if password is not None:
            self.profile[user]["password"] = password
        self._rebuild_taste_dsu()

    def remove_user(self, user: str):
        if user in self.adj:
            for f in list(self.adj[user]):
                self.adj[f].remove(user)
            del self.adj[user]
        if user in self.profile:
            del self.profile[user]
        self._rebuild_taste_dsu()

    def add_friendship(self, u: str, v: str):
        if u==v: return
        for x in (u,v):
            if x not in self.adj:
                self.add_user(x, "", [])
        self.adj[u].add(v)
        self.adj[v].add(u)

    def remove_friendship(self, u: str, v: str):
        if u in self.adj and v in self.adj[u]:
            self.adj[u].remove(v)
            self.adj[v].remove(u)

    # BFS shortest path
    def bfs_shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
        if src not in self.adj or dst not in self.adj: return None
        if src==dst: return [src]
        from collections import deque
        q = deque([src]); parent={src:None}
        while q:
            n=q.popleft()
            for nei in self.adj[n]:
                if nei not in parent:
                    parent[nei]=n
                    if nei==dst:
                        return self._recon(parent,dst)
                    q.append(nei)
        return None

    def _recon(self,parent,node):
        p=[]
        while node is not None:
            p.append(node); node=parent[node]
        return p[::-1]

    def mutual_friends(self,u,v) -> Set[str]:
        if u not in self.adj or v not in self.adj: return set()
        return self.adj[u] & self.adj[v]

    def recommend_friends(self,u:str) -> List[tuple]:
        if u not in self.adj: return []
        direct=self.adj[u]
        ut=set(self.profile[u]["tastes"])
        # FoF
        fof=set()
        for f in direct: fof |= self.adj[f]
        fof.discard(u); fof-=direct
        # Cluster users
        cu=self.users_in_same_taste_cluster(u)
        # Count shared tastes
        sc={}
        for other in cu|fof:
            if other==u: continue
            shared=len(ut & set(self.profile[other]["tastes"]))
            sc[other]=shared
        # Buckets
        both=sorted(cu&fof, key=lambda x:(-sc.get(x,0),x))
        clo=sorted(cu-{*both}-direct, key=lambda x:(-sc.get(x,0),x))
        fofo=sorted(fof-{*both}, key=lambda x:(-sc.get(x,0),x))
        return ([(n,2,sc[n]) for n in both]
              +[(n,1,sc[n]) for n in clo]
              +[(n,0,sc[n]) for n in fofo])

    def adjacency_list(self) -> Dict[str,List[str]]:
        return {u:sorted(v) for u,v in self.adj.items()}

    def connected_components(self) -> List[Set[str]]:
        vis=set(); comps=[]
        def dfs(n,c):
            vis.add(n); c.add(n)
            for nei in self.adj[n]:
                if nei not in vis: dfs(nei,c)
        for node in self.adj:
            if node not in vis:
                c=set(); dfs(node,c); comps.append(c)
        return comps

    def get_profile(self,u:str):
        return self.profile.get(u,{"bio":"","tastes":[],"password":""})

# --- DB ↔ Graph Persistence --- #
def load_graph_from_db() -> Graph:
    g=Graph()
    # load profiles (with password)
    for doc in profiles_col.find():
        g.add_user(doc["username"], doc["bio"], doc["tastes"], password=doc.get("password",""))
    # load friendships
    for doc in friends_col.find():
        g.adj[doc["username"]] = set(doc["friends"])
    return g

def save_user(user: str, bio: str, tastes: list, password: str = ""):
    profiles_col.update_one(
        {"username":user},
        {"$set":{
            "bio":bio,
            "tastes":tastes,
            "password":password
        }},
        upsert=True
    )

def save_friends(user: str, friends: list):
    friends_col.update_one(
        {"username":user},
        {"$set":{"friends":friends}},
        upsert=True
    )

def persist_graph(g: Graph):
    for u, p in g.profile.items():
        save_user(u, p["bio"], p["tastes"], p.get("password",""))
    for u,fr in g.adj.items():
        save_friends(u, list(fr))

def load_profiles():
    return list(profiles_col.find())

def load_friendships():
    return list(friends_col.find())
