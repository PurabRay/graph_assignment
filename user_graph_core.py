# import streamlit as st
# from typing import List, Set, Dict, Optional

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
#         # Return all tastes in the same clusters as any in taste_list
#         roots = {self.find(t) for t in taste_list}
#         return {t for t in self.parent if self.find(t) in roots}

# # --- Graph + Profile --- #
# class Graph:
#     def __init__(self):
#         self.adj: Dict[str, Set[str]] = {}
#         self.profile: Dict[str, Dict] = {}  # {user: {bio, tastes}}
#         self.taste_list = [
#             "Rock Music", "Classical Music", "Hip-Hop", "Jazz",
#             "Football", "Basketball", "Cricket", "Badminton",
#             "Science Fiction", "Fantasy", "Mystery", "Romance",
#             "Coding", "Gaming", "Cooking", "Travel"
#         ]
#         self.taste_dsu = DSU()

#     # ---- DSU logic ---- #
#     def _rebuild_taste_dsu(self):
#         self.taste_dsu = DSU()
#         for taste in self.taste_list:
#             self.taste_dsu.find(taste)
#         for p in self.profile.values():
#             tastes = p["tastes"]
#             if len(tastes) > 1:
#                 for i in range(1, len(tastes)):
#                     self.taste_dsu.union(tastes[0], tastes[i])

#     def users_in_same_taste_cluster(self, user: str) -> Set[str]:
#         """All users sharing any transitive taste cluster with user (excluding direct self)."""
#         if user not in self.profile:
#             return set()
#         user_tastes = self.profile[user]["tastes"]
#         if not user_tastes:
#             return set()
#         cluster_tastes = self.taste_dsu.cluster_members(user_tastes)
#         users = set()
#         for other, prof in self.profile.items():
#             if other == user:
#                 continue
#             if set(prof["tastes"]) & cluster_tastes:
#                 users.add(other)
#         return users

#     # ---- CRUD ---- #
#     def add_user(self, user: str, bio: str, tastes: List[str]):
#         user = user.strip()
#         if not user or user in self.adj:
#             return
#         self.adj[user] = set()
#         self.profile[user] = {"bio": bio, "tastes": tastes}
#         self._rebuild_taste_dsu()

#     def edit_profile(self, user: str, bio: str, tastes: List[str]):
#         if user not in self.profile:
#             return
#         self.profile[user]["bio"] = bio
#         self.profile[user]["tastes"] = tastes
#         self._rebuild_taste_dsu()

#     def remove_user(self, user: str):
#         if user in self.adj:
#             for friend in list(self.adj[user]):
#                 self.adj[friend].remove(user)
#             del self.adj[user]
#         if user in self.profile:
#             del self.profile[user]
#         self._rebuild_taste_dsu()

#     def add_friendship(self, u: str, v: str):
#         if u == v:
#             return
#         for name in (u, v):
#             if name not in self.adj:
#                 self.add_user(name, "", [])
#         self.adj[u].add(v)
#         self.adj[v].add(u)

#     def remove_friendship(self, u: str, v: str):
#         if u in self.adj and v in self.adj[u]:
#             self.adj[u].remove(v)
#             self.adj[v].remove(u)

#     # ---- Graph Algorithms ---- #
#     def bfs_shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
#         if src not in self.adj or dst not in self.adj:
#             return None
#         if src == dst:
#             return [src]
#         from collections import deque
#         q = deque([src])
#         parent = {src: None}
#         while q:
#             node = q.popleft()
#             for nei in self.adj[node]:
#                 if nei not in parent:
#                     parent[nei] = node
#                     if nei == dst:
#                         return self._reconstruct(parent, dst)
#                     q.append(nei)
#         return None

#     def _reconstruct(self, parent, node):
#         path = []
#         while node is not None:
#             path.append(node)
#             node = parent[node]
#         return path[::-1]

#     def mutual_friends(self, u: str, v: str) -> Set[str]:
#         if u not in self.adj or v not in self.adj:
#             return set()
#         return self.adj[u] & self.adj[v]

