function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

window.initMessageBoard = function initMessageBoard() {
  const mountPoint = document.querySelector("#messageApp");
  if (!mountPoint || mountPoint.dataset.vueReady) return;
  mountPoint.dataset.vueReady = "1";

  Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
      return {
        currentUser: mountPoint.dataset.currentUser || "",
        form: { name: "", email: "", content: "" },
        replyForm: { name: "", content: "" },
        replyingTo: null,
        messages: [],
      };
    },
    mounted() {
      this.loadMessages();
    },
    methods: {
      async loadMessages() {
        const response = await fetch("/api/messages/");
        const data = await response.json();
        this.messages = data.messages;
      },
      laneMessages(lane) {
        return this.messages.filter((_, index) => index % 6 === lane - 1);
      },
      danmakuText(item) {
        const firstReply = item.replies && item.replies.length ? item.replies[0] : null;
        if (!firstReply) return `${item.name}：${item.content}`;
        return `${item.name}：${item.content} · ${firstReply.name}：${firstReply.content}`;
      },
      toggleReply(id) {
        this.replyingTo = this.replyingTo === id ? null : id;
        this.replyForm = { name: "", content: "" };
      },
      async submitMessage(parentId = null) {
        const source = parentId ? this.replyForm : this.form;
        if (!this.currentUser && !source.name.trim()) return;
        if (!source.content.trim()) return;

        const payload = {
          name: source.name,
          email: this.form.email,
          content: source.content,
          parentId,
        };
        const response = await fetch("/api/messages/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) return;
        const data = await response.json();
        if (parentId) {
          const parent = this.messages.find((item) => item.id === parentId);
          if (parent) parent.replies.push(data.message);
          this.replyForm = { name: "", content: "" };
          this.replyingTo = null;
        } else {
          this.messages = [data.message, ...this.messages];
          this.form = { name: "", email: "", content: "" };
        }
      },
    },
  }).mount(mountPoint);
};

window.initMessageBoard();
