<script setup>
import Multiselect from './multiselect/Multiselect.vue'
import NDK, { NDKEvent, NDKNip07Signer }  from "@nostr-dev-kit/ndk";
import Trust from './Trust.vue'
import User from "./User.vue"
import KingSelect from "./KingSelect.vue"
import stamp_add from "/svg/stamp-add.svg?raw"
</script>

<template>
  <div>
    <div class="user">
      <user v-if="pubkey" :pubkey="pubkey" :ndk="ndk"/>
    </div>
    <div class="search">
      <multiselect
          v-model="value"
          :options="options"
          ref="search"
          :multiple="true"
          :loading="isLoading"
          placeholder="Start typing..."
          openDirection="below"
          :hide-selected="true"
          :show-labels="true"
          :customLabel="customLabel"
          :close-on-select="true"
          @search-change="onSearchChange"
          @select="onOptionSelected"
          @submit="onSearch"
          :optionsLimit="20"
          :showNoOptions="false"
          :max="5">

        <template v-slot:afterList>
          <div class="afterList" v-if="options.length">
            <div>Select a tag from the list.</div>
          </div>
        </template>
      </multiselect>

      <div class="menu-line">
        <div style="margin-left: auto;" />
        <king-select v-model="king" :value="king" :ndk="ndk" :show_reset="king !== 'df5134e31206e6a5c898ea12efaa2c8dadc556e2ab1a273ab383d817c3404ff1'"/>
      </div>

      <button class="search-button" :disabled="!value.length" @click="onSearch">Search</button>
    </div>

    <div class="results">
      <div v-if="indexer" class="indexer">
        <div class="indexer-inner">
          Results by <user :pubkey="indexer" :ndk="ndk"/>
          <trust :king="king" :author="indexer" context="*" :ndk="ndk" :search_ndk="search_ndk" :fetch_="true" @trust="onTrustIndexer()"/>
        </div>
      </div>

      <div v-if="results.length && results[0] === null">There are no trusted results</div>
      <div class="result" v-for="r in results" :key="r?.id">
        <hr v-if="r === null" width="98%">
        <div v-else>
          <div class="result-header">
            <a v-if="getTagValue(r, 'dest')" :href="getTagValue(r, 'dest')">{{ getTagValue(r, 'dest') }}</a>
            <span v-else class="missing">Missing destination!</span>
            <!-- <span class="explore"><a :href="'https://njump.me/'+r.id">o</a></span> --><!-- TODO: add relay data to nevent -->
          </div>

          <div class="content">
            {{ r.content }}
          </div>

          <div class="tags">
            <template v-for="tag in r.tags" :key="tag">
              <span v-if="tag[0]=='s'">
                {{ tag[1] }}
              </span>
            </template>
          </div>

          <div v-if="!indexer" class="author">
            Indexed by <user :pubkey="r.pubkey" :ndk="ndk" @click.once.prevent="onAuthorClick(r)"/>
            <trust v-if="!r.unauthorized" :king="king" :author="r.pubkey" context="*" :ndk="ndk" :search_ndk="search_ndk"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  components: { Multiselect, Trust, User, KingSelect },
  data () {
    return {
      value: [],
      isLoading: false,
      options: [],
      results: [],
      ndk: null,
      search_ndk: null,
      king: document.cookie.split('; ').find(c => c.startsWith('king='))?.split('=')[1] || "df5134e31206e6a5c898ea12efaa2c8dadc556e2ab1a273ab383d817c3404ff1",
      indexer: null,
      indexer_trusted: false,
      pubkey: null,
    }
  },
  beforeMount () {
    let search_relays = ["wss://relay.magnifiq.tech"]
    let profile_relays = ["wss://bitcoinmaximalists.online", "wss://relay.primal.net", "wss://relay.damus.io"]

    this.search_ndk = new NDK({
      explicitRelayUrls: search_relays,
    })
    this.ndk = new NDK({
      //TODO: if an unreachable relay is in the list, the search relay is not tried :/
      explicitRelayUrls: search_relays.concat(profile_relays)
    })
  },
  async mounted () {
    window.x = this
    this.$refs.search.activate()
    window.localStorage.debug = ''

    await this.ndk.connect()
    await this.search_ndk.connect()

    this.search_ndk.signer = new NDKNip07Signer()

    let user = await this.search_ndk.signer.user()
    console.log('user', user)
    this.pubkey = user?.pubkey
    console.log('pubkey', this.pubkey)
  },
  methods: {
    async onAuthorClick (result) {
      console.log("Click", result.pubkey);
      let u = this.ndk.getUser({pubkey: result.pubkey})
      this.value = ["indexer:"+u.npub]
      this.$nextTick(this.onSearch)
    },
    async onOptionSelected (option) {
      console.log("onOptionSelected", option)
    },
    async onSearchChange (searchQuery) {
      console.log("onSearchChange", searchQuery)
      if (searchQuery === "") {
        this.options = []
        return
      }

      this.isLoading = true // Careful! Hard on CPU.

      let r = await fetch('/api/tags?prefix=' + searchQuery)
      r = await r.json()
      console.log(`Tags by prefix [${searchQuery}]:`, r.tags)

      this.options = r.tags
      this.isLoading = false
    },

    async onSearch (x) {
      if (this.value.length == 0) {
        console.log("No tags, no search.")
        return
      }
      console.log("Search!", Array.from(this.value))

      let tags = []
      this.indexer = null

      for (let t of this.value) {
        if (t.startsWith("indexer:")) {
          let npub = t.slice("indexer:".length)
          let u = this.ndk.getUser({ npub })
          this.indexer = u.pubkey
        } else {
          tags.push(t)
        }
      }

      let filter = {
        kinds: [78],
      }
      if (tags.length) {
        filter["&s"] = tags
      }

      if (this.indexer) {
        filter.authors = [this.indexer]
      } else {
        filter.trust = {
          root: this.king,
          context: "*",
          // depth: 4
        }
      }

      console.log("REQ filter", filter)
      let events = await this.search_ndk.fetchEvents(filter)
      console.log("< REQ events", events)
      let events_arr = Array.from(events)

      console.log("< REQ events_arr", events_arr)
      let result_ids = new Set(events_arr.map(ev => ev.id))
      console.log("Approved result ids", result_ids)

      this.results = events_arr.sort((a, b) => {
        // Invalid events go to the bottom.
        if (this.getTagValue(a, "dest") && !this.getTagValue(b, "dest")) return -1;
        if (!this.getTagValue(a, "dest") && this.getTagValue(b, "dest")) return 1;

        // Fewer tags are ranked better to avoid tag bloat.
        if (this.scnt(a) < this.scnt(b)) return -1;
        if (this.scnt(a) > this.scnt(b)) return 1;

        return 0;
      })
      console.log("Results", this.results)

      if (this.indexer) return

      let hr = false
      // Fetching unauthorized results.

      filter = {...filter} // Make console log keep original filter.
      delete filter["trust"]

      console.log("unauthorized filter", filter)
      let all_results = await this.search_ndk.fetchEvents(filter)

      if (all_results.size === 0)
        return

      this.results.push(null) //<hr>

      all_results.forEach(e => {
        if (!result_ids.has(e.id)) {
          e.unauthorized = true
          this.results.push(e)
        }
      }, this)
    },

    scnt (event) {
      let n = 0
      for (let t of event.tags){
        if (t[0] == "s") {
          n += 1
        }
      }
      return n
    },

    // Return first value of tag by tagname.
    getTagValue (event, tagname){
      for (let t of event.tags) {
        if (t[0] == tagname) {
          return t[1]
        }
      }
      return null
    },
    customLabel (label) {
      if (label.startsWith("indexer:")) {
        return label.slice(0, 17) + "..." + label.slice(-4)
      }
      return label
    },
    async onTrustIndexer () {
      if (!confirm("Trust this person to index sites?")) return

      this.search_ndk.signer = new NDKNip07Signer()

      let e = new NDKEvent(this.search_ndk, {
        kind: 30077,
        tags: [
          ["d", this.indexer + "/*"],
          ["c", "*"],
          ["p", this.indexer],
        ]
      })

      let r = await e.publish()
      console.log("Trust published", r)
    },
  },
}
</script>