#     def recommend_friends(self, u: str) -> List[tuple]:
#         if u not in self.adj:
#             return []
#         direct = self.adj[u]
#         user_tastes = set(self.profile[u]["tastes"])
#         # Friends-of-friends
#         fof = set()
#         for f in direct:
#             fof.update(self.adj[f])
#         fof.discard(u)
#         fof -= direct
#         # Users in any shared taste cluster
#         cluster_users = self.users_in_same_taste_cluster(u)
#         shared_taste_counts = {}
#         for other in cluster_users | fof:
#             if other == u: continue
#             shared = user_tastes & set(self.profile[other]["tastes"])
#             shared_taste_counts[other] = len(shared)
#         # Build buckets
#         both = [name for name in (cluster_users & fof)]
#         cluster_only = [name for name in (cluster_users - set(both) - direct)]
#         fof_only = [name for name in (fof - set(both))]
#         # Now sort each by shared taste count (desc), then name
#         both = sorted(both, key=lambda x: (-shared_taste_counts.get(x,0), x))
#         cluster_only = sorted(cluster_only, key=lambda x: (-shared_taste_counts.get(x,0), x))
#         fof_only = sorted(fof_only, key=lambda x: (-shared_taste_counts.get(x,0), x))
#         ranked = [(name, 2, shared_taste_counts.get(name,0)) for name in both] + \
#                  [(name, 1, shared_taste_counts.get(name,0)) for name in cluster_only] + \
#                  [(name, 0, shared_taste_counts.get(name,0)) for name in fof_only]
#         return ranked

#     def adjacency_list(self):
#         return {u: sorted(list(v)) for u, v in self.adj.items()}

#     def connected_components(self):
#         visited = set()
#         comps = []
#         def dfs(n, comp):
#             visited.add(n)
#             comp.add(n)
#             for nei in self.adj[n]:
#                 if nei not in visited:
#                     dfs(nei, comp)
#         for node in self.adj:
#             if node not in visited:
#                 comp = set()
#                 dfs(node, comp)
#                 comps.append(comp)
#         return comps

#     def get_profile(self, user):
#         return self.profile.get(user, {"bio": "", "tastes": []})

# # --- Streamlit App Logic --- #
# def init_state():
#     if "graph" not in st.session_state:
#         st.session_state.graph = Graph()

# def sidebar_user_ui():
#     g = st.session_state.graph
#     st.sidebar.header("Add New User")
#     uname = st.sidebar.text_input("Name", key="add_name")
#     bio = st.sidebar.text_area("Bio", key="add_bio")
#     tastes = st.sidebar.multiselect("Select at least 3 tastes", g.taste_list, key="add_tastes")
#     if st.sidebar.button("Add User"):
#         if not uname:
#             st.sidebar.error("Name required")
#         elif len(tastes) < 3:
#             st.sidebar.error("Select at least 3 tastes")
#         else:
#             g.add_user(uname, bio, tastes)
#             st.sidebar.success("User added")
#     st.sidebar.divider()
#     users = list(g.adj.keys())
#     rem = st.sidebar.selectbox("Remove User", ["-"] + users, key="rem_user")
#     if st.sidebar.button("Remove", key="rem_btn") and rem != "-":
#         g.remove_user(rem)
#         st.sidebar.warning(f"Removed {rem}")

# def sidebar_friendship_ui():
#     g = st.session_state.graph
#     st.sidebar.header("Friendships")
#     users = list(g.adj.keys())
#     if len(users) < 2:
#         st.sidebar.info("Need at least two users")
#         return
#     a = st.sidebar.selectbox("User A", users, key="fa")
#     b = st.sidebar.selectbox("User B", users, key="fb")
#     if st.sidebar.button("Add Friendship"):
#         g.add_friendship(a, b)
#         st.sidebar.success("Friendship added")
#     if st.sidebar.button("Remove Friendship"):
#         g.remove_friendship(a, b)
#         st.sidebar.warning("Friendship removed")

# def edit_profile_ui():
#     g = st.session_state.graph
#     st.header("Edit Profile")
#     users = list(g.adj.keys())
#     if not users:
#         st.info("No users yet")
#         return
#     u = st.selectbox("Select User", users, key="edit_sel")
#     p = g.get_profile(u)
#     bio = st.text_area("Bio", value=p["bio"], key="edit_bio")
#     tastes = st.multiselect("Tastes (≥3)", g.taste_list, default=p["tastes"], key="edit_tastes")
#     if st.button("Update Profile"):
#         if len(tastes) < 3:
#             st.error("Select at least 3 tastes")
#         else:
#             g.edit_profile(u, bio, tastes)
#             st.success("Updated")

