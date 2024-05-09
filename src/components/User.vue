<template>
  <div class="user-wrapper">
    <a v-if="link" class="user-name" :href="'http://njump.me/'+npub" :title="npub + ' (' + user.pubkey + ')'">
      {{ name }}
    </a>
    <span v-else class="user-name">
      {{ name }}
    </span>
  </div>
</template>

<script>
export default {
  name: "user",
  props: {
    pubkey: {type: String, required: true},
    link: {type: Boolean, default: true},
    ndk: {type: Object},
  },
  data: function () {
    return {
      npub: null,
      user: null,
    }
  },
  methods: {
    async fetch_name() {
      console.log("fetching name for", this.pubkey)
      await this.user.fetchProfile()
      console.log("Profile for", JSON.stringify(this.pubkey), "is", JSON.stringify(this.user.profile))
    }
  },
  beforeMount: function() {
    this.user = this.ndk.getUser({pubkey: this.pubkey})
    this.npub = this.user.npub
  },
  mounted: function() {
    this.fetch_name()
  },
  computed: {
    name() {
      if (this.user?.profile?.name) {
        return this.user.profile.name
      }
      return this.npub.slice(0, 9) + "..." + this.npub.slice(-4)
    }
  }
}
</script>

<style scoped>
.user-wrapper {
  display: inline-flex;
  align-items: center;
}
.user-name {
  padding: 0 4px;
}
</style>
