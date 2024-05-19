<script setup>
import king_svg from '/svg/king.svg?raw'
import arrow_down from '/svg/arrow-down.svg?raw'
import arrow_up from '/svg/arrow-up.svg?raw'
import User from './User.vue'
import Popper from 'vue3-popper'
</script>

<!-- Show current king details and set new one. -->
<template>
  <Popper @open:popper="setOpen(true)" @close:popper="setOpen(false)" placement="bottom-end">
    <div class="king-select">
      <div class="crown" v-html="king_svg" />
      <user :pubkey="value" :link="false" :ndk="ndk" :title="npub" />
      <div class="arrow" v-html="arrow_we_need" />
    </div>
    <template #content>
      <div class="popper-content">
        <div>The current king is <user :pubkey="value" :ndk="ndk"/></div>
        <div class="new-king">Set to <input type="text" class="npub-input" ref="npub" placeholder="king's npub..." @enter.prevent="onSetKing"><button @click="onSetKing">Set</button></div>
        <a v-if="show_reset" href="#reset-king" @click="onResetKing()">reset king</a>
      </div>
    </template>
  </Popper>
</template>


<script>
export default {
  props: ["value", "ndk", "show_reset"],
  data: function () {
    return {
      is_open: false
    }
  },
  components: { Popper },
  beforeMount () {
    this.npub = this.ndk.getUser({ pubkey: this.value }).npub
  },
  methods: {
    setOpen (state) {
      this.is_open = state
    },
    onResetKing () {
      document.cookie = "king=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; samesite=strict"
      window.location.reload()
    },
    onSetKing () {
      let npub = this.$refs.npub.value
      console.log("king npub", npub)
      let u = this.ndk.getUser({ npub })
      if (!u) {
        alert("Invalid npub.")
        return
      }
      let pubkey = u.pubkey
      document.cookie = `king=${pubkey}; max-age=31536000; path=/; samesite=strict`
      console.log("king is set to", pubkey)
      window.location.reload()
    }
  },
  computed: {
    arrow_we_need () {
      return this.is_open ? arrow_up : arrow_down
    }
  }
}
</script>

<style scoped>
.crown {
  width: 16px;
  height: 16px;
  position: relative;
  top: 2px;
  margin-right: 5px;
}
.arrow {
  width: 10px;
  height: 10px;
  margin-left: 8px;
  fill: var(--text5);
}
.king-select {
  display: flex;
  color: var(--text5);
  fill: var(--text5);
  cursor: pointer;
  border-radius: 8px;
  padding: 0 12px;
}
.king-select:hover {
  background: var(--bg3);
}
.npub-input {
  width: 100%;
  margin-left: 10px;
}
.new-king {
  margin-top: 8px;
  display: flex;
  flex-direction: row;
  white-space: nowrap;
}
.popper-content {
  padding: 8px 12px;
}
</style>
