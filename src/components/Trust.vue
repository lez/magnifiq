<!-- Display trust icon, show trail in popper. -->
<script setup>
import Popper from "vue3-popper"
import User from "./User.vue"
import stamp from "/svg/stamp.svg?raw"
import stamp_add from "/svg/stamp-add.svg?raw"
</script>

<template>
  <span class="trust">
    <Popper placement="right-end" @open:popper="onFetchTrust()">
      <div v-if="trust !== null" class="stamp" v-html="stamp"></div>
      <div v-else class="stamp-add" v-html="stamp_add"></div>

      <template #content>
        <div class="hovercard">
          <div class="content-header">
            Trust for <span class="context">{{ context }}</span>
          </div>
          <div v-if="trust === undefined">Loading...</div>
          <div v-else-if="trust === false">Error fetching trust</div>
          <div v-else-if="trust === null">
            Not trusted<br>
            <a href="#" @click.prevent="$emit('trust')">trust this user</a>
          </div>
          <div v-else>
            <user :pubkey="king" :ndk="ndk"/>
            <span v-if="trust && trust.length === 0">is king.</span>

            <div v-for="(t, idx) of trust" :key="t.pubkey">
              <div class="dotted"></div>
              <div class="hierarchy-level">
                <user :pubkey="t.trusted" :ndk="ndk"/>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Popper>
  </span>
</template>

<script>
export default {
  name: 'trust',
  props: ["ndk", "search_ndk", "king", "author", "context", "fetch_"],
  components: { Popper, User },
  data: function () {
    return {
      trust: undefined,
    }
  },
  beforeMount() {
    if (this.king === this.author) {
      this.trust = []
    }
  },
  mounted () {
    if (this.fetch_) {
      this.onFetchTrust()
    }
  },
  methods: {
    // Fetch trust events from king to author.
    getTagValue(event, tagname){
      for (let t of event.tags) {
        if (t[0] == tagname) {
          return t[1]
        }
      }
      return null
    },

    async onFetchTrust () {
      if (this.trust !== undefined) {
        console.log("already fetched trust")
        return
      }
      console.log("onFetchTrust", this.king, this.author)
      let filter = {
        kinds: [30077],
        trust: {
          root: this.king,
          context: this.context,
          members: [this.author],
        }
      }

      let r
      try {
        r = await this.search_ndk.fetchEvents(filter)
      } catch (e) {
        this.trust = false
        return
      }

      console.log('trust events response', r)
      if (r.size === 0) {
        this.trust = null
        return
      }
      this.trust = []
      let truster = this.king

      let mapping = {}
      for (let t of r) {
        mapping[t.pubkey] = t
        t.trusted = this.getTagValue(t, "p")
        t.context = this.getTagValue(t, "c")
      }
      while (true) {
        if (!(truster in mapping)) {
          break
        }
        this.trust.push(mapping[truster])
        truster = this.getTagValue(mapping[truster], 'p')
      }
      console.log("web of trust from author", this.trust);
    },
  },
}
</script>

<style>
:root {
  --popper-theme-background-color: var(--bg3);
  --popper-theme-background-color-hover: var(--bg3);
  --popper-theme-text-color: var(--text1);
  --popper-theme-border-radius: 12px;
  --popper-theme-padding: 5px 10px 4px;
  --popper-theme-box-shadow: 0 6px 30px -6px rgba(0, 0, 0, 0.25);
}
</style>

<style scoped>
/* popper content */
.hovercard {
  display: flex;
  flex-direction: column;
  font-weight: bold;
  color: var(--text3);
}
.hierarchy-level {
  margin-top: 5px;
  display: flex;
  align-items: center;
}
.dotted {
  height: 16px;
  border-left: 2px dotted var(--gray8);
  margin-left: 10px;
}
.stamp, .stamp-add {
  display: inline-block;
  fill: var(--aqua3);
  width: 24px;
  height: 16px;
  padding: 0 4px;
  cursor: pointer;
}
.content-header {
  white-space: nowrap;
}
.context {
  font-family: Consolas, Menlo, "Liberation Mono", Courier, monospace;
  border: 1px solid var(--bg5);
}
</style>
