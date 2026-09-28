# Domain 7 question review

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q18 | [`11_connections_network_rules_preflight.py`](../11_connections_network_rules_preflight.py) | L11 `connections.bicep` keyless `AIServices` connection shared by the project's apps | Existing |
| Q70 | [`01_security_operations_preflight.py`](01_security_operations_preflight.py) | `questions/01_security_operations_preflight.py` | New |
| Q89 | [`04_cicd_preflight.py`](../04_cicd_preflight.py) | L04 CI/CD OIDC | Existing |
| Q119 | [`11_connections_network_rules_preflight.py`](../11_connections_network_rules_preflight.py) | L11 `connections.bicep`: category `AzureKeyVault`, authType `AccountManagedIdentity` | Existing |
| Q129 | [`11_connections_network_rules_preflight.py`](../11_connections_network_rules_preflight.py), [`01_bicep_preflight.py`](../01_bicep_preflight.py) | L11 `az cognitiveservices account ... --encryption`; L01 Bicep CMK | Existing; partial: prints `--kind AIServices`; the exam's Azure OpenAI resource uses `--kind OpenAI` with the same `--encryption` flag |
| Q156 | [`11_connections_network_rules_preflight.py`](../11_connections_network_rules_preflight.py) | L11 virtual network rules with default Deny on the resource | Existing |
| Q157 | [`11_connections_network_rules_preflight.py`](../11_connections_network_rules_preflight.py) | L11 resource network settings plus a `Microsoft.CognitiveServices` service endpoint on the subnet | Existing |

The security-operations supplement is read-only. It does not create a Sentinel workspace or diagnostic export. See [`../../docs/question-coverage.md`](../../docs/question-coverage.md#07---production-platform).
