# 使用说明

- 设置`config.json`的参数，每次运行都会实时读取参数，无需重启程序。
- 需要手动添加`id`
- 需要将`steam_appid.txt`放在`steamapps\common\ELDEN RING NIGHTREIGN\Game`,其内容不要修改
- 手动运行`nightreign.exe`，注意不要用`steam`运行，没有看到小蓝熊启动并且游戏内弹出无法联网就表示运行成功。
- SL 模式，使用`config.json`即可
- 作弊模式，使用`config.json.back`更名为`config.json`即可
- `Alt+1` 启动
- `Alt+0` 退出
- `Alt+2` 锁定暗痕/王证

## 首次运行
需要执行安装依赖包
```bash
pip install -r requirements.txt
```



## 作弊模式说明
需要设置`lock`为`true`
然后想抽什么就将焦点聚焦到该物品上
![聚焦](/images/1.png)
按下`alt+1`开始自动抽奖，过程中不要移动鼠标和键盘，否则会导致识别失败。

作弊模式就是锁定了暗痕和王证，然后抽遗物，过程中不会消耗暗痕和王证，省区SL的时间

## 参数说明

`item`参数说明：
- `color`：物品颜色，为空表示不限制。
    - 颜色关键字 : `r`,`y`,`g`,`b`
- `size`：物品大小，为空表示不限制。
    - 大小关键字 : `b`,`m`,`s`
- `keyword1` - `keyword3`：物品名称关键词1-3，为空表示不限制。
- `keyword4`：全局黑名单，只要有这个字眼都算不匹配。

`lock`参数说明：
- `lock`：表示锁定`暗痕`和`王证`

`regions` 参数说明：
  - 识别区域 `2560 * 1440`不需要设置

`times`参数说明：
- `times`：表示整体执行次数，默认值为`1`。

`save`和`load`参数说明：
- 不需要管

`actions`表示动作:

## actions参数
还原存档
```json
{
   "type" : "load" 
}
```

备份存档
```json
{
   "type" : "save" 
}
```

### 识别进入游戏 enter
等待`delay`秒后,每隔`wait`秒后在`coords`区域内找到`image`,如果没有找到,模拟按下`key`,一直等待匹配到`image`
```json
{
    "type": "enter", 
    "key": "f",
    "tips": "进入游戏",
    "delay": 0.5,
    "image": "/images/anhen.png",
    "coords": [
        2228.0,
        1326.0,
        2284.0,
        1376.0
    ],
    "wait": 0.5,
    "times": 1
}
```

### 模拟按键 action
等待`delay`秒后,模拟按下`key`,执行`times`次
```json
{
    "type": "action", 
    "key": "f",
    "tips": "模拟按下f",
    "delay": 0.5,
    "times": 1
}
```

### 抽遗物 roll
等待`delay`秒后,进行识别，若识别成功则执行`success`，若识别失败则执行`failure`,执行`times`次

`success`参数说明：
- `delay`：表示执行`key`前等待的秒数，默认值为`0`。
- `key`：表示执行的按键，支持多个按键，用`,`隔开。
    - 按键关键字 : `left`,`right`,`up`,`down`,`enter`,`esc`,`f1`-`f12`

`failure`参数说明：
- `delay`：表示执行`key`前等待的秒数，默认值为`0`。
- `key`：表示执行的按键，支持多个按键，用`,`隔开。
    - 按键关键字 : `left`,`right`,`up`,`down`,`enter`,`esc`,`f1`-`f12`



```json
{
    "type": "roll",
    "tips": "刷遗物启动",
    "delay": 0.1,
    "times": 10,
    "success": {
        "delay": 0.1,
        "key": [
            "2",
            "right"
        ]
    },
    "failure": {
        "delay": 0.1,
        "key": [
            "3"
        ]
    }
}
```
