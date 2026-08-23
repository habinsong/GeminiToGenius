/**
 * GeminiToGenius — Pure Apple.com Interactive Scripts
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. One-touch Terminal Command Copy
  const copyBtn = document.getElementById("copyBtn");
  const toast = document.getElementById("toast");
  const toastText = document.getElementById("toastText");

  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const command = "git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh";
      try {
        await navigator.clipboard.writeText(command);
        showToast("설치 명령어가 클립보드에 복사되었습니다.");
      } catch (err) {
        showToast("명령어 복사에 실패했습니다. 직접 복사해 주세요.");
      }
    });
  }

  function showToast(message) {
    if (!toast || !toastText) return;
    toastText.textContent = message;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2400);
  }

  // 2. Interactive Process Simulator Tabs
  const tabBtns = document.querySelectorAll(".apple-tab-btn");
  const stepContainer = document.getElementById("stepContainer");

  const PRESETS = {
    feature: [
      { num: "01", title: "사용자의 지시를 요약하고 목표를 확정합니다.", desc: "어떤 기능을 만들어야 하는지 명확히 확인하고 현재 폴더 상태를 점검합니다." },
      { num: "02", title: "관련된 소스 코드와 설정을 끝까지 읽습니다.", desc: "대충 훑어보지 않고 전체 맥락을 꼼꼼히 파악하여 꼭 필요한 파일만 선별합니다." },
      { num: "03", title: "500줄을 넘지 않도록 역할을 나누어 작성합니다.", desc: "디자인, 계산, 저장 기능을 깔끔하게 분리하여 나중에 수정하기 쉽게 만듭니다." },
      { num: "04", title: "실제 동작을 직접 테스트하고 검증합니다.", desc: "에러가 없는지 확인하고 통과된 사실만을 투명하게 보고합니다." }
    ],
    bugfix: [
      { num: "01", title: "에러 로그와 발생 상황을 정확히 확인합니다.", desc: "어떤 입력에서 문제가 생겼는지 먼저 확인하고 가설을 세웁니다." },
      { num: "02", title: "7단계 원인 분석으로 진짜 버그 위치를 찾습니다.", desc: "엉뚱한 코드를 건드리지 않고 문제가 발생한 핵심 위치만 조심스럽게 고칩니다." },
      { num: "03", title: "수정 전과 후의 결과를 꼼꼼히 대조합니다.", desc: "기존에 잘 작동하던 다른 기능들이 망가지지 않았는지 재검증합니다." }
    ],
    ui: [
      { num: "01", title: "가짜 창틀이나 네온 색상 등 AI Slop을 배제합니다.", desc: "과장된 시각 장식 대신 선명한 흑백 대비와 웅장한 타이포그래피를 적용합니다." },
      { num: "02", title: "작은 스마트폰 화면부터 데스크톱까지 대응합니다.", desc: "320px 모바일 화면에서도 글자나 버튼이 잘리지 않고 깔끔하게 보이도록 조절합니다." },
      { num: "03", title: "친절하고 쉬운 일상 문장으로 카피를 작성합니다.", desc: "단답형 나열을 피하고 비전공자도 쉽게 이해할 수 있는 자연스러운 한국어를 씁니다." }
    ],
    research: [
      { num: "01", title: "공식 기술 문서와 1차 출처를 직접 검색합니다.", desc: "없는 기능을 지어내지 않고 실제 제공되는 공식 문서를 확인합니다." },
      { num: "02", title: "확인된 사실과 추론을 명확히 구분하여 설명합니다.", desc: "불확실한 내용은 넘겨짚지 않고 근거가 있는 사실만을 명확하게 정리해 드립니다." }
    ]
  };

  if (tabBtns.length > 0 && stepContainer) {
    tabBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        tabBtns.forEach(b => {
          b.classList.remove("active");
          b.setAttribute("aria-selected", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");

        const presetKey = btn.getAttribute("data-preset");
        const steps = PRESETS[presetKey] || PRESETS.feature;

        stepContainer.innerHTML = steps.map(step => `
          <div class="apple-step-item">
            <span class="apple-step-num">${step.num}</span>
            <div class="apple-step-body">
              <strong>${step.title}</strong>
              <p>${step.desc}</p>
            </div>
          </div>
        `).join("");
      });
    });

    // Initial render
    const initialKey = document.querySelector(".apple-tab-btn.active")?.getAttribute("data-preset") || "feature";
    const initialSteps = PRESETS[initialKey];
    stepContainer.innerHTML = initialSteps.map(step => `
      <div class="apple-step-item">
        <span class="apple-step-num">${step.num}</span>
        <div class="apple-step-body">
          <strong>${step.title}</strong>
          <p>${step.desc}</p>
        </div>
      </div>
    `).join("");
  }
});
