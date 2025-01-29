<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<style lang="less">
body {
  background: #0b0f19;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #fff;
  height: 100%;
}

::-webkit-scrollbar {
  width: 5px;
}

::-webkit-scrollbar-track {
  background: #181C33;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(#4b5563, #374151);;
  border-radius: 30px;
}
</style>
