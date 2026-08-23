---
name: architecture-boundaries
description: Prevents God Objects and responsibility pileups while adding features, fixing code, introducing classes, controllers, managers, stores, services, models, components, pipelines, or refactoring architecture. Use automatically for 기능 추가, 코드 구현, 리팩터링, 구조 변경, God Object, 대형 파일, 책임 분리, feature, implementation, refactor, architecture, large file, class, controller, manager, store, service, model, component, or pipeline without requiring @mentions or slash commands.
---

# 책임 경계 및 아키텍처 규율

1. **단순성 우선 (3. Simplicity First)**: 문제를 해결하는 최소한의 코드만 작성합니다. 요구하지 않은 기능, 1회용 코드에 대한 추상화, 유연성/구성성, 새 프레임워크, 새 의존성, 불가능한 시나리오에 대한 에러 처리를 배제합니다. "시니어 엔지니어가 과도하게 복잡하다고 판단할 것인가?"를 점검합니다.
2. **사전 검사 및 책임 식별**: 변경 전에 대상 파일·타입의 LOC, 현재 책임, 상태 소유권, 입출력, 외부 부작용, 주요 의존성을 확인합니다. README나 타입 이름으로 책임을 추측하지 않습니다.
3. **단일 책임 원칙 (SRP) 및 축 분리**: 추가할 동작이 기존 책임과 같은 변경 이유를 갖는지 확인합니다. UI 상태·도메인 정책·변환·IO·영속성·네트워크·외부 프로세스·표현 중 별개 축을 기존 대형 객체에 누적하지 않고 가장 작은 응집 단위로 분리합니다.
4. **500줄 제한 규칙 (15. Architecture Rules: 500-Line Limit Rule)**: 타당하고 문서화된 명백한 이유 없이 단일 파일이 500줄(LOC)을 초과하지 않도록 합니다. 파일이 500줄에 도달하거나 초과할 경우, 단순한 줄바꿈 분할이 아니라 명확한 책임(UI 상태, 도메인 로직, 영속성/IO, 외부 프로세스, 표현)에 따라 전용 디렉터리와 하위 모듈로 분해하여 높은 응집도와 낮은 결합도를 유지합니다.
5. **프론트엔드 및 백엔드 경계**: 프론트엔드는 한 컴포넌트가 원격 조회·도메인 판단·전역 상태·렌더링을 독점하지 않게 가장 가까운 단일 소유자에 상태를 둡니다. 백엔드는 transport handler·도메인 정책·데이터 접근 경계를 분리하고 공개 API 계약을 보존합니다.
6. **아키텍처 변경 제안 5대 필수 항목**: 구조 변경 제안 시 ① Current problem, ② Proposed structure, ③ Migration path, ④ Tradeoffs, ⑤ Verification plan을 반드시 포함합니다.
7. **포워딩 래퍼 금지**: 줄 수만 줄이는 forwarding wrapper, 한 번만 쓰는 추상화, 빈 레이어는 만들지 않습니다.
8. **단계별 검증 및 완료 보고**: 한 책임씩 이동하며 각 단계마다 최소 컴파일/테스트를 실행합니다. 완료 보고에는 주요 변경 파일의 LOC와 책임 확인 결과 및 실제 실행한 검증만 남깁니다.

상세 원문: [아키텍처 및 단순성 원칙](references/architecture-rules.md)
