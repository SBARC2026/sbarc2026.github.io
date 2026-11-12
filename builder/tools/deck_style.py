"""Eye-catching header band for the SBARC deck slides (applied to slide HTML after it is built)."""
import re

BAND = ('<div style="position:absolute;left:0;top:0;width:1920px;height:250px;'
        'background:linear-gradient(115deg, #0C1F35 0%, #14304F 55%, #1F4A75 100%);border-bottom:6px solid #C9A227"></div>\n')


def band(html):
    if 'height:250px;background:linear-gradient(115deg' in html:
        return html
    # old top stripes -> navy band
    html = re.sub(r'<div style="position:absolute;left:0;top:0;width:960px;height:10px;background:#14304F"></div>'
                  r'<div style="position:absolute;left:960px;top:0;width:960px;height:10px;background:#C9A227"></div>\n?', BAND, html, count=1)
    # kicker gold on navy, title white
    html = re.sub(r'(<p style="font-size:24px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:)#8A6A12', r'\1#E0C163', html, count=1)
    html = re.sub(r'(<h1 style="[^"]*?)line-height:1"', r'\1line-height:1;color:#FFFFFF"', html, count=1)
    # logos on a white chip
    html = html.replace('display:flex;flex-direction:row;gap:14px;align-items:center">',
                        'display:flex;flex-direction:row;gap:14px;align-items:center;background:#FFFEFB;padding:8px 14px;border-radius:12px">', 1)
    html = html.replace('position:absolute;right:128px;top:30px;display:flex', 'position:absolute;right:128px;top:26px;display:flex', 1)
    return html
