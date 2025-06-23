
# # import streamlit as st
# # from user_graph_db import load_graph_from_db, persist_graph

# # st.set_page_config(page_title="User Dashboard", layout="wide")

# # def main():
# #     # Restore session from URL on reload
# #     params = st.experimental_get_query_params()
# #     if "user" in params and "user" not in st.session_state:
# #         st.session_state["user"] = params["user"][0]

# #     g = load_graph_from_db()
# #     users = list(g.adj.keys())

# #     # Authentication / Sign-up
# #     if "user" not in st.session_state:
# #         st.title("Welcome to the User Dashboard")
# #         mode = st.radio("Choose mode", ["Login", "Sign Up"])
# #         if mode == "Login":
# #             st.header("Login")
# #             username = st.selectbox("Username", users) if users else st.text_input("Username")
# #             password = st.text_input("Password", type="password")
# #             if st.button("Login"):
# #                 profile = g.get_profile(username)
# #                 if not profile:
# #                     st.error("User not found.")
# #                 elif profile.get("password") != password:
# #                     st.error("Incorrect password.")
# #                 else:
# #                     st.session_state["user"] = username
# #                     # persist in URL so reload remembers
# #                     st.experimental_set_query_params(user=username)
# #                     st.success(f"Logged in as {username}")
# #                     st.experimental_rerun()
# #         else:
# #             st.header("Sign Up")
# #             username = st.text_input("Choose a username")
# #             password = st.text_input("Set a password", type="password")
# #             bio      = st.text_area("Bio")
# #             tastes   = st.multiselect("Select at least 3 tastes", g.taste_list)
# #             if st.button("Sign Up"):
# #                 if not username or not password:
# #                     st.error("Username and password required.")
# #                 elif len(tastes) < 3:
# #                     st.error("Please select at least 3 tastes.")
# #                 elif username in users:
# #                     st.error("Username already taken.")
# #                 else:
# #                     g.add_user(username, bio, tastes, password=password)
# #                     persist_graph(g)
# #                     st.session_state["user"] = username
# #                     st.experimental_set_query_params(user=username)
# #                     st.success("Signed up successfully.")
# #                     st.experimental_rerun()

# #     # Main dashboard
# #     else:
# #         user = st.session_state["user"]
# #         st.title(f"Welcome, {user}!")
# #         if st.button("Log out"):
# #             # clear both session and URL param
# #             del st.session_state["user"]
# #             st.experimental_set_query_params()
# #             st.success("Logged out successfully")
# #             st.experimental_rerun()

# #         # Profile & current friends
# #         profile = g.get_profile(user)
# #         st.write(f"**Bio:** {profile.get('bio', '')}")
# #         st.write(f"**Tastes:** {', '.join(profile.get('tastes', []))}")
# #         friends = sorted(g.adj.get(user, []))
# #         st.write(f"**Friends:** {', '.join(friends) or 'None'}")

# #         # Incoming friend requests
# #         st.subheader("Incoming Friend Requests")
# #         incoming = g.get_incoming_requests(user)
# #         if incoming:
# #             for sender in incoming:
# #                 cols = st.columns([3,1,1])
# #                 cols[0].write(sender)
# #                 if cols[1].button("Accept", key=f"accept_{sender}"):
# #                     g.accept_friend_request(sender, user)
# #                     persist_graph(g)
# #                     st.success(f"You are now friends with {sender}")
# #                     st.experimental_rerun()
# #                 if cols[2].button("Reject", key=f"reject_{sender}"):
# #                     g.reject_friend_request(sender, user)
# #                     persist_graph(g)
# #                     st.info(f"Friend request from {sender} rejected")
# #                     st.experimental_rerun()
# #         else:
# #             st.write("No incoming requests.")

# #         # Friend recommendations
# #         st.subheader("Friend Recommendations")
# #         recs = g.recommend_friends(user)
# #         if recs:
# #             label = {2: "Cluster + FoF", 1: "Cluster", 0: "Friends-of-Friends"}
# #             for name, code, shared in recs:
# #                 with st.container():
# #                     cols = st.columns([3,1])
# #                     cols[0].markdown(f"**{name}**")
# #                     cols[0].write(f"{shared} shared tastes ({label[code]})")
# #                     if cols[1].button("Send Request", key=f"send_{name}"):
# #                         g.send_friend_request(user, name)
# #                         persist_graph(g)
# #                         st.success(f"Friend request sent to {name}")
# #                         st.experimental_rerun()
# #         else:
# #             st.write("No recommendations.")