<style>
.multiselect {
    height: 64px;
}
.multiselect__tags {
  background: var(--bg1);
  min-height: 64px;
  border-radius: 12px;
  border: 1px solid var(--text2);
}
.multiselect__select {
  color: var(--bg1);
}
.multiselect__placeholder {
  font-size: 1.5em;
  margin: 4px 13px;
}
input.multiselect__input {
  color: var(--text2);
  box-sizing: content-box;
  min-height: 46px;
  font-size: 1.5em;
  margin-left: 8px;
  border: 0px;
  padding: 0 0 0 5px;
  box-shadow: 0 0 0 0;
}
input.multiselect__input:focus {
  background: var(--bg1);
  box-shadow: 0 0 0 0;
}
.multiselect__content-wrapper {
  background: var(--bg1);
}
.multiselect__option--highlight, .multiselect__option--highlight:after {
  background: var(--aqua4);
}
.multiselect__tag {
  margin-top: 6px;
  margin-left: 4px;
  background: var(--aqua4);
  font-size: 1.5em !important;
}
</style>

<style scoped>
.search {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 760px;
  margin: 0 auto 16px auto;
}
.search-button:disabled {
  background-color: var(--primary1);
  cursor: default;
}
.search-button {
  color: white;
  background-color: var(--primary1);
  font-weight: bold;
  font-size: 20px;
  border-radius: 12px;
  border: 0px;
  padding: 9px 17px;
  width: 230px;
  height: 64px;
}
.search-button:hover {
  background-color: var(--primary2);
  cursor: pointer;
}
.search-button:active {
  background-color: var(--primary3);
}
.results {
  width: 760px;
  margin: 0 auto;
}
.result {
  padding: 8px 0px;
  font-size: 20px;
}
.tags span {
  background: var(--aqua3);
  color: white;
  padding: 2px 6px;
  margin-right: 12px;
  border-radius: 8px;
}
.afterList {
  display: flex;
  height: 70px;
  padding: 20px 100px;
  align-items: center;
}
.content {
  margin-bottom: 10px;
}
.missing {
  background: red;
}
.author {
  color: var(--text5);
}
svg {
  fill: var(--text5);
}
.menu-line {
  width: 760px;
  display: flex;
  flex-direction: row;
}
.indexer {
  background: var(--bg4);
  border-radius: 12px;
  padding: 8px;
}
.indexer-inner {
  display: inline-flex;
  align-items: center;
}
.user {
  position: absolute;
  top: 10px;
  right: 20px;
}
.stamp-add {
  margin-left: 5px;
  width: 20px;
  height: 20px;
  cursor: pointer;
}
</style>
