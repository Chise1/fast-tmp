def remove_media_start(path: str) -> str:
    """
    对图片和文件类型进行media路径的处理
    主要用于保存到数据库
    """
    from fast_tmp.conf import settings

    if path.startswith("/" + settings.MEDIA_ROOT):  # 去除静态头
        header_len = len(settings.MEDIA_ROOT) + 2
        return path[header_len:]
    return path


def add_media_start(path: str) -> str:
    """
    增加路径（主要用于返回到前台）
    """
    from fast_tmp.conf import settings

    if path.startswith("/" + settings.MEDIA_ROOT):
        return path
    return "/" + settings.MEDIA_ROOT + "/" + path