# #         # People in your network (FoF)
# #         st.subheader("People in Your Network")
# #         fof = set()
# #         for f in g.adj.get(user, []):
# #             fof |= g.adj.get(f, set())
# #         fof.discard(user)
# #         fof -= set(g.adj.get(user, []))
# #         if fof:
# #             for person in sorted(fof):
# #                 cols = st.columns([3,1])
# #                 cols[0].write(person)
# #                 if cols[1].button("Show relation path", key=f"path_{person}"):
# #                     path = g.bfs_shortest_path(user, person)
# #                     if path:
# #                         st.info(" → ".join(path))
# #                     else:
# #                         st.error("No path found")
# #         else:
# #             st.write("No people in your network.")

# # if __name__ == "__main__":
# #     main()
# # user_dashboard.py

# # user_dashboard.py

# import streamlit as st
# from user_graph_db import load_graph_from_db, persist_graph

# # Use Streamlit’s stable query-param API
# # Read params with st.query_params; write with attribute assignment or .clear()
# st.set_page_config(page_title="User Dashboard", layout="wide")

# def main():
#     # 1) Restore login from URL, if present
#     params = st.query_params
#     if "user" in params and "user" not in st.session_state:
#         # st.query_params may return a list if repeated, so handle both cases
#         raw = params["user"]
#         user_param = raw[-1] if isinstance(raw, list) else raw
#         st.session_state["user"] = user_param

#     g     = load_graph_from_db()
#     users = sorted(g.adj.keys())

#     # 2) Login / Sign-Up flow
#     if "user" not in st.session_state:
#         st.title("Welcome to the User Dashboard")
#         mode = st.radio("Choose mode", ["Login", "Sign Up"])
#         if mode == "Login":
#             st.header("Login")
#             username = st.selectbox("Username", users) if users else st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             if st.button("Login"):
#                 prof = g.get_profile(username)
#                 if not prof:
#                     st.error("User not found.")
#                 elif prof.get("password", "") != password:
#                     st.error("Incorrect password.")
#                 else:
#                     st.session_state["user"] = username
#                     # persist in URL
#                     st.query_params.user = username
#                     st.success(f"Logged in as {username}")
#                     st.experimental_rerun()

#         else:
#             st.header("Sign Up")
#             username = st.text_input("Choose a username")
#             password = st.text_input("Set a password", type="password")
#             bio      = st.text_area("Bio")
#             tastes   = st.multiselect("Select ≥3 tastes", g.taste_list)
#             avatar_u = st.file_uploader("Profile picture (png/jpg)", type=["png","jpg","jpeg"])
#             if st.button("Sign Up"):
#                 if not username or not password:
#                     st.error("Username & password required.")
#                 elif len(tastes) < 3:
#                     st.error("Please select at least 3 tastes.")
#                 elif username in users:
#                     st.error("Username already taken.")
#                 else:
#                     avatar_bytes = avatar_u.read() if avatar_u else None
#                     g.add_user(username, bio, tastes, password=password, avatar=avatar_bytes)
#                     persist_graph(g)
#                     st.session_state["user"] = username
#                     st.query_params.user = username
#                     st.success("Signed up successfully.")
#                     st.experimental_rerun()

#     # 3) Main Dashboard
#     else:
#         user = st.session_state["user"]
#         st.title(f"Welcome, {user}!")
#         if st.button("Log out"):
#             # clear session + URL
#             del st.session_state["user"]
#             st.query_params.clear()
#             st.success("Logged out")
#             st.experimental_rerun()

#         # Display avatar if exists
#         prof = g.get_profile(user)
#         if prof.get("avatar"):
#             st.image(prof["avatar"], width=150)

#         # -- Your Friends (hidden until expanded) --
#         with st.expander("Your Friends"):
#             friends = sorted(g.adj.get(user, set()))
#             if friends:
#                 for f in friends:
#                     c1, c2 = st.columns([3,1])
#                     c1.write(f)
#                     if c2.button("Remove", key=f"remove_{f}"):
#                         g.remove_friendship(user, f)
#                         persist_graph(g)
#                         st.success(f"Removed friendship with {f}")
#                         st.experimental_rerun()
#             else:
#                 st.write("You have no friends yet.")

