# 阿里云MySQL迁移至RDS MySQL

## 概览

本文主要介绍通过DTS数据迁移功能从阿里云MySQL迁移至百度智能云RDS。

## 需求场景

适用于使用百度智能云数据传输服务DTS，将阿里云RDS MySQL的数据在不停服的情况下，在线热迁移到百度智能云RDS中。

## 方案概述

数据传输服务DTS支持第三方云厂商MySQL同步至百度智能云RDS中，实现结构同步、全量数据同步和增量数据的实时同步。

## 操作步骤

### 环境准备

* 阿里云RDS MySQL 5.6实例。
* 百度智能云RDS MySQL 5.6实例。

### 检查阿里云云数据库公网访问

1. 登录阿里云访问控制台，进入待迁移实例的详情页。
2. 在实例Tab「基本信息」中检查实例的「外网地址」是否已开通。若未开通，则点击「申请外网地址」按钮并根据提示进行操作。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_01.png)
3. 对于已经开通的实例，记录「外网地址」及「外网端口」，供后面的步骤使用。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_02.png)
4. 进入实例Tab「数据安全性」，在白名单设置页签中，编辑该实例所绑定的白名单组，允许DTS服务器的访问。具体DTS公网IP段请参考：[添加 DTS 服务 IP 白名单](https://cloud.baidu.com/doc/DTS/s/cjwvxji7o)。

### 检查阿里云云数据库参数设置

1. 在实例详情页，进入实例Tab「参数设置」。
2. 在参数列表中，检查参数是否符合要求：「binlog\_row\_format」的值等于「FULL」。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_03.png)
3. 默认状态下，阿里云云数据库MySQL实例的参数值符合要求，无需修改。若参数值不符合要求，则需要点击参数值旁的编辑按钮进行修改。

### 对迁移账号进行授权

1. 使用MySQL管理员账号连接阿里云云数据库实例。可以在命令行中执行「mysql -h外网地址-u 高权限账号 -p -P 外网端口」，其中中文部分根据实例实际的外网地址/端口、账号自行替换。
2. 连接后，进行授权操作。您可以对准备用于迁移的已有账号进行授权，也可以创建新的账号用于迁移，请参考如下授权语句：
   `GRANT SELECT, LOCK TABLES, REPLICATION SLAVE, REPLICATION CLIENT, SHOW VIEW ON ∗.∗ TO '迁移账号'@'主机名' IDENTIFIED BY '迁移密码';`，
   其中「迁移账号」和「迁移密码」请按需自行填写；「主机名」可参考 [DTS公网IP段](https://cloud.baidu.com/doc/DTS/s/cjwvxji7o) 进行填写，实现仅对DTS服务器IP放开访问限制，或填写`%`对全部IP开放访问。
3. 授权完成后，继续刷新系统权限表，确保账号权限立即生效。执行「FLUSH PRIVILEGES;」即可。

## 创建百度智能云DTS迁移任务

### 源库及目标库配置

1. 登录百度智能云访问控制台，购买数据迁移实例。
2. 点击「配置任务」按钮，开始对实例进行迁移任务的配置。
3. 根据需要填写「任务名称」；在「源库信息」中，实例类型选择「公网自建数据库」，数据库引擎选择「MySQL」，然后填入阿里云云数据库实例的外网地址/端口，以及用于迁移的账号信息；「目标库信息」中，选择作为迁移目标的百度智能云RDS实例。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_04.png)
4. 点击「授权白名单进入下一步」按钮继续配置迁移类型及库表。

### 迁移类型及库表

1. 在「迁移类型」中勾选：结构、全量、增量。
2. 在「源库对象」框中选中需要迁移的对象，然后点击「添加所选」按钮，对象出现在「已选择对象」框中。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_05.png)
3. 如果需要更改迁移对象在目标库中的名称，可以点击对象右侧的编辑按钮进行重命名。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_06.png)
   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_07.png)
4. 点击「保存并预检查」开始预检查

### 任务校验及启动

1. 稍等片刻，页面显示任务校验成功。

   ![](https://doc.bce.baidu.com/bce-documentation/DTS/DTS_BestPractise_08.png)
2. 点击「立即开启任务」按钮即可启动任务。

## 相关产品

[云数据库 RDS](https://cloud.baidu.com/doc/RDS/s/ujwvyzdzg)：专业、高性能、高可靠的关系型数据库
