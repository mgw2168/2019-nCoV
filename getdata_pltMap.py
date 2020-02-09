from datetime import datetime
import numpy as np
import json, re
import requests
import matplotlib
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_agg import FigureCanvasAgg

plt.rcParams['font.sans-serif'] = ['FangSong']  # 设置默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时'-'显示为方块的问题


def get_daily_cn():
    """获取全国每日数据"""
    time_stamp = int(time.time()) * 1000
    url = f'https://interface.sina.cn/news/wap/fymap2020_data.d.json?_={time_stamp}&callback='
    resp = requests.get(url=url, )
    resp_data = resp.content.decode("unicode_escape")
    raw_data = json.loads(re.search("\(+([^)]*)\)+", resp_data).group(1)).get('data')['historylist']
    
    # 处理数据
    cn_conNum_list = list()  # 确诊
    cn_deathNum_list = list()  # 死亡
    cn_cureNum_list = list()  # 治愈
    cn_susNum_list = list()  # 疑似
    date_list = list()
    for item in raw_data:
        month, day = item['date'].split('.')
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))
        cn_conNum_list.append(int(item.get('cn_conNum', 0)))
        cn_deathNum_list.append(int(item.get('cn_deathNum', 0)))
        cn_cureNum_list.append(int(item.get('cn_cureNum', 0)))
        cn_susNum_list.append(item.get('cn_susNum', 0))

    cn_susNum_list = [x for x in cn_susNum_list if x is not None]
    for i in range(len(cn_conNum_list) - len(cn_susNum_list)):
        cn_susNum_list.append(1)
    cn_susNum_list = [int(x) for x in cn_susNum_list]
    
    return cn_conNum_list, cn_deathNum_list, cn_susNum_list, cn_cureNum_list, date_list


def plot_date():
    """绘制全国每日疫情数据折线图"""
    cn_conNum_list, cn_deathNum_list, cn_susNum_list, cn_cureNum_list, date_list = get_daily_cn()
    plt.figure('2019-nCoV疫情统计图表', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('2019-nCoV疫情全国数据折线图', fontsize=20)
    
    plt.plot(date_list, cn_conNum_list, label='确诊')
    plt.plot(date_list, cn_susNum_list, label='疑似')
    plt.plot(date_list, cn_deathNum_list, label='死亡')
    plt.plot(date_list, cn_cureNum_list, label='治愈')
    
    ax = plt.gca().xaxis
    ax.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))  # 格式化时间轴标注
    ax.set_major_locator(matplotlib.dates.DayLocator(bymonthday=None, interval=1, tz=None))
    plt.gcf().autofmt_xdate()  # 优化标注（自动倾斜）
    plt.grid(linestyle=':')  # 显示网格
    plt.xlabel('日期', fontsize=16)
    plt.ylabel('人数', fontsize=16)
    plt.legend(loc='best')
    plt.savefig('2019-nCoV.png')
    plt.show()


def china_value():
    """绘制全国每日疫情数据全国地图"""
    time_stamp = int(time.time()) * 1000
    url = f'https://interface.sina.cn/news/wap/fymap2020_data.d.json?_={time_stamp}&callback='
    resp = requests.get(url=url, )
    resp_data = resp.content.decode("unicode_escape")
    raw_data = json.loads(re.search("\(+([^)]*)\)+", resp_data).group(1)).get('data')['list']
    
    # 处理数据，获取每个省份确诊数据
    china_all = list()
    city_value = {}
    for item in raw_data:
        city = item.get('name')
        value = item.get('value')
        city_value[city] = int(value)
        china_all.append(city_value)
    
    return city_value


def plot_distribution():
    """绘制行政区域确诊分布数据"""
    china_data = china_value()
    print(china_data)
    # 经纬度范围
    lat_min = 10  # 纬度
    lat_max = 60
    lon_min = 70  # 经度
    lon_max = 140
    
    font = FontProperties(fname='simsun/simsun.ttf', size=14)
    # 标签颜色和文本
    legend_handles = [
        matplotlib.patches.Patch(color='#7FFFAA', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0),
    ]
    legend_labels = ['0人', '1-10人', '11-100人', '101-1000人', '>1000人']
    
    fig = plt.figure(facecolor='#f4f4f4', figsize=(10, 8))
    # 新建区域
    axes = fig.add_axes(
        (0.1, 0.1, 0.8, 0.8))  # left, bottom, width, height, figure的百分比,从figure 10%的位置开始绘制, 宽高是figure的80%
    axes.set_title('全国新型冠状病毒疫情地图（确诊）', fontsize=20)  # fontproperties=font 设置失败
    # bbox_to_anchor(num1, num2),  num1用于控制legend的左右移动，值越大越向右边移动，num2用于控制legend的上下移动，值越大，越向上移动。
    axes.legend(legend_handles, legend_labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=5)  # prop=font
    
    china_map = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min, urcrnrlat=lat_max, resolution='l',
                        ax=axes)
    # labels=[True,False,False,False] 分别代表 [left,right,top,bottom]
    china_map.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 0])  # 画经度线
    china_map.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])  # 画纬度线
    china_map.drawcoastlines(color='black')  # 洲际线
    china_map.drawcountries(color='red')  # 国界线
    china_map.drawmapboundary(fill_color='aqua')
    # 画中国国内省界和九段线
    china_map.readshapefile('china-shapefiles-master/china', 'province', drawbounds=True)
    china_map.readshapefile('china-shapefiles-master/china_nine_dotted_line', 'section', drawbounds=True)
    
    global count_iter
    count_iter = 0
    
    # 内外循环不能对调，地图中每个省的数据有多条(绘制每一个shape，可以去查一下第一条“台湾省”的数据)
    for info, shape in zip(china_map.province_info, china_map.province):
        pname = info['OWNER'].strip('\x00')
        fcname = info['FCNAME'].strip('\x00')
        if pname != fcname:  # 不绘制海岛
            continue
        is_reported = False  # 西藏没有疫情，数据源就不取不到其数据
        for prov_name in china_data.keys():
            count_iter += 1
            if prov_name in pname:
                is_reported = True
                if china_data[prov_name] == 0:
                    color = '#f0f0f0'
                elif china_data[prov_name] <= 10:
                    color = '#ffaa85'
                elif china_data[prov_name] <= 100:
                    color = '#ff7b69'
                elif china_data[prov_name] <= 1000:
                    color = '#bf2121'
                else:
                    color = '#7f1818'
                break
        
        if not is_reported:
            color = '#7FFFAA'
        poly = Polygon(shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)
        
    axes.legend(legend_handles, legend_labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font)
    axes.set_title("2019-nCoV疫情地图", fontproperties=font)
    FigureCanvasAgg(fig)
    fig.savefig('2019-nCoV疫情地图.png')


if __name__ == '__main__':
    plot_date()
    plot_distribution()
