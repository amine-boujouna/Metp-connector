import requests
from pymongo import MongoClient
from datetime import datetime
import logging
from config import ACCESS_TOKEN, FACEBOOK_PAGE_ID, MONGO_URI, DB_NAME

logging.basicConfig(level=logging.INFO)


class MetaConnector:
    
      """
    Connecteur simple pour Facebook Graph API (page Facebook)
    Collecte posts, images et commentaires, puis on  sauvegarde dans MongoDB.
    """

    def __init__(self, access_token, fb_page_id, mongo_uri=MONGO_URI, db_name=DB_NAME):
        self.access_token = access_token
        self.fb_page_id = fb_page_id
        self.base_url = "https://graph.facebook.com/v17.0"
        self.session = requests.Session()
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db["posts"]

    def _request(self, endpoint, params=None):
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        url = f"{self.base_url}/{endpoint}"
        logging.debug(f"Request URL: {url} Params: {params}")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_posts(self, limit=25):
        """
        On récupère les posts de la page Facebook avec images et commentaires.
        """
        fields = "id,message,created_time,attachments{media},comments.limit(100){from,message,created_time}"
        endpoint = f"{self.fb_page_id}/posts"
        params = {
            "fields": fields,
            "limit": limit
        }
        logging.info(f"Fetching up to {limit} posts from page {self.fb_page_id}")
        data = self._request(endpoint, params)
        posts = data.get("data", [])
        return posts

    def filter_posts_by_keyword(self, posts, keyword):
        """
        On filtre les posts contenant un mot clé dans le message.
        """
        filtered = []
        for post in posts:
            message = post.get("message", "")
            if keyword.lower() in message.lower():
                filtered.append(post)
        logging.info(f"Filtered {len(filtered)} posts containing keyword '{keyword}'")
        return filtered

    def parse_post(self, post):
        """
        On transforme la structure brute du post en un dict propre.
        """
        post_id = post.get("id")
        text = post.get("message", "")
        created_time = post.get("created_time")
        created_datetime = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z") if created_time else None

        # Récupérer les URLs des images
        images = []
        attachments = post.get("attachments", {}).get("data", [])
        for attach in attachments:
            media = attach.get("media", {})
            image_url = media.get("image", {}).get("src")
            if image_url:
                images.append(image_url)

        # Récupérer les commentaires
        comments_data = post.get("comments", {}).get("data", [])
        comments = []
        for c in comments_data:
            author = c.get("from", {}).get("name")
            comment_text = c.get("message")
            comment_time = c.get("created_time")
            comment_datetime = datetime.strptime(comment_time, "%Y-%m-%dT%H:%M:%S%z") if comment_time else None
            comments.append({
                "author": author,
                "text": comment_text,
                "date": comment_datetime
            })

        return {
            "post_id": post_id,
            "text": text,
            "images": images,
            "comments": comments,
            "created_time": created_datetime,
            "date_collected": datetime.utcnow()
        }

    def save_post(self, post_data):
        """
        on sauvegarde un post dans MongoDB (on évite les  doublons sur post_id).
        """
        if self.collection.find_one({"post_id": post_data["post_id"]}):
            logging.info(f"Post {post_data['post_id']} déjà présent, mise à jour ignorée.")
            return False
        self.collection.insert_one(post_data)
        logging.info(f"Post {post_data['post_id']} inséré en base.")
        return True

    def collect_posts(self, keyword=None, limit=50):
        """
        on collecte, filtre  et stocke les posts.
        """
        posts = self.get_posts(limit=limit)
        if keyword:
            posts = self.filter_posts_by_keyword(posts, keyword)

        count_saved = 0
        for post in posts:
            post_data = self.parse_post(post)
            if self.save_post(post_data):
                count_saved += 1
        logging.info(f"Collecte terminée, {count_saved} nouveaux posts enregistrés.")


if __name__ == "__main__":
    connector = MetaConnector(ACCESS_TOKEN, FACEBOOK_PAGE_ID)
    connector.collect_posts(keyword="Jacques Chirac", limit=100)
