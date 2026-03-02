import core
import requests

class HttpTool(core.tool.Tool):
    """lets the AI send/receive HTTP requests"""

    async def get(self, url: str, headers: dict = None, params: dict = None):
        """
        performs a HTTP GET request on url

        Args:
            url: the URL to target
            params: any parameters to add to the request (shows up as the ?q=blah&si=blah2 part of the url)
            headers: HTTP headers. You want to always set these!
        """
        if not headers:
            headers = {'User-Agent': 'Mozilla/5.0'}

        result = requests.get(url, params=params, headers=headers)
        return self.result({
            "status": f"{result.status_code} {result.reason}",
            "content": result.text
        })

    async def post(self, url: str, headers: dict = None, data: dict = None):
        """
        performs a HTTP POST on url

        Args:
            url: the URL to target
            data: the data to post to the url
            headers: HTTP headers. You want to always set these!
        """
        if not headers:
            headers = {'User-Agent': 'Mozilla/5.0'}

        result = requests.post(url, data, headers=headers)
        return self.result(result.text)
