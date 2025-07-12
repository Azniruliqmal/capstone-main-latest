
<template>
  	<Teleport to="body">
    		<div class="flex flex-col fixed inset-0 portalPopupOverlay" :style="popupStyle" @click="onOverlayClick">
      			<div ref="relContainerRef" :style="relativeStyle"><slot></slot></div>
    		</div>
  	</Teleport>
</template>
<script setup >
  	import { ref, computed, onMounted, onUnmounted, nextTick  } from 'vue';
  	
  	
  	const props = defineProps({
    		isOpen: { type: Boolean, default: false },
    		overlayColor: { type: String },
    		placement: { type: String, default: "Centered" },
    		zIndex: { type: Number, default: 100 },
    		left: { type: Number, default: 0 },
    		right: { type: Number, default: 0 },
    		top: { type: Number, default: 0 },
    		bottom: { type: Number, default: 0 },
    		onOutsideClick: { type: Function },
    		relativeLayerRef: { type: HTMLElement },
  	});
  	
  	const relContainerRef = ref<HTMLElement | null>(null);
    		const relativeStyle = ref<any>({
      			opacity: '0',
      			alignSelf: 'flex-start'
    		});
    		
    		const setPosition = () => {
      			const relativeItem = props.relativeLayerRef?.getBoundingClientRect();
      			const el = relContainerRef.value;
      			const containerItem = el?.getBoundingClientRect();
      			const style: any = {};
      			
      			if (relativeItem && containerItem) {
        				const {
          					x: relativeX,
          					y: relativeY,
          					width: relativeW,
          					height: relativeH,
        				} = relativeItem;
        				const { width: containerW, height: containerH } = containerItem;
        				
        				style.position = 'absolute';
        				
        				switch (props.placement) {
          					case 'Top left':
            						style.top = relativeY - containerH - props.top + 'px';
            						style.left = relativeX + props.left + 'px';
            						break;
          					case 'Top right':
            						style.top = relativeY - containerH - props.top + 'px';
            						style.left = relativeX + relativeW - containerW - props.right + 'px';
            						break;
          					case 'Bottom left':
            						style.top = relativeY + relativeH + props.bottom + 'px';
            						style.left = relativeX + props.left + 'px';
            						break;
          					case 'Bottom right':
            						style.top = relativeY + relativeH + props.bottom + 'px';
            						style.left = relativeX + relativeW - containerW - props.right + 'px';
            						break;
        				}
        				
        				relativeStyle.value = style;
      			} else {
        				style.maxWidth = '90%';
        				style.maxHeight = '90%';
        				relativeStyle.value = style;
      			}
    		}
    		
    		const onOverlayClick = (e: MouseEvent) => {
      			const target = e.target as HTMLElement;
      			if (props.onOutsideClick && target.classList.contains("portalPopupOverlay")) {
        				props.onOutsideClick();
      			}
      			e.stopPropagation();
    		}
    		
    		const popupStyle = computed(() => {
      			const style: any = {
        				zIndex: props.zIndex ?? 100,
          					opacity: 1,
      			};
      			
      			if (props.overlayColor) {
        				style.backgroundColor = props.overlayColor;
      			}
      			
      			if (!props.relativeLayerRef) {
        				switch (props.placement) {
          					case 'Centered':
            						style.alignItems = 'center';
            						style.justifyContent = 'center';
            						break;
          					case 'Top left':
            						style.alignItems = 'flex-start';
            						break;
          					case 'Top center':
            						style.alignItems = 'center';
            						break;
          					case 'Top right':
            						style.alignItems = 'flex-end';
            						break;
          					case 'Bottom left':
            						style.alignItems = 'flex-start';
            						style.justifyContent = 'flex-end';
            						break;
          					case 'Bottom center':
            						style.alignItems = 'center';
            						style.justifyContent = 'flex-end';
            						break;
          					case 'Bottom right':
            						style.alignItems = 'flex-end';
            						style.justifyContent = 'flex-end';
            						break
        				}
      			}
      			
      			return style;
    		})
    		
    		onMounted(() => {
      			nextTick(setPosition);
      			window.addEventListener('resize', setPosition);
      			window.addEventListener('scroll', setPosition, true);
    		})
    		
    		onUnmounted(() => {
      			window.removeEventListener('resize', setPosition);
      			window.removeEventListener('scroll', setPosition, true);
    		})
    		</script>
    		
    		