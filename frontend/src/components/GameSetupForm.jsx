import { useState } from "react";

export default function GameSetupForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    title: "안개의 숲",
    genre: "dark fantasy",
    theme: "기억 상실과 진실 왜곡",
    opening: "주인공은 작은 방에서 깨어난다. 자신이 누구인지 기억나지 않는다.",
    goal: "숲 깊은 곳에서 자신의 기억과 진실을 찾는다.",
    locationsText: "작은 방, 숲 입구, 깊은 숲, 폐허의 탑",
    itemsText: "편지, 녹슨 열쇠, 부서진 펜던트",
    npcsText: "숲의 안내자, 이름 없는 그림자",
    endingsText: "기억 회복, 거짓된 평화, 숲에 잠식됨",
    rules: "녹슨 열쇠를 찾으면 탑의 문을 열 수 있고, 문을 열면 엔딩으로 진행된다."
  });

  const updateField = (key, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const parseList = (text) =>
    text
      .split(",")
      .map((v) => v.trim())
      .filter(Boolean);

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      title: form.title,
      genre: form.genre,
      theme: form.theme,
      opening: form.opening,
      goal: form.goal,
      locations: parseList(form.locationsText),
      items: parseList(form.itemsText),
      npcs: parseList(form.npcsText),
      endings: parseList(form.endingsText),
      rules: form.rules,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        maxWidth: "900px",
        margin: "0 auto 24px auto",
        padding: "16px",
        border: "1px solid #ddd",
        borderRadius: "12px",
        background: "#fafafa"
      }}
    >
      <h2>게임 설정</h2>

      <div style={{ marginBottom: "12px" }}>
        <label>제목</label>
        <br />
        <input
          value={form.title}
          onChange={(e) => updateField("title", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>장르</label>
        <br />
        <input
          value={form.genre}
          onChange={(e) => updateField("genre", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>테마</label>
        <br />
        <input
          value={form.theme}
          onChange={(e) => updateField("theme", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>시작 상황</label>
        <br />
        <textarea
          value={form.opening}
          onChange={(e) => updateField("opening", e.target.value)}
          style={{ width: "100%", minHeight: "80px", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>최종 목표</label>
        <br />
        <textarea
          value={form.goal}
          onChange={(e) => updateField("goal", e.target.value)}
          style={{ width: "100%", minHeight: "80px", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>장소들 (쉼표로 구분)</label>
        <br />
        <input
          value={form.locationsText}
          onChange={(e) => updateField("locationsText", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>아이템들 (쉼표로 구분)</label>
        <br />
        <input
          value={form.itemsText}
          onChange={(e) => updateField("itemsText", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>등장인물들 (쉼표로 구분)</label>
        <br />
        <input
          value={form.npcsText}
          onChange={(e) => updateField("npcsText", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>엔딩들 (쉼표로 구분)</label>
        <br />
        <input
          value={form.endingsText}
          onChange={(e) => updateField("endingsText", e.target.value)}
          style={{ width: "100%", padding: "8px" }}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <label>게임 규칙 / 종료 조건</label>
        <br />
        <textarea
          value={form.rules}
          onChange={(e) => updateField("rules", e.target.value)}
          style={{ width: "100%", minHeight: "100px", padding: "8px" }}
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "생성 중..." : "이 설정으로 게임 시작"}
      </button>
    </form>
  );
}