# 刷词条工具

## 运行环境

### 关闭小蓝熊
需要在游戏目录下`/game/steam_appid.txt`文件中添加以下内容：
```
2622380
```
没有则需要创建该文件

每次刷词条都需要手动执行`/game/nightreign.exe`,不要通过`Steam`启动游戏

正式游玩在`Steam`中启动游戏即可,`steam_appid.txt`不需要删除

## 配置文件

`config/config.json`
- `debug` : 是否开启调试模式,开启后会锁定暗痕和王证两个资源,不会发生变化

`/config/filters.json`
记录筛选条件,不建议手动修改,请使用进行修改
```cmd
py setting.py
```

`/config/terminal.json`
记录终端配置,不建议手动修改,请使用进行修改

`/config/task.json`
任务配置详细看下方设置即可

你需要设置: `id` 

通过`win+r`输入`%APPDATA%\Nightreign`即可看到自己的`id`

## 词条配置
你可以通过运行`setting.py`使用界面配置词条

## 任务配置

按下`alt+1`时开始任务,按下`num 9`关闭程序

每次运行都会读取`config.json`的`task`,因此不需要重启软件

### 任务配置说明
#### 模拟按键
```json
{
  "type": "key",
  "key": "f",
  "tips": "购买石头",
  "times": 1,
  "delay": 1
},
```
本次任务是模拟按键,`type = key`,等待`{delay}`秒后,模拟按下`{key}`键,重复`{times}`次,并在终端中打印`{tips}`

#### 分组
```json
{
    "type":"group",
    "times": 1,
    "delay": 1,
    "tips": "购买",
    "task":[
        {
            "type":"key",
            "key":"f",
            "tips":"购买石头",
            "times":1,
            "delay":1
        }
    ]
}
```
本次任务是分组,它可以让你重复执行一组任务,等待`{delay}`秒后,重复执行`{times}`次`{task}`的内容

#### 抽取
```json
{
    "type": "roll",
    "tips": "开始筛选石头",
    "times": 10,
    "delay": 0.0,
    "success": {
      "tips": "找到匹配的石头",
      "interval": 0,
      "key": [
        "2",
        "right"
      ]
    },
    "failure": {
      "tips": "没有找到匹配的石头",
      "interval": 0,
      "key": [
        "3"
      ]
    }
}
```
等待`{delay}`秒后,抽取`{times}`次,如果成功则模拟按下`{success.key}`键,并在终端中打印`{success.tips}`,否则模拟按下`{failure.key}`键,并在终端中打印`{failure.tips}`

若有一次匹配,那么它会要求系统存档一次,若匹配失败,那么就会要求系统读档一次


## 完整购买任务

```json
{
  "id": "",
  "path": "",
  "regions": [
    2231,
    1330,
    2280,
    1376
  ],
  "save": false,
  "load": true,
  "tasks": [
    {
      "type": "load",
      "tips": "加载配置",
      "times": 1,
      "delay": 0.5
    },
    {
      "type": "game",
      "tips": "等待游戏加载",
      "image": "/asset/anhen.png",
      "key": "f",
      "interval": 0.1,
      "times": 1,
      "delay": 0.5
    },
    {
      "type": "key",
      "key": "m",
      "tips": "打开地图",
      "times": 1,
      "delay": 0.5
    },
    {
      "type": "key",
      "key": "down",
      "tips": "找到商人面板",
      "times": 6,
      "delay": 0
    },
    {
      "type": "key",
      "key": "f",
      "tips": "跳转到商人",
      "times": 1,
      "delay": 0
    },
    {
      "type": "key",
      "key": "up",
      "tips": "找到情景原石(无版本的)",
      "times": 1,
      "delay": 1.5
    },
    {
      "type": "key",
      "key": "f",
      "tips": "购买石头",
      "times": 1,
      "delay": 0
    },
    {
      "type": "key",
      "key": "down",
      "tips": "修改购买数量",
      "times": 1,
      "delay": 0.1
    },
    {
      "type": "lock",
      "tips": "锁定暗痕和王证数量",
      "times": 1,
      "delay": 0
    },
    {
      "type": "key",
      "key": "f",
      "tips": "确认购买",
      "times": 1,
      "delay": 0.1
    },
    {
      "type": "key",
      "key": "f",
      "tips": "跳过动画",
      "times": 1,
      "delay": 0.5
    },
    {
      "type": "roll",
      "tips": "开始筛选石头",
      "times": 10,
      "delay": 0.1,
      "success": {
        "tips": "找到匹配的石头",
        "interval": 0.1,
        "key": [
          "2",
          "right"
        ]
      },
      "failure": {
        "tips": "没有找到匹配的石头",
        "interval": 0.1,
        "key": [
          "3"
        ]
      }
    },
    {
      "type": "lock",
      "tips": "还原暗痕和王证数量",
      "times": 1,
      "delay": 0
    },
    {
      "type": "group",
      "tips": "退出游戏",
      "times": 1,
      "delay": 0.1,
      "task": [
        {
          "type": "key",
          "key": "esc",
          "tips": "打开菜单",
          "times": 2,
          "delay": 0.1
        },
        {
          "type": "key",
          "key": "f1",
          "tips": "选择系统菜单",
          "times": 1,
          "delay": 0.1
        },
        {
          "type": "key",
          "key": "up",
          "tips": "选择结束游戏",
          "times": 1,
          "delay": 0.1
        },
        {
          "type": "key",
          "key": "f",
          "tips": "确认结束游戏",
          "times": 2,
          "delay": 0.1
        },
        {
          "type": "key",
          "key": "left",
          "tips": "确认退出游戏",
          "times": 1,
          "delay": 0.1
        },
        {
          "type": "key",
          "key": "f",
          "tips": "确认退出游戏",
          "times": 1,
          "delay": 0.1
        }
      ]
    },
    {
      "type": "save",
      "tips": "保存配置",
      "times": 1,
      "delay": 2
    }
  ]
}
```