#         # -- Incoming Friend Requests --
#         st.subheader("Incoming Friend Requests")
#         incoming = g.get_incoming_requests(user)
#         if incoming:
#             for sender in incoming:
#                 c1, c2, c3 = st.columns([3,1,1])
#                 c1.write(sender)
#                 if c2.button("Accept", key=f"accept_{sender}"):
#                     g.accept_friend_request(sender, user)
#                     persist_graph(g)
#                     st.success(f"You are now friends with {sender}")
#                     st.experimental_rerun()
#                 if c3.button("Reject", key=f"reject_{sender}"):
#                     g.reject_friend_request(sender, user)
#                     persist_graph(g)
#                     st.info(f"Rejected request from {sender}")
#                     st.experimental_rerun()
#         else:
#             st.write("No incoming requests.")

#         # -- Friend Recommendations --
#         st.subheader("Friend Recommendations")
#         recs = g.recommend_friends(user)
#         if recs:
#             labels = {2: "Cluster + FoF", 1: "Cluster", 0: "Friends-of-Friends"}
#             for name, code, shared in recs:
#                 exp = st.expander(f"{name} — {shared} shared tastes ({labels[code]})")
#                 with exp:
#                     p = g.get_profile(name)
#                     if p.get("avatar"):
#                         st.image(p["avatar"], width=100)
#                     st.write("**Bio:**", p.get("bio",""))
#                     st.write("**Tastes:**", ", ".join(p.get("tastes",[])))
#                     if st.button("Send Request", key=f"send_{name}"):
#                         g.send_friend_request(user, name)
#                         persist_graph(g)
#                         st.success(f"Friend request sent to {name}")
#                         st.experimental_rerun()
#         else:
#             st.write("No recommendations at this time.")

#         # -- People in Your Network (FoF) --
#         st.subheader("People in Your Network")
#         fof = set()
#         for f in g.adj.get(user, set()):
#             fof |= g.adj.get(f, set())
#         fof.discard(user)
#         fof -= g.adj.get(user, set())

#         if fof:
#             for person in sorted(fof):
#                 exp = st.expander(person)
#                 with exp:
#                     p = g.get_profile(person)
#                     if p.get("avatar"):
#                         st.image(p["avatar"], width=100)
#                     st.write("**Bio:**", p.get("bio",""))
#                     st.write("**Tastes:**", ", ".join(p.get("tastes",[])))
#                     col1, col2 = st.columns(2)
#                     if col1.button("Show relation path", key=f"path_{person}"):
#                         path = g.bfs_shortest_path(user, person)
#                         st.info(" → ".join(path) if path else "No path found")
#                     # allow sending request if not already friends/requested
#                     if (person not in g.adj.get(user, set())
#                         and user not in g.pending_requests.get(person, set())):
#                         if col2.button("Send Request", key=f"netreq_{person}"):
#                             g.send_friend_request(user, person)
#                             persist_graph(g)
#                             st.success(f"Friend request sent to {person}")
#                             st.experimental_rerun()
#         else:
#             st.write("No one in your network beyond your friends.")

# if __name__ == "__main__":
#     main()
import streamlit as st
from user_graph_db import load_graph_from_db, persist_graph

st.set_page_config(page_title="User Dashboard", layout="wide")

