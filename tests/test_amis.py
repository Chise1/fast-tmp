from fast_tmp.amis.nav import Nav, NavLinks
from fast_tmp.amis.view.card import Card, CardHeader
from fast_tmp.amis.view.divider import Divider

from .base import BaseSite


class TestAmis(BaseSite):
    """
    amis的模板
    这里主要是为了提高代码覆盖率 并没有实际的测试效果
    """

    nav = Nav()
    navlinks = NavLinks(to="https://www.baidu.com", label="links")
    Divider()
    card_header = CardHeader(title="header", subTitle="dd", description="..", avatar="....")
    Card(header=card_header)
