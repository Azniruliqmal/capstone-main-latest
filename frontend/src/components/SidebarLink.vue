<template>
  <div
    class="flex items-center w-full max-w-full overflow-hidden p-3 rounded-lg hover:bg-gray-700 transition cursor-pointer"
    :class="[
      active ? 'bg-gray-700 border-l-2 border-secondary' : '',
      !expanded ? 'justify-center px-0' : 'gap-3'
    ]"
    style="min-width:0;"
  >
    <div class="flex-shrink-0 flex items-center justify-center w-6 h-6">
      <span
        v-if="materialIcon"
        class="material-icons text-xl"
        :class="active ? 'text-secondary' : 'text-text-muted'"
      >{{ materialIcon }}</span>
      <img 
        v-else-if="iconSrc" 
        :src="iconSrc" 
        alt="icon" 
        class="w-6 h-6 object-contain"
        :class="active ? 'filter brightness-0 saturate-100 invert-[.85] sepia-[.85] saturate-[7] hue-rotate-[36deg] brightness-[1.1]' : 'filter brightness-0 saturate-100 invert-[.5]'"
      />
      <span v-else class="text-xl" :class="active ? 'text-secondary' : 'text-text-muted'">{{ icon }}</span>
    </div>
    <span
      v-if="expanded"
      class="whitespace-nowrap font-inter-medium text-sm overflow-hidden text-ellipsis"
      :class="active ? 'text-text-primary' : 'text-text-secondary'"
    >
      {{ label }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  icon: String,
  iconSrc: String,
  materialIcon: String,
  label: String,
  expanded: Boolean,
  active: Boolean,
})
</script>