# def analysis_ui():
#     g = st.session_state.graph
#     st.header("Network Analysis")
#     users = list(g.adj.keys())
#     if not users:
#         st.info("Add users first")
#         return

#     st.subheader("Shortest Path")
#     if len(users) >= 2:
#         s = st.selectbox("Source", users, key="sp_src")
#         d = st.selectbox("Destination", users, key="sp_dst")
#         if st.button("Find Path"):
#             path = g.bfs_shortest_path(s, d)
#             if path:
#                 st.success(" → ".join(path))
#             else:
#                 st.error("No connection")

#     st.subheader("Friend Recommendations")
#     u = st.selectbox("User", users, key="rec_user")
#     if st.button("Recommend"):
#         recs = g.recommend_friends(u)
#         if recs:
#             label = {2: "Taste cluster + FoF", 1: "Same taste cluster", 0: "Friends-of-friends"}
#             st.table([(name, label[code], f"{shared} shared tastes") for name, code, shared in recs])
#         else:
#             st.write("No recommendations")

#     st.subheader("Users in Same Taste Cluster")
#     if u:
#         group = sorted(g.users_in_same_taste_cluster(u))
#         st.write(group if group else "None")

#     st.subheader("Mutual Friends")
#     if len(users) >= 2:
#         x = st.selectbox("User 1", users, key="mf_x")
#         y = st.selectbox("User 2", users, key="mf_y")
#         if st.button("Find Mutual"):
#             st.write(sorted(g.mutual_friends(x, y)))

#     st.subheader("Popular Users (Most Friends)")
#     degrees = {u: len(g.adj[u]) for u in g.adj}
#     if degrees:
#         st.table(sorted(degrees.items(), key=lambda x: x[1], reverse=True))
#     else:
#         st.write("No users in network.")

#     st.subheader("Connected Components")
#     comps = g.connected_components()
#     st.write(f"Total components: {len(comps)}")
#     for idx, comp in enumerate(comps, 1):
#         st.write(f"Component {idx}: {', '.join(sorted(comp))}")

#     st.subheader("Adjacency List")
#     st.json(g.adjacency_list())

#     st.subheader("User Profiles")
#     for user in users:
#         profile = g.get_profile(user)
#         st.markdown(f"**{user}**\n\n_Bio_: {profile['bio']}\n\n_Tastes_: {', '.join(profile['tastes']) if profile['tastes'] else 'None'}")

# def main():
#     st.set_page_config(page_title="Social Network Friendship Finder", layout="wide")
#     init_state()
#     st.title("Social Network Friendship Finder (Chained Taste Clusters + Manual Graph)")
#     sidebar_user_ui()
#     sidebar_friendship_ui()
#     st.write("---")
#     edit_profile_ui()
#     st.write("---")
#     analysis_ui()

# if __name__ == "__main__":
#     main()
import streamlit as st
from typing import List, Set, Dict, Optional

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
        # Return all tastes in the same clusters as any in taste_list
        roots = {self.find(t) for t in taste_list}
        return {t for t in self.parent if self.find(t) in roots}

