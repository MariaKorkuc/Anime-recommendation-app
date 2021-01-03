import random
from neo4j import GraphDatabase
from enum import Enum


class R_category(Enum):
    GENRE = 'GENRE'
    ACTOR = 'ACTOR'
    USER = 'USER'
    RANDOM = 'RANDOM'


class Neo:
    def __init__(self, url, auth):
        self.driver = GraphDatabase.driver(uri=url, auth=auth)
        self.session = self.driver.session()

    def get_series(self, user=None, actor=None, genre=None):
        if user:
            query = """
            match (n:u7korkucUser{username:$username})--(s:u7korkucSeries) return s.title as title, count(*)
            """
            x = {"username": user}
            results = self.session.run(query, x)
        elif actor:
            query = """
            match (n:u7korkucActor{name:$name})--(s:u7korkucSeries) return s.title as title, count(*)
            """
            x = {"name": actor}
            results = self.session.run(query, x)
        elif genre:
            query = """
            match (n:u7korkucGenre{name:$name})--(s:u7korkucSeries) return s.title as title, count(*)
            """
            x = {"name": genre}
            results = self.session.run(query, x)
        else:
            query = """
            match (n:u7korkucSeries) return n.title as title, count(*)
            """
            results = self.session.run(query)

        return [result['title'] for result in results]

    def get_actors(self, user=None, series=None, genre=None):
        if user:
            query = """
            MATCH (n:u7korkucUser{username:$username})-[:WATCHED]->(s)<-[:VOICED_IN]-(a) RETURN a.name as name, count(*)
            """
            x = {"username": user}
            results = self.session.run(query, x)
        elif series:
            query = """
            match (n:u7korkucSeries{title:$title})--(s:u7korkucActor) return s.name as name, count(*)
            """
            x = {"title": series}
            results = self.session.run(query, x)
        elif genre:
            query = """
            MATCH (n:u7korkucGenre{name:$name})<-[:IS_OF_GENRE]-(s)<-[:VOICED_IN]-(a) RETURN a.name as name, count(*)
            """
            x = {"name": genre}
            results = self.session.run(query, x)
        else:
            query = """
            match (n:u7korkucActor) return n.name as name, count(*)
            """
            results = self.session.run(query)

        return [result['name'] for result in results]

    def get_genres(self, user=None, series=None, actor=None):
        if user:
            query = """
            MATCH (n:u7korkucUser{username:$username})-[:WATCHED]->(s)-[:IS_OF_GENRE]->(g) RETURN g.name as name, count(*)
            """
            x = {"username": user}
            results = self.session.run(query, x)
        elif series:
            query = """
            match (n:u7korkucSeries{title:$title})--(g:u7korkucGenre) return g.name as name, count(*)
            """
            x = {"title": series}
            results = self.session.run(query, x)
        elif actor:
            query = """
            MATCH (n:u7korkucActor{name:$name})-[:VOICED_IN]->(s)-[:IS_OF_GENRE]->(g) RETURN g.name as name, count(*)
            """
            x = {"name": actor}
            results = self.session.run(query, x)
        else:
            query = """
            match (n:u7korkucGenre) return n.name as name, count(*)
            """
            results = self.session.run(query)

        return [result['name'] for result in results]

    def genre_list_series(self, user):
        genres = self.get_genres(user=user)
        if not genres:
            genres = self.get_genres()
        genre = random.choice(genres)
        series_genre = self.get_series(genre=genre)
        return series_genre, genre

    def actor_list_series(self, user):
        #     get actors by user
        actors = self.get_actors(user=user)
        #     get random actor from actors to use in: we recommend {series}, because you like {actor}
        if not actors:
            actors = self.get_actors()
        actor = random.choice(actors)
        #     get all series with our actor
        series_actors = self.get_series(actor=actor)
        return series_actors, actor

    def user_list_series(self, user):
        query = """
            MATCH (n:u7korkucUser{username:$username}), (u:u7korkucUser)
            WHERE (n)-->(u) OR (u)-->(n)
            RETURN u.username as name, count(*)
            """
        x = {"username": user}
        results = self.session.run(query, x)
        friends = [result['name'] for result in results]
        if not friends:
            return [], 'nobody'
        friend = random.choice(friends)
        series_friend = self.get_series(user=friend)
        return series_friend, friend

    def random_list_series(self, user):
        generators = [self.genre_list_series, self.actor_list_series, self.user_list_series]
        gen = random.choice(generators)
        return gen(user)

    def get_recommendation(self, user, category=R_category.RANDOM, number_to_recommend=1):
        if category == R_category.GENRE:
            series, cat = self.genre_list_series(user)
        elif category == R_category.ACTOR:
            series, cat = self.actor_list_series(user)
        elif category == R_category.USER:
            series, cat = self.user_list_series(user)
        else:
            series, cat = self.random_list_series(user)

        series_to_exclude = self.get_series(user=user)

        if not series:
            series = self.get_series()
        series_rec = [s for s in series if s not in series_to_exclude]
        number_to_recommend = number_to_recommend if number_to_recommend <= len(series_rec) else len(series_rec)
        chosen_series = random.sample(series_rec, number_to_recommend)
        return chosen_series, cat

    def create_user(self, username, password):
        query = """
            match (n:u7korkucUser{username:$username}) return n.username
            """
        x = {"username": username}
        results = list(self.session.run(query, x))
        if results:
            info = f'User {username} already exists'
        else:
            query = """
            create(n:u7korkucUser{database: 'u7korkuc', username:$username, password:$password})
            RETURN n.name as name
            """
            x = {"username": username, "password": password}
            results = list(self.session.run(query, x))
            info = f'Created user {username}'
        return info

    def delete_user(self, username):
        query = """
            match (n:u7korkucUser{username:$username}) return n.username
            """
        x = {"username": username}
        results = list(self.session.run(query, x))
        if len(results) == 1:
            query = """
            MATCH (n:u7korkucUser { username: $username })
            DETACH DELETE n    
            """
            x = {"username": username}
            results = list(self.session.run(query, x))
            info = f'User {username} deleted'
        else:
            info = f"User {username} doesn't exist"
        return info

    def get_friendly(self, user1, user2):
        query = """
        MATCH (a:u7korkucUser{username:$user1})-[:FRIEND]->(b:u7korkucUser)
        RETURN b.username as name
        """
        x = {"user1": user1}
        result = self.session.run(query, x)
        users = [r['name'] for r in result]
        if user2 in users:
            info = 'Already befriended'
        else:
            query = """
                match(a:u7korkucUser{username:$user1}),(b:u7korkucUser{username:$user2}) 
                create (a)-[r:FRIEND]->(b)
                """
            x = {"user1": user1, "user2": user2}
            info = self.session.run(query, x).value()
        return info

    def get_unfriendly(self, user1, user2):
        query = """
            MATCH (a:u7korkucUser{username:$user1})-[r:FRIEND]->(b:u7korkucUser{username:$user2})
            DELETE r
            """
        x = {"user1": user1, "user2": user2}
        info = self.session.run(query, x).value()
        return info

    def marked_as_watched(self, user, series):
        query = """
        MATCH (a:u7korkucUser{username:$user1})--(s:u7korkucSeries) RETURN s.title as title
        """
        x = {"user1": user}
        result = self.session.run(query, x)
        ser = [r['title'] for r in result]
        if series in ser:
            info = 'Already marked as watched'
        else:
            query = """
                match(u:u7korkucUser{username:$user}),(s:u7korkucSeries{title:$series}) 
                create (u)-[r:WATCHED]->(s)
                """
            x = {"user": user, "series": series}
            info = self.session.run(query, x).value()
        return info

    def marked_as_unwatched(self, user, series):
        query = """
            match (u:u7korkucUser{username:$user})-[r:WATCHED]->(s:u7korkucSeries{title:$series})
            DELETE r
            """
        x = {"user": user, "series": series}
        info = self.session.run(query, x).value()
        return info

    def get_friends(self, user=None):
        if user:
            query = """
            MATCH (n:u7korkucUser{username:$username})--(s:u7korkucUser) RETURN s.username as name, count(*)
            """
            x = {"username": user}
            results = self.session.run(query, x)
        else:
            query = """
            match (n:u7korkucUser) return n.username as name, count(*)
            """
            results = self.session.run(query)

        return [result['name'] for result in results]
