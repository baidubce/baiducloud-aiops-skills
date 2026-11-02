# API概览

## 实例相关接口

| 接口名称 | 接口功能 |
| --- | --- |
| [创建主实例](https://cloud.baidu.com/doc/RDS/s/Dka65m22p) | 调用API接口创建RDS实例 |
| [创建只读实例](https://cloud.baidu.com/doc/RDS/s/7ka65mz34) | 调用API接口创建只读实例 |
| [创建代理实例](https://cloud.baidu.com/doc/RDS/s/4ka65nv81) | 调用API接口创建代理实例 |
| [查询实例列表](https://cloud.baidu.com/doc/RDS/s/6ka65oy9l) | 调用API接口查询实例列表 |
| [查询指定实例详情](https://cloud.baidu.com/doc/RDS/s/fka65tbm6) | 调用API接口查询指定实例详情 |
| [删除实例](https://cloud.baidu.com/doc/RDS/s/Ika65unzt) | 调用API接口释放实例 |
| [重启实例](https://cloud.baidu.com/doc/RDS/s/Nka65vo3e) | 调用API接口重启实例 |
| [修改实例名称](https://cloud.baidu.com/doc/RDS/s/Cka666y1f) | 调用API接口修改目标实例名称 |
| [修改同步模式](https://cloud.baidu.com/doc/RDS/s/hka668z5u) | 调用API接口设置主备实例之间的数据复制方式，以提高云数据库可用性 |
| [修改连接信息](https://cloud.baidu.com/doc/RDS/s/hka66b24j) | 调用API接口修改域名前缀信息 |
| [开关公网访问](https://cloud.baidu.com/doc/RDS/s/Dka66bhf8) | 如果有公网访问需求，可以通过此 API 接口开/关公网访问 |
| [实例扩缩容](https://cloud.baidu.com/doc/RDS/s/jka66dcbl) | 为指定云数据库 RDS 所用资源扩缩容，目前支持对主实例或只读实例的内存、磁盘、cpu数进行扩缩容操作，支持对代理实例的节点数做扩缩容操作 |

## 账号管理

| 接口名称 | 接口功能 |
| --- | --- |
| [创建账号](https://cloud.baidu.com/doc/RDS/s/Mka64ss3k) | 在某个主实例下创建一个新的账号 |
| [查询账号列表](https://cloud.baidu.com/doc/RDS/s/Rka651dzq) | 查看指定实例的账号列表 |
| [查询特定账号信息](https://cloud.baidu.com/doc/RDS/s/Eka653sdc) | 获取一个账号信息(包括授权信息) |

## 备份管理

| 接口名称 | 接口功能 |
| --- | --- |
| [修改备份策略](https://cloud.baidu.com/doc/RDS/s/Kka66c4w4) | 调用API接口修改备份策略 |
| [获取备份列表](https://cloud.baidu.com/doc/RDS/s/Hka65ex1w) | 获取一个实例下的备份列表 |
| [获取备份信息](https://cloud.baidu.com/doc/RDS/s/ika65gbxm) | 调用API接口获取备份信息 |

## 参数管理

| 接口名称 | 接口功能 |
| --- | --- |
| [获取参数列表](https://cloud.baidu.com/doc/RDS/s/jka65sjbq) | 返回该实例下数据库参数列表 |
| [修改配置参数](https://cloud.baidu.com/doc/RDS/s/1ka65tdrg) | 修改云数据库的参数配置 |

## 慢日志下载任务

| 接口名称 | 接口功能 |
| --- | --- |
| [获取慢日志管理任务列表](https://cloud.baidu.com/doc/RDS/s/qkvw0sgi0) | 调用API接口查询实例下的慢日志下载任务列表 |
| [获取慢日志下载任务详情](https://cloud.baidu.com/doc/RDS/s/Bkvw1lzlh) | 调用API接口查询慢日志下载任务详情 |

## 其他

| 接口名称 | 接口功能 |
| --- | --- |
| [获取可用区列表](https://cloud.baidu.com/doc/RDS/s/zka65zqz2) | 调用API接口获取可用区列表 |
| [获取子网列表](https://cloud.baidu.com/doc/RDS/s/Wka66184u) | 调用API接口获取子网列表 |
| [查看白名单](https://cloud.baidu.com/doc/RDS/s/Cka65mski) | 调用API接口查看白名单 |
| [更新白名单](https://cloud.baidu.com/doc/RDS/s/Uka65osab) | 白名单全量更新 |