# --- Graph + Profile --- #
class Graph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        self.profile: Dict[str, Dict] = {}  # {user: {bio, tastes, password}}
        self.taste_list = [
            "Rock Music", "Classical Music", "Hip-Hop", "Jazz",
            "Football", "Basketball", "Cricket", "Badminton",
            "Science Fiction", "Fantasy", "Mystery", "Romance",
            "Coding", "Gaming", "Cooking", "Travel"
        ]
        self.taste_dsu = DSU()

    # ---- DSU logic ---- #
    def _rebuild_taste_dsu(self):
        self.taste_dsu = DSU()
        for taste in self.taste_list:
            self.taste_dsu.find(taste)
        for p in self.profile.values():
            tastes = p["tastes"]
            if len(tastes) > 1:
                for i in range(1, len(tastes)):
                    self.taste_dsu.union(tastes[0], tastes[i])

    def users_in_same_taste_cluster(self, user: str) -> Set[str]:
        """All users sharing any transitive taste cluster with user (excluding direct self)."""
        if user not in self.profile:
            return set()
        user_tastes = self.profile[user]["tastes"]
        if not user_tastes:
            return set()
        cluster_tastes = self.taste_dsu.cluster_members(user_tastes)
        users = set()
        for other, prof in self.profile.items():
            if other == user:
                continue
            if set(prof["tastes"]) & cluster_tastes:
                users.add(other)
        return users

    # ---- CRUD ---- #
    def add_user(self, user: str, bio: str, tastes: List[str], password: str = ""):
        user = user.strip()
        if not user or user in self.adj:
            return
        self.adj[user] = set()
        self.profile[user] = {"bio": bio, "tastes": tastes, "password": password}
        self._rebuild_taste_dsu()

    def edit_profile(self, user: str, bio: str, tastes: List[str], password: str = None):
        if user not in self.profile:
            return
        self.profile[user]["bio"] = bio
        self.profile[user]["tastes"] = tastes
        if password is not None:
            self.profile[user]["password"] = password
        self._rebuild_taste_dsu()

    def remove_user(self, user: str):
        if user in self.adj:
            for friend in list(self.adj[user]):
                self.adj[friend].remove(user)
            del self.adj[user]
        if user in self.profile:
            del self.profile[user]
        self._rebuild_taste_dsu()

    def add_friendship(self, u: str, v: str):
        if u == v:
            return
        for name in (u, v):
            if name not in self.adj:
                self.add_user(name, "", [])
        self.adj[u].add(v)
        self.adj[v].add(u)

    def remove_friendship(self, u: str, v: str):
        if u in self.adj and v in self.adj[u]:
            self.adj[u].remove(v)
            self.adj[v].remove(u)

    # ---- Graph Algorithms ---- #
    def bfs_shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
        if src not in self.adj or dst not in self.adj:
            return None
        if src == dst:
            return [src]
        from collections import deque
        q = deque([src])
        parent = {src: None}
        while q:
            node = q.popleft()
            for nei in self.adj[node]:
                if nei not in parent:
                    parent[nei] = node
                    if nei == dst:
                        return self._reconstruct(parent, dst)
                    q.append(nei)
        return None

    def _reconstruct(self, parent, node):
        path = []
        while node is not None:
            path.append(node)
            node = parent[node]
        return path[::-1]

    def mutual_friends(self, u: str, v: str) -> Set[str]:
        if u not in self.adj or v not in self.adj:
            return set()
        return self.adj[u] & self.adj[v]

    def recommend_friends(self, u: str) -> List[tuple]:
        if u not in self.adj:
            return []
        direct = self.adj[u]
        user_tastes = set(self.profile[u]["tastes"])
        # Friends-of-friends
        fof = set()
        for f in direct:
            fof.update(self.adj[f])
        fof.discard(u)
        fof -= direct
        # Users in any shared taste cluster
        cluster_users = self.users_in_same_taste_cluster(u)
        shared_taste_counts = {}
        for other in cluster_users | fof:
            if other == u: continue
            shared = user_tastes & set(self.profile[other]["tastes"])
            shared_taste_counts[other] = len(shared)
        # Build buckets
        both = [name for name in (cluster_users & fof)]
        cluster_only = [name for name in (cluster_users - set(both) - direct)]
        fof_only = [name for name in (fof - set(both))]
        both = sorted(both, key=lambda x: (-shared_taste_counts.get(x,0), x))
        cluster_only = sorted(cluster_only, key=lambda x: (-shared_taste_counts.get(x,0), x))
        fof_only = sorted(fof_only, key=lambda x: (-shared_taste_counts.get(x,0), x))
        ranked = [(name, 2, shared_taste_counts.get(name,0)) for name in both] + \
                 [(name, 1, shared_taste_counts.get(name,0)) for name in cluster_only] + \
                 [(name, 0, shared_taste_counts.get(name,0)) for name in fof_only]
        return ranked

    def adjacency_list(self):
        return {u: sorted(list(v)) for u, v in self.adj.items()}

    def connected_components(self):
        visited = set()
        comps = []
        def dfs(n, comp):
            visited.add(n)
            comp.add(n)
            for nei in self.adj[n]:
                if nei not in visited:
                    dfs(nei, comp)
        for node in self.adj:
            if node not in visited:
                comp = set()
                dfs(node, comp)
                comps.append(comp)
        return comps

    def get_profile(self, user):
        return self.profile.get(user, {"bio": "", "tastes": [], "password": ""})

