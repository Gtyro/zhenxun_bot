class NotFoundError(Exception):
    """
    未发现
    """

    pass


class GroupInfoNotFound(Exception):
    """
    群组未找到
    """

    pass


class EmptyError(Exception):
    """
    空错误
    """

    pass


class UserAndGroupIsNone(Exception):
    """
    用户和群组为空
    """

    pass


class InsufficientGold(Exception):
    """
    金币不足
    """

    pass


class NotFindSuperuser(Exception):
    """
    未找到超级用户
    """

    pass


class GoodsNotFound(Exception):
    """
    或找到道具
    """

    pass


class PlaywrightRenderError(Exception):
    """Playwright 渲染基础异常类"""

    pass
