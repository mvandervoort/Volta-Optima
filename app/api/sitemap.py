from starlette.responses import Response
from starlette.requests import Request
from app.services.sitemap_service import SitemapService


async def sitemap_endpoint(request: Request):
    content = SitemapService.get_sitemap_xml()
    return Response(content=content, media_type="application/xml")


async def robots_endpoint(request: Request):
    content = SitemapService.get_robots_txt()
    return Response(content=content, media_type="text/plain")