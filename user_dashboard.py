# import streamlit as st
# from user_graph_db import load_profiles, load_friendships, Graph

# # Set page config as the first Streamlit command
# st.set_page_config(page_title="User Dashboard", layout="wide")

# # Cache the raw profile data from the database
# @st.cache_data
# def get_profiles():
#     return load_profiles()

# # Cache the raw friendship data from the database
# @st.cache_data
# def get_friendships():
#     return load_friendships()

# # Build the Graph object from cached data (not cached itself)
# def build_graph():
#     g = Graph()
#     profiles = get_profiles()
#     for doc in profiles:
#         g.add_user(doc["username"], doc["bio"], doc["tastes"])
#     friendships = get_friendships()
#     for doc in friendships:
#         username = doc["username"]
#         if username not in g.adj:
#             g.adj[username] = set()
#         g.adj[username].update(doc["friends"])
#         for friend in doc["friends"]:
#             if friend not in g.adj:
#                 g.adj[friend] = set()
#             g.adj[friend].add(username)
#     return g

# def main():
#     g = build_graph()
#     st.title("User Dashboard")
#     users = list(g.adj.keys())
#     if not users:
#         st.info("No users—ask admin to add.")
#         return

#     st.header("Login")
#     user = st.selectbox("Select Username", users, key="login_user")
#     st.write("---")

#     profile = g.get_profile(user)
#     st.subheader(f"Welcome, {user}!")
#     st.markdown(f"**Bio:** {profile['bio']}")
#     st.markdown(f"**Your Tastes:** {', '.join(profile['tastes']) or 'None'}")

#     st.subheader("Your Friends")
#     fr = sorted(g.adj[user])
#     st.write(", ".join(fr) or "None")

#     st.subheader("Friend Recommendations")
#     recs = g.recommend_friends(user)
#     if recs:
#         lbl = {2: "Cluster+FoF", 1: "Cluster", 0: "FoF"}
#         st.table([(n, lbl[c], f"{s} shared") for n, c, s in recs])
#     else:
#         st.write("No recommendations.")

#     st.subheader("Users in Your Taste Cluster")
#     cluster = sorted(g.users_in_same_taste_cluster(user))
#     st.write(", ".join(cluster) or "None")

# if __name__ == "__main__":
#     main()   

import streamlit as st
from user_graph_db import load_graph_from_db, persist_graph, Graph

st.set_page_config(page_title="User Dashboard", layout="wide")

def main():
    g = load_graph_from_db()
    users = list(g.adj.keys())

    if "user" not in st.session_state:
        st.title("Welcome to the User Dashboard")
        mode = st.radio("Choose mode", ["Login", "Sign Up"])

        if mode == "Login":
            st.header("Login")
            username = st.selectbox("Username", users) if users else st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                profile = g.get_profile(username)
                if not profile:
                    st.error("User not found.")
                elif profile.get("password") != password:
                    st.error("Incorrect password.")
                else:
                    st.session_state["user"] = username
                    st.success(f"Logged in as {username}")

        else:  # Sign Up
            st.header("Sign Up")
            username = st.text_input("Choose a username")
            password = st.text_input("Set a password", type="password")
            bio = st.text_area("Bio")
            tastes = st.multiselect("Select at least 3 tastes", g.taste_list)
            if st.button("Sign Up"):
                if not username or not password:
                    st.error("Username and password required.")
                elif len(tastes) < 3:
                    st.error("Please select at least 3 tastes.")
                elif username in users:
                    st.error("Username already taken.")
                else:
                    g.add_user(username, bio, tastes, password=password)
                    persist_graph(g)
                    st.session_state["user"] = username
                    st.success("Signed up successfully.")

    else:
        user = st.session_state["user"]
        st.title(f"Welcome, {user}!")
        if st.button("Log out"):
            del st.session_state["user"]
            st.success("Logged out successfully")
            st.experimental_rerun()

        profile = g.get_profile(user)
        st.write(f"**Bio:** {profile.get('bio', '')}")
        st.write(f"**Tastes:** {', '.join(profile.get('tastes', []))}")
        friends = sorted(g.adj.get(user, []))
        st.write(f"**Friends:** {', '.join(friends) or 'None'}")

if __name__ == "__main__":
    main()
