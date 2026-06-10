import os
import httpx
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Api42():
	"""This Class implement 42 api connectivity"""
	def __init__(self):
		self.FT_USER = os.getenv("FT_USER")
		self.FT_CLIENT_ID = os.getenv("FT_CLIENT_ID")
		self.FT_CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")
		self.BASE_URL = "https://api.intra.42.fr/v2"
		self.token = None
		self.token_expires_at = 0
		self.client = httpx.Client()
		if not self.FT_CLIENT_ID or not self.FT_CLIENT_SECRET or not self.FT_USER:
			raise ValueError("FT_CLIENT_ID, FT_CLIENT_SECRET, FT_USER requis")
		
	def get_token(self):
		now = datetime.now().timestamp()
		if not self.token or now >= self.token_expires_at:
			try:
				r = self.client.post(
					url="https://api.intra.42.fr/oauth/token",
					data={
						"grant_type": "client_credentials",
						"client_id": self.FT_CLIENT_ID,
						"client_secret": self.FT_CLIENT_SECRET
					}
				)
				r.raise_for_status()

			except httpx.HTTPError as e:
				logger.error(f"Token fetch failed: {e}")
				raise

			self.token = r.json()["access_token"]
			self.token_expires_at = now + r.json()["expires_in"]
		return self.token

	def _request(self, url: str):
		header = {"Authorization": f"Bearer {self.get_token()}"}
		try:
			r = self.client.get(url=url, headers=header)
			logger.debug(f"Response status: {r.status_code}")
			logger.debug(f"Response text: {r.text[:200]}")
			return r.json()
		except Exception as e:
			logger.error(f"Request failed:\n{e}")
			raise

	def get_user(self):
		return self._request(url=f"{self.BASE_URL}/users/{self.FT_USER}")

	def get_projects_users(self):
		page = 1
		projects = []
		while True:
			url = f"{self.BASE_URL}/users/{self.FT_USER}/projects_users?per_page=100&page={page}"
			r = self._request(url=url)
			if not r:
				break
			projects.extend(r)
			page += 1
			time.sleep(0.6)
		return projects

	
if __name__ == "__main__":
	import json
	api = Api42()
	token = api.get_token()
	user = api.get_user()
	projects = api.get_projects_users()
	print(json.dumps(user, indent=2))
	print(json.dumps(projects[:2], indent=2))