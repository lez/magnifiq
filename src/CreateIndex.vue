<script setup>
import NDK, { NDKEvent, NDKNip07Signer }  from "@nostr-dev-kit/ndk";
import Multiselect from './components/multiselect/Multiselect.vue'
import User from './components/User.vue'
</script>

<template>
  <div class="user">
    <user v-if="user" :pubkey="user.pubkey" :ndk="ndk"/>
  </div>

  <header>
    <a href="/">
      <img class="logo" src="../image/logo.png" width="250">
    </a>
  </header>

  <main>
    <form v-if="!stored" class="form">
      <label for="destination">Destination </label>
      <input type="text" name="destination" ref="destination" required>

      <!-- TODO: Crawl title based on destination.
      <label for="title">Title </label>
      <input type="text" name="title" ref="title" class="title" disabled> -->

      <label for="content">Content </label>
      <textarea name="content" ref="content" rows="4"/>

      <label for="tags">Tags </label>
      <multiselect
          v-model="tags"
          :options="options"
          ref="tags"
          :multiple="true"
          :loading="isLoading"
          placeholder="Add tags..."
          openDirection="below"
          :hide-selected="true"
          :show-labels="true"
          label="tag"
          track-by="tag"
          :close-on-select="true"
          @search-change="onSearchChange"
          @select="onOptionSelected"
          :optionsLimit="20"
          :showNoOptions="false"
          :max="5">

        <!-- Signal new tags -->
        <template v-slot:option="slotProps">
          <span :class="{isnew: slotProps.option.new_}">
            {{ slotProps.option.tag }}
          </span>
          <span v-if="slotProps.option.new_">
            (add new tag)
          </span>
        </template>

        <!-- New tags are colored differently -->
        <template v-slot:tag="slotProps">
          <span class="multiselect__tag" :class="{isnew: slotProps.option.new_}" :key="slotProps.index">
            <span v-text="slotProps.option.tag"></span>
            <i tabindex="1" @keypress.enter.prevent="$refs.tags.removeElement(slotProps.option)"
               @mousedown.prevent="$refs.tags.removeElement(slotProps.option)" class="multiselect__tag-icon"></i>
          </span>
        </template>

      </multiselect>

      <button class="create-button" @click.prevent="onCreateIndex">Create Index</button>
    </form>
    <div v-else>
      <pre>{{stored_event}}</pre>
      <button class="create-button" @click.prevent="onClear">Add new index</button>
    </div>
  </main>

  <footer>
    Made by <a href="https://njump.me/npub1elta7cneng3w8p9y4dw633qzdjr4kyvaparuyuttyrx6e8xp7xnq32cume">Lez</a>
    -
    <a href="https://github.com/lez/magnifiq">Source code</a>
  </footer>
</template>

<script>
export default {
  data () {
    return {
      // ndk
      ndk: null,
      npub: null,
      user: null,
      // autocomplete
      isLoading: false,
      tags: [],
      options: [],
      // after submit
      stored: false,
      stored_event: null,
    }
  },
  async mounted() {
    window.c = this
    this.signer = new NDKNip07Signer()
    this.user = await this.signer.user()
    this.ndk = new NDK({
      signer: this.signer,
      explicitRelayUrls: ["ws://127.0.0.1:8080"],
    });
    await this.ndk.connect();
    console.log("User:", this.user.npub)
  },
  methods: {
    async onOptionSelected(e) {
      //TODO: Prefetch number of results.
    },

    async onSearchChange (searchQuery) {
      if (searchQuery === "") {
        this.options = []
        return
      }

      this.isLoading = true // Careful! Hard on CPU.

      let r = await fetch('/api/tags?prefix=' + searchQuery)
      r = await r.json()
      console.log(`Tags by prefix [${searchQuery}]:`, r.tags)

      if (r.tags.length == 0) {
        this.options = [{tag: searchQuery, new_: true}]
      } else {
        this.options = r.tags.map(t => { return { tag: t, new_: false}})
      }

      this.isLoading = false
    },

    domainFrom(destination) {
      let url = new URL(destination)
      if (url.protocol.startsWith("http")) {
        let nameparts = url.host.split(/\./)
        if (nameparts.length < 2) {
          return null
        }
        return nameparts[nameparts.length-2] + "." + nameparts[nameparts.length-1]
      }
      return null
    },

    async onCreateIndex(e) {
      // Search tags
      let tags = this.tags.map(t => {return ["s", t.tag]})

      // Destination
      let dest = this.$refs.destination.value
      tags.push(["dest", dest])

      //TODO: Try prefixing with http(s)://
      let domain = this.domainFrom(dest)
      if (domain) {
        tags.push(["D", domain])
      }
      let event = new NDKEvent(this.ndk, {
        kind: 78,
        content: this.$refs.content.value,
        tags
      })
      console.log("Publishing event", event)
      let r = await event.publish()
      console.log("r", r)
      this.stored = r.size
      console.log("event", event)
      let nevent = await event.toNostrEvent()
      this.stored_event = JSON.stringify(nevent, null, 4)
    },
    async onClear(e) {
      this.tags = []
      this.stored_event = null
      this.stored = false
    }
  }
}
</script>

<style>
h3 {
  margin: 1em;
}
.multiselect {
    height: 48px;
}
.multiselect__tags {
  background: var(--bg1);
  min-height: 48px;
  border-radius: 12px;
  border: 0;
}
.multiselect__select {
  color: var(--bg1);
}
.multiselect__placeholder {
  font-size: 1.5em;
  margin: 7px 15px;
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
.multiselect__option:has(> span.isnew), .multiselect__option:has(> span.isnew):after {
  background: var(--purple3);
}
.multiselect__option--highlight, .multiselect__option--highlight:after {
  background: var(--aqua4);
}
.multiselect__tag {
  margin-top: 6px;
  margin-left: 4px;
  font-size: 1.5em !important;
}
.multiselect__tag.isnew {
  background: var(--purple3);
}
</style>

<style scoped>
.tags span {
  background: var(--aqua2);
  padding: 4px;
  margin-right: 12px;
}
.form {
  display: grid;
  grid-template-columns: [labels] auto [controls] 1fr;
  grid-auto-flow: row;
  grid-gap: .8em .5em;
  background: var(--bg3);
  padding: 1.2em;
  width: 36em;
}
.form > label,
.form > fieldset  {
  grid-column: labels;
  grid-row: auto;
}
.form > input,
.form > textarea {
  background: var(--bg1);
  color: var(--text2);
  font-size: 20px;
}
.form > input,
.form > select,
.form > textarea,
.form > button {
  grid-column: controls;
  grid-row: auto;
  padding: .5em 1em;
  border: 0;
  border-radius: 12px;
}
.form > fieldset {
  grid-column: span 2;
}
.form > button {
  margin-top: 40px;
  background: var(--primary2);
  color: white;
  padding: 8px;
  border-radius: 12px;
}
.isnew {
  /*TODO: only in dropdown!*/
  margin-right: 20px;
}
pre {
  border: 2px solid var(--aqua3);
  max-width: 720px;
  font-size: 0.7em;
  overflow: hidden;
  padding: 1em;
  height: 550px;
  max-height: 550px;
  border-radius: 12px;
  overflow-x: hidden;
  overflow-y: scroll;
}
.user {
  position: absolute;
  top: 10px;
  right: 20px;
}

</style>
