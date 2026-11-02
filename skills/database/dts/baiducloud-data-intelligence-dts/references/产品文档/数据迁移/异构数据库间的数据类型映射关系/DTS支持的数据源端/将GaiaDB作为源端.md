# 将GaiaDB作为源端

本文介绍源端为GaiaDB-S时如何配置DTS任务

## 前置条件

1. 账号下有可用的GaiaDB-S实例(详情见 [GaiaDB-S操作指南](https://cloud.baidu.com/doc/GaiaDB/index.html))。
2. 若需DTS任务具备高可用，需保证可用节点至少为2个。

## 配置任务

1. 进入DTS控制台界面。
2. 点击创建实例。

   ![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_8d4697a.png)
3. 选择百度智能云数据库，接入类型选择GaiaDB-S，选择地域后下单。

   ![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6ab42b7.png)
4. 创建完成后，在列表操作列点击配置任务进行配置。

   ![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7ed40b4.png)
5. 点击选择实例ID下拉框选择源端实例。
6. 按需配置目标端信息，点击授权白名单进入下一步按钮。(详情见 [配置任务](https://cloud.baidu.com/doc/DTS/s/Kjwvxjhs5))
