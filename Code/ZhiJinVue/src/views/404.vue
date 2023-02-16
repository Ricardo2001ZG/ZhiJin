<template>
  <div class="wscn-http-container">
    <img src="@/assets/images/404.png" alt="你访问的页面不存在！">
    <p style="color:#5782CF;margin-top:64px">你访问的页面不存在！</p>
  </div>
</template>

<style lang="scss" scoped>
.wscn-http-container{
  position: relative;
  width: 611px;
  height: 363px;
  margin: 118px auto;
  text-align: center;
  animation: nothttp 1s;
}
@keyframes nothttp{
   0% {
        opacity: 0;
    }
    50% {
        opacity: 0.5;
    }
    100% {
        opacity: 1;
    }
}
</style>
