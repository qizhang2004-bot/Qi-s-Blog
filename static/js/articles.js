const { createApp } = Vue;

createApp({
  delimiters: ["[[", "]]"],
  data() {
    return {
      selected: "",
      articles: [],
      initialTag: "",
    };
  },
  mounted() {
    const tagScript = document.getElementById("selected-tag-slug");
    this.initialTag = tagScript ? JSON.parse(tagScript.textContent) : "";
    this.loadArticles("", this.initialTag);
  },
  methods: {
    async loadArticles(category, tag = "") {
      this.selected = category;
      const query = new URLSearchParams();
      if (category) query.set("category", category);
      if (tag) query.set("tag", tag);
      const params = query.toString() ? `?${query.toString()}` : "";
      const response = await fetch(`/api/articles/${params}`);
      const data = await response.json();
      this.articles = data.articles;
    },
  },
}).mount("#articlesApp");
