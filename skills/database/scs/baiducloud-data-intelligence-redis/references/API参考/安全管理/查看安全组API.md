# 查看安全组API

## 请求说明

通过调用API来查看Redis设置的安全组。

## 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/securityGroup HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |

## 返回头域

除公共头域，无其它特殊头域。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| groups | List<Group> | 安全组列表。 |
| activeRules | List<Rule> | 安全组规则列表。 |

## Group

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| securityGroupRemark | String | 安全组备注。 |
| securityGroupName | String | 安全组名称。 |
| securityGroupId | String | 安全组ID。 |
| securityGroupUuid | String | 安全组长ID。 |
| vpcId | String | vpcId。 |
| vpcName | String | vpc名称。 |
| outbound | List<Rule> | 安全组规则。 |

## Rule

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| id | String | 安全组规则ID。 |
| securityGroupRuleId | String | 安全组规则ID。 |
| securityGroupId | String | 安全组ID。 |
| securityGroupUuid | String | 安全组长ID。 |
| direction | String | 入站/出站，取值ingress/Ingress或egress/Egress。 |
| ethertype | String | 网络类型，取值IPv4或IPv6。值为空时表示默认取值IPv4。 |
| protocol | String | 协议类型，tcp、udp或icmp，值为空时默认取值all。 |
| portRange | String | 端口范围，可以指定80等单个端口，值为空时默认取值1-65535。 |
| remoteGroupId | String | 源安全组ID。 |
| remoteGroupName | String | 源安全组名称。 |
| remoteIP | String | 源IP地址。 |
| name | String | 安全组规则名称。 |

## 请求示例

Plain Text

```
GET /v1/instance/scs-bdbl-ynqvbwopdesj/securityGroup HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "groups": [
        {
            "securityGroupRemark": "default",
            "securityGroupName": "默认安全组",
            "securityGroupId": "g-0qdtc2bzp0gd",
            "securityGroupUuid": "a825fdcd-9533-4bc2-8084-05a01952ceb7",
            "vpcId": "vpc-e20k5jh5afv2",
            "vpcName": "默认私有网络",
            "outbound": [
                {
                    "tenantId": "d443fbaf17e044d587701d7f4fdb9bd6",
                    "id": "r-lz1iqYEg",
                    "securityGroupRuleId": "r-lz1iqYEg",
                    "securityGroupId": "g-0qdtc2bzp0gd",
                    "securityGroupUuid": "a825fdcd-9533-4bc2-8084-05a01952ceb7",
                    "direction": "Egress",
                    "ethertype": "IPv4",
                    "protocol": "",
                    "portRange": "",
                    "remoteGroupId": "",
                    "remoteIP": "",
                    "name": ""
                }
            ],
            "inbound": [
                {
                    "tenantId": "d443fbaf17e044d587701d7f4fdb9bd6",
                    "id": "r-f1y3ruc1rzrb",
                    "securityGroupRuleId": "r-f1y3ruc1rzrb",
                    "securityGroupId": "g-0qdtc2bzp0gd",
                    "securityGroupUuid": "a825fdcd-9533-4bc2-8084-05a01952ceb7",
                    "direction": "Ingress",
                    "ethertype": "IPv6",
                    "protocol": "",
                    "portRange": "",
                    "remoteGroupId": "",
                    "remoteIP": "",
                    "name": ""
                }
            ],
            "projectId": "scs-bdbl-ynqvbwopdesj"
        }
    ],
    "activeRules": [
        {
            "tenantId": "d443fbaf17e044d587701d7f4fdb9bd6",
            "id": "r-r2qdz2sax6w1",
            "securityGroupRuleId": "r-r2qdz2sax6w1",
            "securityGroupId": "g-0qdtc2bzp0gd",
            "securityGroupUuid": "a825fdcd-9533-4bc2-8084-05a01952ceb7",
            "direction": "egress",
            "ethertype": "IPv6",
            "protocol": "",
            "portRange": "",
            "remoteGroupId": "",
            "remoteIP": "",
            "name": ""
        }
    ]
}
```
