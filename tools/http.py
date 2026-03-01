import core
import requests

class HttpTool(core.tool.Tool):
    """lets the AI send/receive HTTP requests"""

    async def http_get(self, url: str, headers: dict, params: dict = None):
        """
        performs a HTTP GET request on url

        Args:
            url: the URL to target
            params: any parameters to add to the request (shows up as the ?q=blah&si=blah2 part of the url)
            headers: HTTP headers. You want to always set these!
        """
        result = requests.get(url, params=params, headers=headers)
        return self.result({
            "status": f"{result.status_code} {result.reason}",
            "content": result.text
        })

    async def http_post(self, url: str, headers: dict, data: dict = None):
        """
        performs a HTTP POST on url

        Args:
            url: the URL to target
            data: the data to post to the url
            headers: HTTP headers. You want to always set these!
        """
        result = requests.post(url, data, headers=headers)
        return self.result(result.text)
