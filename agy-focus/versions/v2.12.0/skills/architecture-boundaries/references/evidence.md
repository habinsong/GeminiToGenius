# 공식 아키텍처 근거

경계 선택이나 리팩터링 근거가 필요할 때만 읽습니다.

- Android Developers: [관심사 분리, 명확한 경계, 단일 진실 공급원](https://developer.android.com/topic/architecture)
- React: [UI·데이터 구조에 맞춘 컴포넌트와 단일 책임](https://react.dev/learn/thinking-in-react)
- Microsoft .NET Architecture: [모놀리스 안에서도 관심사 분리](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)
- Microsoft Azure Architecture: [느슨한 결합과 내부 데이터 구조를 그대로 노출하지 않는 API](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)

이 자료는 무조건 계층·repository·microservice를 늘리라는 뜻이 아닙니다. 현재 코드의 변경 이유와 의존 방향이 실제 분리 기준입니다.