def main():
    # 1) Restore session from the URL on reload
    params = st.query_params
    if "user" in params and "user" not in st.session_state:
        raw = params["user"]
        user_param = raw[-1] if isinstance(raw, list) else raw
        st.session_state["user"] = user_param

    # 2) Load graph and user list
    g = load_graph_from_db()
    users = sorted(g.adj.keys())

    # 3) Login / Sign-up
    if "user" not in st.session_state:
        st.title("Welcome to the User Dashboard")
        mode = st.radio("Choose mode", ["Login", "Sign Up"])
        if mode == "Login":
            st.header("Login")
            username = st.selectbox("Username", users) if users else st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                prof = g.get_profile(username)
                if not prof:
                    st.error("User not found.")
                elif prof.get("password", "") != password:
                    st.error("Incorrect password.")
                else:
                    st.session_state["user"] = username
                    st.query_params["user"] = username
                    st.success(f"Logged in as {username}")
        else:
            st.header("Sign Up")
            username = st.text_input("Choose a username")
            password = st.text_input("Set a password", type="password")
            bio      = st.text_area("Bio")
            tastes   = st.multiselect("Select at least 3 tastes", g.taste_list)
            avatar_u = st.file_uploader("Profile picture (png/jpg)", type=["png","jpg","jpeg"])
            if st.button("Sign Up"):
                if not username or not password:
                    st.error("Username and password required.")
                elif len(tastes) < 3:
                    st.error("Please select at least 3 tastes.")
                elif username in users:
                    st.error("Username already taken.")
                else:
                    avatar_bytes = avatar_u.read() if avatar_u else None
                    g.add_user(username, bio, tastes, password=password, avatar=avatar_bytes)
                    persist_graph(g)
                    st.session_state["user"] = username
                    st.query_params["user"] = username
                    st.success("Signed up successfully.")
    # 4) Main dashboard
    else:
        user = st.session_state["user"]
        st.title(f"Welcome, {user}!")

        # Log out
        if st.button("Log out"):
            del st.session_state["user"]
            st.query_params.clear()
            st.success("Logged out successfully")

        # Show avatar if present
        prof = g.get_profile(user)
        if prof.get("avatar"):
            st.image(prof["avatar"], width=150)

        # Your friends (hidden until you expand)
        with st.expander("Your Friends"):
            friends = sorted(g.adj.get(user, set()))
            if friends:
                for f in friends:
                    c1, c2 = st.columns([3,1])
                    c1.write(f)
                    if c2.button("Remove", key=f"rm_{f}"):
                        g.remove_friendship(user, f)
                        persist_graph(g)
                        st.success(f"Removed friendship with {f}")
            else:
                st.write("You have no friends yet.")

        # Incoming friend requests
        st.subheader("Incoming Friend Requests")
        incoming = g.get_incoming_requests(user)
        if incoming:
            for sender in incoming:
                c1, c2, c3 = st.columns([3,1,1])
                c1.write(sender)
                if c2.button("Accept", key=f"ac_{sender}"):
                    g.accept_friend_request(sender, user)
                    persist_graph(g)
                    st.success(f"You are now friends with {sender}")
                if c3.button("Reject", key=f"rj_{sender}"):
                    g.reject_friend_request(sender, user)
                    persist_graph(g)
                    st.info(f"Rejected request from {sender}")
        else:
            st.write("No incoming requests.")

        # Friend recommendations
        st.subheader("Friend Recommendations")
        recs = g.recommend_friends(user)
        if recs:
            labels = {2: "Cluster + FoF", 1: "Cluster", 0: "Friends-of-Friends"}
            for name, code, shared in recs:
                exp = st.expander(f"{name} — {shared} shared tastes ({labels[code]})")
                with exp:
                    p = g.get_profile(name)
                    if p.get("avatar"):
                        st.image(p["avatar"], width=100)
                    st.write("**Bio:**", p.get("bio",""))
                    st.write("**Tastes:**", ", ".join(p.get("tastes",[])))
                    if st.button("Send Request", key=f"sr_{name}"):
                        g.send_friend_request(user, name)
                        persist_graph(g)
                        st.success(f"Friend request sent to {name}")
        else:
            st.write("No recommendations at this time.")

        # Friends-of-Friends network
        st.subheader("People in Your Network")
        fof = set()
        for f in g.adj.get(user, set()):
            fof |= g.adj.get(f, set())
        fof.discard(user)
        fof -= g.adj.get(user, set())

        if fof:
            for person in sorted(fof):
                exp = st.expander(person)
                with exp:
                    p = g.get_profile(person)
                    if p.get("avatar"):
                        st.image(p["avatar"], width=100)
                    st.write("**Bio:**", p.get("bio",""))
                    st.write("**Tastes:**", ", ".join(p.get("tastes",[])))
                    c1, c2 = st.columns(2)
                    if c1.button("Show relation path", key=f"path_{person}"):
                        path = g.bfs_shortest_path(user, person)
                        st.info(" → ".join(path) if path else "No path found")
                    if person not in g.adj.get(user, set()) \
                       and user not in g.pending_requests.get(person, set()):
                        if c2.button("Send Request", key=f"nr_{person}"):
                            g.send_friend_request(user, person)
                            persist_graph(g)
                            st.success(f"Friend request sent to {person}")
        else:
            st.write("No one in your network beyond your friends.")

if __name__ == "__main__":
    main()
