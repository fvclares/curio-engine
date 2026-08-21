/**
 * Painel de controle do Curio Engine.
 *
 * Chama diretamente a API REST do GitHub (workflow_dispatch) para acionar
 * os workflows de geração de conteúdo, sem precisar abrir o GitHub.
 *
 * O token de acesso NUNCA é salvo no repositório — fica apenas no
 * localStorage deste navegador. Use um token "fine-grained" com permissão
 * mínima (Actions: Read and write) restrito a este repositório.
 */

const STORAGE_KEY = "curioEngine.adminConfig";

const els = {
  repo: document.querySelector("#repoInput"),
  branch: document.querySelector("#branchInput"),
  token: document.querySelector("#tokenInput"),
  saveConfig: document.querySelector("#saveConfigButton"),
  clearConfig: document.querySelector("#clearConfigButton"),
  configStatus: document.querySelector("#configStatus"),

  category: document.querySelector("#categoryInput"),
  quantity: document.querySelector("#quantityInput"),
  audioToo: document.querySelector("#audioTooCheckbox"),
  generateQuestions: document.querySelector("#generateQuestionsButton"),
  questionsStatus: document.querySelector("#questionsStatus"),

  forceAudio: document.querySelector("#forceAudioCheckbox"),
  generateAudio: document.querySelector("#generateAudioButton"),
  audioStatus: document.querySelector("#audioStatus"),

  actionsLink: document.querySelector("#actionsLink"),
};

function loadConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveConfig(config) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

function setStatus(element, message, kind) {
  element.textContent = message;
  element.className = `admin-status${kind ? ` admin-status--${kind}` : ""}`;
}

function getConfig() {
  const repo = els.repo.value.trim();
  const branch = els.branch.value.trim() || "main";
  const token = els.token.value.trim();
  return { repo, branch, token };
}

function updateActionsLink() {
  const { repo } = getConfig();
  els.actionsLink.href = repo ? `https://github.com/${repo}/actions` : "#";
}

async function dispatchWorkflow(workflowFile, inputs, statusElement) {
  const { repo, branch, token } = getConfig();

  if (!repo || !token) {
    setStatus(statusElement, "Preencha o repositório e o token na seção 1 antes de continuar.", "error");
    return;
  }

  setStatus(statusElement, "Disparando workflow no GitHub...", "pending");

  try {
    const response = await fetch(
      `https://api.github.com/repos/${repo}/actions/workflows/${workflowFile}/dispatches`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ref: branch, inputs }),
      }
    );

    if (response.status === 204) {
      setStatus(
        statusElement,
        "✅ Workflow disparado! Acompanhe o progresso na aba Actions do repositório (link no rodapé).",
        "ok"
      );
      return;
    }

    const body = await response.json().catch(() => ({}));
    const message = body.message || `Erro HTTP ${response.status}`;
    setStatus(statusElement, `❌ ${message}`, "error");
  } catch (error) {
    setStatus(statusElement, `❌ Falha de rede: ${error.message}`, "error");
  }
}

// --- Configuração (repo / branch / token) ---

function restoreConfig() {
  const config = loadConfig();
  if (config.repo) els.repo.value = config.repo;
  if (config.branch) els.branch.value = config.branch;
  if (config.token) els.token.value = config.token;
  updateActionsLink();
}

els.saveConfig.addEventListener("click", () => {
  const config = getConfig();
  if (!config.repo) {
    setStatus(els.configStatus, "Informe o repositório antes de salvar.", "error");
    return;
  }
  saveConfig(config);
  updateActionsLink();
  setStatus(els.configStatus, "✅ Configuração salva neste navegador.", "ok");
});

els.clearConfig.addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  els.token.value = "";
  setStatus(els.configStatus, "Token esquecido. Os campos de repositório/branch continuam preenchidos até você recarregar a página.", "ok");
});

els.repo.addEventListener("input", updateActionsLink);
els.branch.addEventListener("input", updateActionsLink);

// --- Gerar perguntas ---

els.generateQuestions.addEventListener("click", async () => {
  const category = els.category.value.trim();
  const quantity = els.quantity.value.trim() || "5";

  if (!category) {
    setStatus(els.questionsStatus, "Informe uma categoria.", "error");
    return;
  }

  els.generateQuestions.disabled = true;
  await dispatchWorkflow(
    "generate-questions.yml",
    {
      categoria: category,
      quantidade: quantity,
      gerar_audio_tambem: els.audioToo.checked,
    },
    els.questionsStatus
  );
  els.generateQuestions.disabled = false;
});

// --- Gerar áudio ---

els.generateAudio.addEventListener("click", async () => {
  els.generateAudio.disabled = true;
  await dispatchWorkflow(
    "generate-audio.yml",
    { forcar: els.forceAudio.checked },
    els.audioStatus
  );
  els.generateAudio.disabled = false;
});

restoreConfig();
