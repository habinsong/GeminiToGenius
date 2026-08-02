---
name: architecture-boundaries
description: Prevents God Objects and responsibility pileups while adding features, fixing code, introducing classes, controllers, managers, stores, services, models, components, pipelines, or refactoring architecture. Use automatically for 기능 추가, 코드 구현, 리팩터링, 구조 변경, God Object, 대형 파일, 책임 분리, feature, implementation, refactor, architecture, large file, class, controller, manager, store, service, model, component, or pipeline without requiring @mentions or slash commands.
---

# 책임 경계

1. 변경 전에 대상 파일·타입의 LOC, 현재 책임, 상태 소유권, 입출력, 외부 부작용, 주요 의존성을 확인합니다. README나 타입 이름으로 책임을 추측하지 않습니다.
2. 추가할 동작이 기존 책임과 같은 변경 이유를 갖는지 확인합니다. UI 상태·도메인 정책·변환·IO·영속성·네트워크·외부 프로세스·표현 중 별개 축을 기존 대형 객체에 누적하지 않습니다.
3. 경계가 섞이면 기능을 붙이기 전에 가장 작은 응집 단위를 뽑습니다. pure helper, state holder, model, service, pipeline, persistence adapter, view, support, test 중 실제 책임에 맞는 형태만 선택합니다.
4. 프론트엔드는 화면과 데이터 모델의 실제 구조에 맞춰 컴포넌트를 나눕니다. 한 컴포넌트가 원격 조회·도메인 판단·전역 상태·렌더링·애니메이션을 함께 소유하지 않게 하고, 상태는 필요한 가장 가까운 단일 소유자에 둡니다.
5. 백엔드는 transport handler·도메인 정책·데이터 접근·외부 서비스 경계를 분리하되 기존 프로젝트 구조를 따릅니다. API 계약이 내부 DB 구조를 그대로 노출하지 않게 하고, 리팩터링 때문에 공개 계약이 바뀌지 않게 합니다.
6. 엔트리포인트·controller·coordinator는 흐름을 조정할 수 있지만 모든 상태와 정책과 부작용을 직접 소유하지 않습니다. 데이터에는 명확한 단일 소유자를 두고 변경 경로를 추적 가능하게 유지합니다.
7. LOC는 경고 신호이지 합격선이 아닙니다. 줄 수만 줄이는 forwarding wrapper, 한 번만 쓰는 추상화, 파일 수 늘리기, 이름만 Layer인 빈 구조는 만들지 않습니다. 작은 앱에 계층·repository·microservice를 억지로 추가하지 않습니다.
8. 기존 공개 API와 동작을 보존하고 한 책임씩 이동합니다. 이동할 때 필요한 import·의존성·테스트를 함께 옮기고 각 단계마다 가장 작은 컴파일이나 테스트를 실행합니다.
9. 변경 뒤 주요 파일·타입별로 남은 책임과 변경 이유를 다시 적습니다. 새 God Object가 생기지 않았는지, 의존 방향과 상태 소유자가 분명한지, 새 책임을 검증하는 테스트가 있는지 확인합니다.

완료 보고에는 주요 변경 파일의 LOC·책임 확인 결과와 실제 실행한 검증만 남깁니다.

경계 선택에 외부 근거가 필요한 작업에서는 [공식 아키텍처 근거](references/evidence.md)를 읽습니다.
