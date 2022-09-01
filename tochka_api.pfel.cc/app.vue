<template>
  <div id="main">
    <div id="container">
      <div class="title">
        <h1 class="serif">Tochka API</h1>
      </div>
      <div class="params_container">
        <div class="field_container" v-for="(value, name, index) in queries">
          <div class="field_name">
            <span>{{name}}</span>
          </div>
          <div class="field_value">
            <div class="value">
              <span>{{ value }}</span>
            </div>
            <div class="copy_icon_container" @click="() => {copy_to_clipboard(value)}">
              <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
            </div>
          </div>
        </div>
      </div>
      <div class="footer">
        <p>
          <a href="https://github.com/WhiteApfel/tochka_api">Source code</a> |
          (c) <a href="https://dev.pfel.cc/">WhiteApfel</a> | 2022
        </p>

      </div>
    </div>
  </div>
</template>

<script setup>
const queries = useState('queries', () => {return {}})

function copy_to_clipboard(text) {
  navigator.clipboard.writeText(text)
}

onMounted(() => {
  location.search.substr(1).split("&").forEach(function(item) {queries.value[item.split("=")[0]] = item.split("=")[1]})
  console.log(queries.value.code)
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat&family=Playfair+Display:wght@700&display=swap');

:root {
  --color: #333;
  --link-color: #111;
  --bg-color: #fbfbfc;
  --border-color: #e1e1e1;
}
@media (prefers-color-scheme: light) {
  :root {
    --color: #c7c7c7;
    --link-color: #e7e7e7;
    --bg-color: #1d1d1d;
    --border-color: #696969;

  }
}
body {
  color: var(--color);
  background-color: var(--bg-color);
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
  min-height: 100vh;
  padding: 0;
  margin: 0;
}
.serif {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
}
a {
  color: var(--link-color);
  text-decoration: None;
}

#main {
  display: grid;
  width: 100%;
  min-height: 100vh;
  background: url(https://tochka.com/theme/main/img/component/form/new_paint_right.png) 100% 0 no-repeat,url(https://tochka.com//theme/main/img/component/form/new_paint_left.png) 0 100% no-repeat;
  background-size: 193px 361px, 242px 376px;
}
#container {
  display: flex;
  flex-direction: column;
  margin: auto;
}
div.title > h1 {
  text-align: center;
  font-size: 3em;
  margin: 0;
}
.params_container {
  min-width: 30em;
  max-width: 90vw;
  display: flex;
  box-sizing: border-box;
  flex-direction: column;
  /*border: 3px solid var(--color);*/
  /*border-radius: 1em;*/
  padding: 1em;
}
@media (min-width: 600px) {
  .params_container {
    max-width: 40em;
  }
}
.field_container {
  display: grid;
  grid-template-columns: 8em auto;
  width: 100%;
  margin: 1em 0;
  backdrop-filter: blur(1em);
}
.field_container > div {
  border: 1px solid var(--border-color);
  padding: 1em 1.5em;
  box-sizing: border-box;
}
.field_container > div.field_name {
  border-radius: .5em 0 0 .5em;
  border-right: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.field_container > div.field_value {
  border-radius: 0 .5em .5em 0;
  padding: 1em 3.25em 1em 1.5em;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin: auto 0;
  overflow: hidden;
  position: relative;
}
.field_container > div.field_value > div.value {
}
.field_container > div.field_value > div.copy_icon_container {
  display: flex;
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 3.25em;
  background: linear-gradient(90deg, #fff0, #fff 20%);
}
.field_container > div.field_value > div.copy_icon_container > svg {
  height: 1.25em;
  width: 1.25em;
  margin: auto;
  fill: var(--color);
  transition: .3s;
}
.field_container > div.field_value > div.copy_icon_container:hover {
  cursor: pointer;
}
.field_container > div.field_value > div.copy_icon_container:hover > svg {
  transform: scale(1.1);
  fill: var(--link-color);
}
div.footer > p {
  font-size: .75em;
  text-align: center;
}
</style>