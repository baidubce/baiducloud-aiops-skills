# BCM alarm policy and control-plane CLI contract

## Read operations

| Intent | Operation |
| --- | --- |
| list/detail policies | `DescribeAlarmPolicies`, `DescribeAlarmPolicy` |
| resource/metric metadata | `DescribeResourceCatalogs`, `DescribeMetricCatalogs` |
| system rule suggestions | `DescribeSystemTemplateRules` |
| instance groups | `DescribeInstanceGroups`, `DescribeInstanceGroup` |
| notification templates | `DescribeNotifyTemplates`, `DescribeNotifyTemplate` |
| receiver lookup | `DescribeReceivers` |

Always paginate list APIs with their advertised page or marker scheme and bound displayed output. Resolve partial-name results to exact IDs before mutation.

## Policy mutations

| Intent | Operation |
| --- | --- |
| create/update | `CreateAlarmPolicy`, `UpdateAlarmPolicy` |
| enable/disable policies | `UpdateAlarmPolicyState` |
| add/remove notification bindings | `AddAlarmPolicyActions`, `DeleteAlarmPolicyActions` |
| delete | `DeleteAlarmPolicies` |

Create accepts no `state` field and defaults to enabled in the manager. `notifyEnabled=false` suppresses notification delivery but does not itself suppress alarm history after dispatcher admission. Resource-deletion, PaaS, and other dispatcher filters remain independent. Update requires the current full mutable policy shape plus `id` and `state`; read the current policy immediately before constructing an update.

Do not send `version` or `action` manually. Policy body has no top-level `region`; put the business region only at `target.region` for `INSTANCES`. Keep global `--region`, profile, endpoint, scheme, output, query, timeout, and dry-run flags outside JSON.

## Related control-plane resources

Alarm templates use `CreateAlarmTemplate`, `UpdateAlarmTemplate`, `DeleteAlarmTemplates`, list/detail operations, import/export, and `DescribeSystemTemplateRules`. Instance groups and notification templates have their own CRUD operations. Treat each as an independent mutation with a separate preview and confirmation because one object can affect many policies.

Alarm masking has a separate request shape, helper, and execution workflow. Read [alarm-masking-cli-contract.md](alarm-masking-cli-contract.md) before any masking operation; do not reuse the alarm-policy target schema or validator.

## Safe execution

1. Generate the current operation skeleton.
2. Validate JSON and strip generated `version`.
3. Run the exact command with `--dry-run`.
4. Show an impact summary with no raw callback URL or receiver contact details.
5. Obtain immediate confirmation.
6. Execute once.
7. Read back by exact ID.

## Timed-out mutation reconciliation

Before mutation, record the UTC start time and the exact pre-mutation object or a bounded candidate set. If the mutation times out, never repeat it automatically:

- **Create:** list only the already confirmed `scope/resourceType` and exact name, bounded to objects created or updated around the recorded start time. Compare target, rules, no-data behavior, `notifyEnabled`, and action bindings. If exactly one candidate matches, read it by exact ID and verify every intended non-secret field. Zero or multiple matches leave the outcome unknown.
- **Update or state change:** read the exact object ID and compare the intended mutable fields or state. Report complete only on a full match. An unchanged or partially changed object is not permission to retry.
- **Action binding:** read the exact policy and compare the resulting action/template ID set, not display names.
- **Delete:** read the exact ID. Treat a confirmed not-found result as the intended final state only when the response is not an authentication, authorization, routing, or transient service error.
- **Template or instance-group mutation:** read the exact ID when available; otherwise use the narrowest unique name and creation-time window and require a single full-field match.

Allow at most one identical read retry when propagation delay or a transient read failure is plausible. If the result remains absent, ambiguous, or partial, report the evidence and stop. Any later mutation attempt requires a new current-state read, a new dry-run and impact summary, and fresh confirmation.

Preserve a returned service `requestId` for logs or support investigation. It is not an idempotency token and must not be used as proof that the mutation succeeded or failed unless a future documented operation explicitly supports that query.

Do not use `--debug` by default. Callback URL user info, path tokens, query strings, signed headers, receiver phone numbers, and email addresses are sensitive.
