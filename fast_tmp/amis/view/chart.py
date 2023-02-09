from typing import Optional

from fast_tmp.amis.base import SchemaNode


# https://aisuda.bce.baidu.com/amis/zh-CN/components/chart#%E4%BA%8B%E4%BB%B6%E8%A1%A8
class Chart(SchemaNode):
    type: str = "chart"
    className: Optional[str]  # 外层 Dom 的类名
    body: Optional[SchemaNode]  # 内容容器
    api: Optional[str]  # 配置项接口地址
    source: Optional[str]  # 通过数据映射获取数据链中变量值作为配置
    initFetch: Optional[bool]  # 组件初始化时，是否请求接口
    interval: Optional[int]  # 刷新时间(最小 1000)
    config: Optional[dict]  # 设置 eschars 的配置项,当为string的时候可以设置 function 等配置项
    style: Optional[str]  # 设置根元素的 style
    width: Optional[str]  # 设置根元素的宽度
    height: Optional[str]  # 设置根元素的高度
    replaceChartOption: Optional[bool]  # 每次更新是完全覆盖配置项还是追加？
    trackExpression: Optional[str]  # 当这个表达式的值有变化时更新图表
    dataFilter: Optional[
        str
    ]  # 自定义 echart config 转换，函数签名：function(config, echarts, data) {return config;} 配置时直接写函数体。其中 config 是当前 echart 配置，echarts 就是 echarts 对象，data 为上下文数据。
    mapURL: Optional[str]  # 地图 geo json 地址
    mapName: Optional[str]  # 地图名称
    loadBaiduMap: Optional[bool]  # 加载百度地图
    onEvent: Optional[dict]
