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

配置文件为`config.json`,默认在工具目录下

你需要设置: `id` 

通过`win+r`输入`%APPDATA%\Nightreign`即可看到自己的`id`

### 配置项

- `id`: 你需要手动填写该项目
- `path` : 游戏目录,若没有设置则自动获取,如果有误则需要手动填写
- `terminal` : 终端配置,不建议修改
- `bd` : 词条配置详细请查看 [词条配置](#词条配置)
- `save` : 是否保存配置,不要修改,软件自动修改
- `load` : 是否加载配置,不要修改,软件自动修改
- `debug` : 是否开启调试模式,开启后会锁定暗痕和王证两个资源,不会发生变化
- `task` : 任务配置,详细请查看 [任务配置](#任务配置)


## 词条配置

你可以通过运行`setting.py`使用界面配置词条

## 任务配置

按下`alt+1`时开始任务,由于程序问题,没有办法在运行过程中停止,但你可以强制停止软件

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
