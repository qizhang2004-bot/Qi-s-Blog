const savedTheme = localStorage.getItem("blog-theme") || "day";
document.documentElement.dataset.theme = savedTheme;

function syncThemeButton() {
  const button = document.querySelector("[data-theme-toggle]");
  if (!button) return;
  button.textContent = document.documentElement.dataset.theme === "night" ? "夜色" : "白昼";
}

syncThemeButton();

function initHomeGate() {
  const homePage = document.querySelector(".home-page");
  if (!homePage || homePage.dataset.homeGateReady) return;
  homePage.dataset.homeGateReady = "1";
  document.body.classList.remove("home-locked", "home-unlocked");
  if (sessionStorage.getItem("blog-home-entered") === "1") {
    document.body.classList.add("home-unlocked");
    return;
  }
  document.body.classList.add("home-locked");
  window.addEventListener("click", revealHome, { once: true });
}

function revealHome() {
  if (!document.body.classList.contains("home-locked")) return;
  document.body.classList.remove("home-locked");
  document.body.classList.add("home-unlocked");
  sessionStorage.setItem("blog-home-entered", "1");
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(playBackgroundMusic, 850);
}

initHomeGate();

document.addEventListener("click", (event) => {
  if (!event.target.matches("[data-theme-toggle]")) return;
  const nextTheme = document.documentElement.dataset.theme === "night" ? "day" : "night";
  document.documentElement.dataset.theme = nextTheme;
  localStorage.setItem("blog-theme", nextTheme);
  syncThemeButton();
});

const musicPlayer = document.querySelector("[data-music-player]");
let playBackgroundMusic = () => {};
if (musicPlayer) {
  const musicAudio = musicPlayer.querySelector("[data-music-audio]");
  const musicToggle = musicPlayer.querySelector("[data-music-toggle]");
  const musicTitle = musicPlayer.querySelector("[data-music-title]");
  const playlistElement = document.querySelector("#music-playlist-data");
  const playlist = playlistElement ? JSON.parse(playlistElement.textContent) : [];
  const savedMusic = JSON.parse(localStorage.getItem("blog-music-state") || "{}");
  let currentTrack = Math.min(savedMusic.track || 0, Math.max(playlist.length - 1, 0));
  let shouldResume = savedMusic.playing === true;
  let lastSavedSecond = -1;

  const setMusicState = (isPlaying) => {
    musicToggle.classList.toggle("is-playing", isPlaying);
    musicToggle.textContent = isPlaying ? "Ⅱ" : "♪";
    musicToggle.setAttribute("aria-label", isPlaying ? "暂停背景音乐" : "播放背景音乐");
  };

  const saveMusicState = () => {
    localStorage.setItem("blog-music-state", JSON.stringify({
      track: currentTrack,
      time: Number.isFinite(musicAudio.currentTime) ? musicAudio.currentTime : 0,
      playing: !musicAudio.paused,
    }));
  };

  const loadTrack = (index, startTime = 0) => {
    if (!playlist.length) return;
    currentTrack = (index + playlist.length) % playlist.length;
    const track = playlist[currentTrack];
    if (musicAudio.src !== new URL(track.url, window.location.origin).href) {
      musicAudio.src = track.url;
    }
    musicAudio.loop = playlist.length === 1;
    musicTitle.textContent = track.title;
    if (startTime) {
      musicAudio.addEventListener("loadedmetadata", () => {
        musicAudio.currentTime = Math.min(startTime, Math.max(musicAudio.duration - 1, 0));
      }, { once: true });
    }
  };

  loadTrack(currentTrack, savedMusic.time || 0);

  playBackgroundMusic = async () => {
    if (musicAudio.paused) {
      try {
        await musicAudio.play();
        shouldResume = true;
        setMusicState(true);
      } catch (error) {
        shouldResume = true;
        setMusicState(false);
      }
    }
  };

  musicToggle.addEventListener("click", async () => {
    if (musicAudio.paused) {
      await playBackgroundMusic();
      return;
    }
    musicAudio.pause();
    shouldResume = false;
    setMusicState(false);
    saveMusicState();
  });

  musicAudio.addEventListener("play", () => {
    setMusicState(true);
    saveMusicState();
  });
  musicAudio.addEventListener("pause", () => {
    setMusicState(false);
    saveMusicState();
  });
  musicAudio.addEventListener("timeupdate", () => {
    const second = Math.floor(musicAudio.currentTime);
    if (second !== lastSavedSecond && second % 3 === 0) {
      lastSavedSecond = second;
      saveMusicState();
    }
  });
  musicAudio.addEventListener("ended", async () => {
    if (playlist.length > 1) {
      loadTrack(currentTrack + 1, 0);
      await playBackgroundMusic();
      return;
    }
    setMusicState(false);
  });
  window.addEventListener("pagehide", saveMusicState);
  if (shouldResume) {
    playBackgroundMusic();
    document.addEventListener("click", () => {
      if (shouldResume && musicAudio.paused) playBackgroundMusic();
    }, { once: true });
  }
}

