const API_BASE = "http://localhost:8000";

export async function fetchScene(sceneId, state = {}) {
  const res = await fetch(`${API_BASE}/scene`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      scene_id: sceneId,
      state,
    }),
  });

  const text = await res.text();

  if (!res.ok) {
    throw new Error(`Scene API error: ${res.status} ${text}`);
  }

  return JSON.parse(text);
}

export async function chooseOption(sceneId, choiceId, state = {}) {
  const res = await fetch(`${API_BASE}/choice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      scene_id: sceneId,
      choice_id: choiceId,
      state,
    }),
  });

  const text = await res.text();

  if (!res.ok) {
    throw new Error(`Choice API error: ${res.status} ${text}`);
  }

  return JSON.parse(text);
}

export async function generateItemFromSketch(
  itemId,
  sketchDataUrl,
  objectHint = "",
  detailHint = ""
) {
  const res = await fetch(`${API_BASE}/items/generate-from-sketch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      item_id: itemId,
      sketch_data_url: sketchDataUrl,
      object_hint: objectHint,
      detail_hint: detailHint,
    }),
  });

  const text = await res.text();

  if (!res.ok) {
    throw new Error(`Generate from sketch API error: ${res.status} ${text}`);
  }

  return JSON.parse(text);
}

export async function setupGame(storyConfig) {
  const res = await fetch(`${API_BASE}/game/setup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(storyConfig),
  });

  const text = await res.text();

  if (!res.ok) {
    throw new Error(`Game setup API error: ${res.status} ${text}`);
  }

  return JSON.parse(text);
}