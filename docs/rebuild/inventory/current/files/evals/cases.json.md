# `evals/cases.json`

- 형식: `100644`
- 바이트: 18545
- SHA-256: `8cfb1c3e4f217a29d4dc1d31008e4f62d5e961589cdf09a21cb89ec2f232c60e`
- 인코딩: `utf-8`

```
{
  "schema_version": 1,
  "cases": {
    "bounds": {
      "prompt": "범위 밖 값이 제대로 안 잡히는데 고쳐봐.",
      "fixture": "bounds",
      "module": "mathlib.py",
      "function": "clamp",
      "allowed_edits": [
        "mathlib.py",
        "test_mathlib.py"
      ],
      "checks": [
        {
          "args": [
            -3,
            0,
            10
          ],
          "expected": 0
        },
        {
          "args": [
            15,
            0,
            10
          ],
          "expected": 10
        },
        {
          "args": [
            5,
            0,
            10
          ],
          "expected": 5
        },
        {
          "args": [
            -1.5,
            -1,
            2
          ],
          "expected": -1
        },
        {
          "args": [
            3,
            3,
            3
          ],
          "expected": 3
        },
        {
          "args": [
            0,
            10,
            1
          ],
          "error": "ValueError"
        }
      ]
    },
    "merge-records": {
      "prompt": "중복된 항목 합치면 값이 자꾸 사라짐. 고쳐줘.",
      "fixture": "merge-records",
      "module": "records.py",
      "function": "merge_records",
      "allowed_edits": [
        "records.py",
        "test_records.py",
        "app.py"
      ],
      "checks": [
        {
          "args": [
            [
              {
                "id": "a",
                "name": "사진"
              },
              {
                "id": "a",
                "count": 2
              }
            ]
          ],
          "expected": [
            {
              "id": "a",
              "name": "사진",
              "count": 2
            }
          ]
        },
        {
          "args": [
            [
              {
                "id": "a",
                "count": 1
              },
              {
                "id": "b",
                "count": 5
              },
              {
                "id": "a",
                "count": 3
              }
            ]
          ],
          "expected": [
            {
              "id": "a",
              "count": 3
            },
            {
              "id": "b",
              "count": 5
            }
          ]
        },
        {
          "args": [
            []
          ],
          "expected": []
        },
        {
          "args": [
            [
              {
                "id": 0,
                "name": "영"
              },
              {
                "id": 0,
                "count": 1
              }
            ]
          ],
          "expected": [
            {
              "id": 0,
              "name": "영",
              "count": 1
            }
          ]
        },
        {
          "args": [
            [
              {
                "name": "ID 없음"
              }
            ]
          ],
          "error": "ValueError"
        }
      ],
      "preserve_arguments": true,
      "integrations": [
        {
          "module": "app.py",
          "function": "summarize",
          "preserve_arguments": true,
          "checks": [
            {
              "args": [
                [
                  {
                    "id": "a",
                    "name": "사진"
                  },
                  {
                    "id": "a",
                    "count": 2
                  }
                ]
              ],
              "expected": {
                "items": [
                  {
                    "id": "a",
                    "name": "사진",
                    "count": 2
                  }
                ]
              }
            },
            {
              "args": [
                []
              ],
              "expected": {
                "items": []
              }
            },
            {
              "args": [
                [
                  {
                    "name": "ID 없음"
                  }
                ]
              ],
              "error": "ValueError"
            }
          ]
        }
      ]
    },
    "inspect-only": {
      "prompt": "왜 음수가 그대로 나옴? 원인만 찾아. 수정 ㄴㄴ.",
      "fixture": "bounds",
      "allowed_edits": [],
      "requires_human_review": true
    },
    "report-export": {
      "prompt": "CSV로도 뽑을 수 있게 해줘. 내가 바꾼 파일명은 그대로 두고.",
      "fixture": "report-export",
      "module": "exports.py",
      "function": "to_csv",
      "allowed_edits": [
        "app.py",
        "exports.py",
        "test_app.py"
      ],
      "allowed_new_files": [
        "test_exports.py"
      ],
      "preexisting_edits": {
        "app.py": {
          "from": "DOWNLOAD_STEM = \"records\"",
          "to": "DOWNLOAD_STEM = \"현장 기록\""
        }
      },
      "preserve_arguments": true,
      "checks": [
        {
          "args": [
            []
          ],
          "expected": "id,name,note\r\n",
          "comparison": "csv"
        },
        {
          "args": [
            [
              {
                "id": 0,
                "name": "사진, 1",
                "note": "첫 줄\n둘째 \"줄\"",
                "ignored": "제외"
              }
            ]
          ],
          "expected": "id,name,note\r\n0,\"사진, 1\",\"첫 줄\n둘째 \"\"줄\"\"\"\r\n",
          "comparison": "csv"
        },
        {
          "args": [
            [
              {
                "id": "b",
                "name": "둘째"
              },
              {
                "id": "a",
                "note": "메모"
              }
            ]
          ],
          "expected": "id,name,note\r\nb,둘째,\r\na,,메모\r\n",
          "comparison": "csv"
        }
      ],
      "integrations": [
        {
          "module": "app.py",
          "function": "download",
          "preserve_arguments": true,
          "checks": [
            {
              "args": [
                [
                  {
                    "id": 0,
                    "name": "사진, 1",
                    "note": "첫 줄\n둘째 \"줄\"",
                    "ignored": "제외"
                  }
                ],
                "csv"
              ],
              "expected": {
                "filename": "현장 기록.csv",
                "media_type": "text/csv; charset=utf-8",
                "content": "id,name,note\r\n0,\"사진, 1\",\"첫 줄\n둘째 \"\"줄\"\"\"\r\n"
              },
              "comparison": "csv"
            },
            {
              "args": [
                [],
                "csv"
              ],
              "expected": {
                "filename": "현장 기록.csv",
                "media_type": "text/csv; charset=utf-8",
                "content": "id,name,note\r\n"
              },
              "comparison": "csv"
            },
            {
              "args": [
                [
                  {
                    "id": 0,
                    "name": "사진, 1",
                    "note": "첫 줄\n둘째 \"줄\"",
                    "ignored": "제외"
                  }
                ]
              ],
              "expected": {
                "filename": "현장 기록.json",
                "media_type": "application/json; charset=utf-8",
                "content": "[\n  {\n    \"id\": 0,\n    \"name\": \"사진, 1\",\n    \"note\": \"첫 줄\\n둘째 \\\"줄\\\"\",\n    \"ignored\": \"제외\"\n  }\n]"
              }
            },
            {
              "args": [
                [],
                "xml"
              ],
              "error": "ValueError"
            },
            {
              "args": [
                []
              ],
              "kwargs": {
                "format": "json"
              },
              "expected": {
                "filename": "현장 기록.json",
                "media_type": "application/json; charset=utf-8",
                "content": "[]"
              }
            }
          ]
        }
      ]
    },
    "resume-export": {
      "prompt": "아까 하던 거 이어서 끝내줘. 내가 바꾼 파일명은 그대로 두고.",
      "fixture": "resume-export",
      "oracle_case": "report-export",
      "prior_progress": "progress.json",
      "allowed_edits": [
        "app.py",
        "exports.py",
        "test_app.py",
        "test_exports.py"
      ],
      "allowed_new_files": [],
      "preexisting_edits": {
        "app.py": {
          "from": "DOWNLOAD_STEM = \"records\"",
          "to": "DOWNLOAD_STEM = \"현장 기록\""
        }
      }
    },
    "refactor-pricing": {
      "prompt": "여기 중복 심한데 좀 정리해줘. 쓰는 쪽 깨지면 안 됨.",
      "fixture": "refactor-pricing",
      "module": "pricing.py",
      "function": "member_total",
      "allowed_edits": [
        "pricing.py",
        "test_pricing.py"
      ],
      "required_edits": [
        "pricing.py"
      ],
      "checks": [
        {
          "args": [
            [
              {
                "price": 100,
                "count": 2
              }
            ],
            0.1
          ],
          "expected": 180.0
        },
        {
          "args": [
            [
              {
                "price": 100,
                "count": 2
              }
            ],
            0.0
          ],
          "expected": 200.0
        },
        {
          "args": [
            [],
            0.5
          ],
          "expected": 0
        },
        {
          "args": [
            [
              {
                "price": 19.99,
                "count": 3
              }
            ],
            0.15
          ],
          "expected": 50.97
        },
        {
          "args": [
            [
              {
                "price": 10,
                "count": -1
              }
            ],
            0.1
          ],
          "error": "ValueError"
        }
      ],
      "integrations": [
        {
          "module": "pricing.py",
          "function": "guest_total",
          "checks": [
            {
              "args": [
                [
                  {
                    "price": 100,
                    "count": 2
                  }
                ]
              ],
              "expected": 200.0
            },
            {
              "args": [
                []
              ],
              "expected": 0
            },
            {
              "args": [
                [
                  {
                    "price": 10,
                    "count": -1
                  }
                ]
              ],
              "error": "ValueError"
            }
          ]
        },
        {
          "module": "pricing.py",
          "function": "staff_total",
          "checks": [
            {
              "args": [
                [
                  {
                    "price": 100,
                    "count": 1
                  }
                ]
              ],
              "expected": 70.0
            },
            {
              "args": [
                [
                  {
                    "price": 10,
                    "count": -1
                  }
                ]
              ],
              "error": "ValueError"
            }
          ]
        },
        {
          "module": "checkout.py",
          "function": "receipt",
          "checks": [
            {
              "args": [
                [
                  {
                    "price": 100,
                    "count": 2
                  }
                ],
                "member"
              ],
              "expected": {
                "kind": "member",
                "total": 180.0
              }
            },
            {
              "args": [
                [
                  {
                    "price": 100,
                    "count": 1
                  }
                ],
                "staff"
              ],
              "expected": {
                "kind": "staff",
                "total": 70.0
              }
            },
            {
              "args": [
                [
                  {
                    "price": 100,
                    "count": 2
                  }
                ],
                "guest"
              ],
              "expected": {
                "kind": "guest",
                "total": 200.0
              }
            }
          ]
        }
      ]
    },
    "run-tests-only": {
      "prompt": "테스트만 한 번 돌려봐. 코드는 건드리지 마.",
      "fixture": "run-tests-only",
      "allowed_edits": [],
      "requires_execution": true,
      "module": "inventory.py",
      "function": "restock",
      "checks": [
        {
          "args": [
            [
              [
                "볼트",
                2
              ],
              [
                "너트",
                7
              ]
            ],
            5
          ],
          "expected": [
            [
              "볼트",
              5
            ],
            [
              "너트",
              7
            ]
          ]
        },
        {
          "args": [
            [],
            5
          ],
          "expected": []
        }
      ]
    },
    "dead-code": {
      "prompt": "안 쓰는 거 좀 지워줘. 쓰는 건 남기고.",
      "fixture": "dead-code",
      "module": "reporting.py",
      "function": "build_label",
      "allowed_edits": [
        "reporting.py",
        "test_reporting.py"
      ],
      "required_edits": [
        "reporting.py"
      ],
      "removed_symbols": {
        "reporting.py": [
          "legacy_csv_header"
        ]
      },
      "checks": [
        {
          "args": [
            "월간"
          ],
          "expected": "[월간]"
        },
        {
          "args": [
            ""
          ],
          "expected": "[]"
        }
      ],
      "integrations": [
        {
          "module": "reporting.py",
          "function": "summarize",
          "checks": [
            {
              "args": [
                [
                  {
                    "amount": 1000
                  },
                  {
                    "amount": 2500
                  }
                ]
              ],
              "expected": {
                "count": 2,
                "total": 3500
              }
            },
            {
              "args": [
                []
              ],
              "expected": {
                "count": 0,
                "total": 0
              }
            }
          ]
        },
        {
          "module": "reporting.py",
          "function": "format_currency",
          "checks": [
            {
              "args": [
                3500
              ],
              "expected": "3,500.00원"
            }
          ]
        },
        {
          "module": "reporting.py",
          "function": "to_json",
          "checks": [
            {
              "args": [
                [
                  {
                    "amount": 5
                  }
                ]
              ],
              "expected": "{\"count\": 1, \"total\": 5}"
            }
          ]
        },
        {
          "module": "dashboard.py",
          "function": "render",
          "checks": [
            {
              "args": [
                [
                  {
                    "amount": 1000
                  },
                  {
                    "amount": 2500
                  }
                ],
                "월간"
              ],
              "expected": "[월간] 2건 3,500.00원"
            }
          ]
        }
      ]
    },
    "test-encodes-bug": {
      "prompt": "5kg 딱 맞춰 보냈는데 추가요금이 붙는대. 규칙엔 5kg까진 무료라던데?",
      "fixture": "test-encodes-bug",
      "module": "shipping.py",
      "function": "shipping_fee",
      "allowed_edits": [
        "shipping.py",
        "test_shipping.py"
      ],
      "required_edits": [
        "shipping.py",
        "test_shipping.py"
      ],
      "checks": [
        {
          "args": [
            3
          ],
          "expected": 3000
        },
        {
          "args": [
            5
          ],
          "expected": 3000
        },
        {
          "args": [
            6
          ],
          "expected": 3500
        },
        {
          "args": [
            0
          ],
          "expected": 3000
        },
        {
          "args": [
            10
          ],
          "expected": 5500
        },
        {
          "args": [
            5,
            true
          ],
          "expected": 6000
        },
        {
          "args": [
            6,
            true
          ],
          "expected": 7000
        }
      ]
    },
    "cross-module-break": {
      "prompt": "금액에 천 단위 쉼표 좀 넣어줘.",
      "fixture": "cross-module-break",
      "module": "currency.py",
      "function": "format_won",
      "allowed_edits": [
        "currency.py",
        "receipt.py",
        "test_currency.py",
        "test_receipt.py"
      ],
      "required_edits": [
        "currency.py",
        "test_receipt.py"
      ],
      "checks": [
        {
          "args": [
            0
          ],
          "expected": "0원"
        },
        {
          "args": [
            999
          ],
          "expected": "999원"
        },
        {
          "args": [
            1234
          ],
          "expected": "1,234원"
        },
        {
          "args": [
            1000000
          ],
          "expected": "1,000,000원"
        }
      ],
      "integrations": [
        {
          "module": "receipt.py",
          "function": "render",
          "checks": [
            {
              "args": [
                [
                  [
                    "커피",
                    4500
                  ],
                  [
                    "빵",
                    12000
                  ]
                ]
              ],
              "expected": "커피: 4,500원\n빵: 12,000원"
            },
            {
              "args": [
                []
              ],
              "expected": ""
            }
          ]
        }
      ]
    }
  }
}
```