const lifeLightbox = document.querySelector("[data-life-lightbox]");
function initLifeLightbox() {
  const lifeLightbox = document.querySelector("[data-life-lightbox]");
  if (!lifeLightbox || lifeLightbox.dataset.lightboxReady) return;
  lifeLightbox.dataset.lightboxReady = "1";
  const lifeImage = lifeLightbox.querySelector("[data-life-image]");
  const lifeDate = lifeLightbox.querySelector("[data-life-date]");
  const lifeNote = lifeLightbox.querySelector("[data-life-note]");
  const closeLife = () => {
    lifeLightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
  };

  document.querySelectorAll("[data-life-card]").forEach((card) => {
    if (card.dataset.lifeReady) return;
    card.dataset.lifeReady = "1";
    card.addEventListener("click", () => {
      lifeImage.src = card.dataset.photo;
      lifeDate.textContent = card.dataset.date;
      lifeNote.textContent = card.dataset.note;
      lifeLightbox.hidden = false;
      document.body.classList.add("lightbox-open");
    });
  });

  lifeLightbox.querySelector("[data-life-close]").addEventListener("click", closeLife);
  lifeLightbox.addEventListener("click", (event) => {
    if (event.target === lifeLightbox) closeLife();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeLife();
  });
}

initLifeLightbox();

function initArticleToc() {
  const tocPanel = document.querySelector(".toc-panel");
  if (!tocPanel || tocPanel.dataset.tocReady) return;
  tocPanel.dataset.tocReady = "1";

  tocPanel.addEventListener("click", (event) => {
    const link = event.target.closest("a[href^='#']");
    if (!link) return;
    const rawHash = link.getAttribute("href").slice(1);
    if (!rawHash) return;
    const targetId = decodeURIComponent(rawHash);
    const target = document.getElementById(targetId);
    if (!target) return;

    event.preventDefault();
    const topbar = document.querySelector(".topbar");
    const offset = (topbar?.getBoundingClientRect().height || 76) + 28;
    const currentTop = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    const targetTop = target.getBoundingClientRect().top + currentTop - offset;
    const previousScrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = "auto";
    window.scrollTo({ top: Math.max(targetTop, 0), behavior: "auto" });
    requestAnimationFrame(() => {
      document.documentElement.style.scrollBehavior = previousScrollBehavior;
      history.replaceState(history.state, "", `${window.location.pathname}${window.location.search}#${encodeURIComponent(targetId)}`);
    });
  });
}

initArticleToc();

let articleSidebarCleanup = null;

function initArticleSidebarFollow() {
  if (articleSidebarCleanup) {
    articleSidebarCleanup();
    articleSidebarCleanup = null;
  }

  const layout = document.querySelector(".article-reading-layout");
  const side = document.querySelector(".article-side");
  if (!layout || !side) return;

  let ticking = false;
  let startTop = 0;
  let maxTranslate = 0;
  let topOffset = 108;
  let currentTranslate = 0;
  let targetTranslate = 0;
  let animationFrame = null;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const applyTranslate = (value) => {
    side.style.transform = `translate3d(0, ${value.toFixed(2)}px, 0)`;
  };

  const animate = () => {
    animationFrame = null;
    const delta = targetTranslate - currentTranslate;
    if (Math.abs(delta) < .35) {
      currentTranslate = targetTranslate;
      applyTranslate(currentTranslate);
      return;
    }
    currentTranslate += delta * .24;
    applyTranslate(currentTranslate);
    animationFrame = requestAnimationFrame(animate);
  };

  const startAnimation = () => {
    if (reduceMotion) {
      currentTranslate = targetTranslate;
      applyTranslate(currentTranslate);
      return;
    }
    if (!animationFrame) animationFrame = requestAnimationFrame(animate);
  };

  const measure = () => {
    side.style.transform = "translate3d(0, 0, 0)";
    const topbar = document.querySelector(".topbar");
    topOffset = (topbar?.getBoundingClientRect().height || 76) + 16;
    const pageY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    startTop = side.getBoundingClientRect().top + pageY;
    const layoutBottom = layout.getBoundingClientRect().top + pageY + layout.offsetHeight;
    maxTranslate = Math.max(0, layoutBottom - side.offsetHeight - startTop);
  };

  const update = () => {
    ticking = false;
    if (window.innerWidth <= 1000) {
      side.style.transform = "";
      currentTranslate = 0;
      targetTranslate = 0;
      return;
    }
    const pageY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    targetTranslate = Math.min(Math.max(pageY + topOffset - startTop, 0), maxTranslate);
    startAnimation();
  };

  const requestUpdate = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  const refresh = () => {
    measure();
    currentTranslate = Math.min(currentTranslate, maxTranslate);
    targetTranslate = Math.min(targetTranslate, maxTranslate);
    update();
  };

  refresh();
  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", refresh);
  articleSidebarCleanup = () => {
    window.removeEventListener("scroll", requestUpdate);
    window.removeEventListener("resize", refresh);
    if (animationFrame) cancelAnimationFrame(animationFrame);
    side.style.transform = "";
  };
}

initArticleSidebarFollow();

let activeNavigation = null;
let navigationSerial = 0;

async function loadPage(url, pushState = true) {
  const navigationId = navigationSerial + 1;
  navigationSerial = navigationId;
  if (activeNavigation) activeNavigation.abort();
  const controller = new AbortController();
  activeNavigation = controller;

  const currentContent = document.querySelector("[data-page-content]");
  if (currentContent) currentContent.classList.add("page-leave");

  let response;
  try {
    response = await fetch(url, {
      headers: { "X-Requested-With": "fetch" },
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") return;
    throw error;
  }

  if (navigationId !== navigationSerial) return;
  if (!response.ok) {
    window.location.assign(url);
    return;
  }

  const html = await response.text();
  if (navigationId !== navigationSerial) return;
  const nextDocument = new DOMParser().parseFromString(html, "text/html");
  const nextContent = nextDocument.querySelector("[data-page-content]");
  if (!nextContent || !currentContent) {
    window.location.assign(url);
    return;
  }

  await new Promise((resolve) => setTimeout(resolve, 110));
  if (navigationId !== navigationSerial) return;
  nextContent.classList.add("page-enter");
  currentContent.replaceWith(nextContent);
  document.title = nextDocument.title;
  document.body.className = nextDocument.body.className || "";
  if (pushState) history.pushState({}, "", url);
  window.scrollTo({ top: 0, behavior: "auto" });
  syncThemeButton();
  initHomeGate();
  initLifeLightbox();
  initArticleToc();
  initArticleSidebarFollow();
  loadPageScripts(nextDocument);
  requestAnimationFrame(() => {
    nextContent.classList.add("is-visible");
    window.setTimeout(() => nextContent.classList.remove("page-enter", "is-visible"), 420);
  });
  if (activeNavigation === controller && !controller.signal.aborted) activeNavigation = null;
}

function loadPageScripts(nextDocument) {
  const needsMessages = [...nextDocument.querySelectorAll("script[src]")]
    .some((script) => script.src.includes("/static/js/messages.js"));

  if (!needsMessages) return;
  if (window.initMessageBoard) {
    window.initMessageBoard();
    return;
  }

  const script = document.createElement("script");
  script.src = "/static/js/messages.js";
  script.onload = () => window.initMessageBoard && window.initMessageBoard();
  document.body.appendChild(script);
}

function shouldHandleLink(link, event) {
  if (!link || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
  if (link.target || link.hasAttribute("download")) return false;
  const url = new URL(link.href, window.location.href);
  if (url.origin !== window.location.origin) return false;
  if (url.pathname.startsWith("/admin/")) return false;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/media/") || url.pathname.startsWith("/static/")) return false;
  if (["/login/", "/register/", "/logout/"].includes(url.pathname)) return false;
  if (url.pathname === window.location.pathname && url.search === window.location.search && !url.hash) return false;
  if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return false;
  return true;
}

document.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!shouldHandleLink(link, event)) return;
  event.preventDefault();
  loadPage(link.href).catch(() => {
    window.location.href = link.href;
  });
});

window.addEventListener("popstate", () => {
  loadPage(window.location.href, false).catch(() => window.location.reload());
});

const canRenderCursorTrail = window.matchMedia("(pointer: fine)").matches
  && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let lastTrailAt = 0;
document.addEventListener("pointermove", (event) => {
  if (!canRenderCursorTrail) return;
  if (event.pointerType && event.pointerType !== "mouse") return;
  const now = Date.now();
  if (now - lastTrailAt < 72) return;
  lastTrailAt = now;

  const dot = document.createElement("span");
  dot.className = "cursor-trail";
  dot.style.left = `${event.clientX}px`;
  dot.style.top = `${event.clientY}px`;
  document.body.appendChild(dot);
  setTimeout(() => dot.remove(), 500);
});
