# Design System Implementation

This document outlines the design system implementation for the SceneSplit application, matching the provided design specifications.

## Typography

### Font Family
- **Primary Font**: Inter (Google Fonts)
- **Fallback**: system-ui, sans-serif

### Font Weights
- `font-inter-thin` (100)
- `font-inter-extralight` (200)
- `font-inter-light` (300)
- `font-inter-regular` (400) - Default
- `font-inter-medium` (500)
- `font-inter-semibold` (600)
- `font-inter-bold` (700)
- `font-inter-extrabold` (800)
- `font-inter-black` (900)

### Font Sizes
- `text-xs` (12px) - Small text, captions
- `text-sm` (14px) - Body text, labels
- `text-base` (16px) - Default body text
- `text-lg` (18px) - Subheadings
- `text-xl` (20px) - Card titles
- `text-2xl` (24px) - Page headers
- `text-3xl` (30px) - Large headings
- `text-4xl` (36px) - Hero text

## Color System

### Primary Colors
- `bg-background-primary` (#1F2937) - Main background
- `bg-background-secondary` (#131726) - Card backgrounds
- `bg-background-tertiary` (#0D1019) - Input backgrounds
- `bg-background-quaternary` (#070914) - Deepest backgrounds

### Secondary Color (Accent)
- `bg-secondary` (#D4AF37) - Primary accent (Golden)
- `bg-secondary-hover` (#C19B26) - Hover state

### Text Colors
- `text-text-primary` (#FFFFFF) - Primary text (white)
- `text-text-secondary` (#9CA3AF) - Secondary text (gray)
- `text-text-muted` (#6B7280) - Muted text (darker gray)

### Button Colors
- `bg-button-yellow` (#D4AF37) - Primary action buttons
- `bg-button-green` (#10B981) - Success actions
- `bg-button-cyan` (#06B6D4) - Info actions

### Border Colors
- `border-gray-700` - Primary borders
- `border-gray-600` - Lighter borders
- `border-secondary` - Accent borders

## Component Styles

### Buttons
```css
.btn-primary {
  @apply bg-secondary text-black font-inter-semibold px-4 py-2 rounded-lg hover:bg-secondary-hover transition-colors;
}

.btn-secondary {
  @apply bg-gray-700 text-white font-inter-medium px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors;
}
```

### Cards
```css
.card {
  @apply bg-background-secondary rounded-xl p-6 shadow-lg border border-gray-700;
}
```

### Inputs
```css
.input-primary {
  @apply bg-background-tertiary border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-text-muted focus:border-secondary focus:outline-none transition-colors;
}
```

## Layout Specifications

### Sidebar
- **Collapsed Width**: 16 (64px)
- **Expanded Width**: 64 (256px)
- **Background**: `bg-background-primary`
- **Border**: Right border with `border-gray-700`

### Main Content
- **Margin Left**: Adjusted based on sidebar state
  - Collapsed: `ml-16` (64px)
  - Expanded: `ml-64` (256px)

### Header
- **Height**: 20 (80px)
- **Background**: `bg-background-primary`
- **Border**: Bottom border with `border-gray-700`
- **Sticky**: Top positioned

## Icons

### Material Icons
Using Google Material Icons for consistency:
- Projects: `folder`
- Script Breakdown: `list_alt`
- Budget: `account_balance_wallet`
- Menu: `menu`
- Search: `search`

### Usage
Icons are sized at 24px (w-6 h-6) for sidebar links and appropriately colored based on active/inactive states.

## States

### Active States
- **Sidebar Links**: Yellow accent color (`text-secondary`) with left border
- **Filter Tabs**: Yellow background (`bg-secondary`) with black text

### Hover States
- **Buttons**: Darker variants of base colors
- **Cards**: Border color changes to lighter gray
- **Links**: Background color lightens

### Focus States
- **Inputs**: Yellow border (`border-secondary`)
- **Buttons**: Ring outline in yellow

## Responsive Design

### Breakpoints
- **Mobile**: Single column grid
- **Tablet** (md): 2-column grid
- **Desktop** (lg): 3-column grid

### Grid System
Projects are displayed in a responsive grid with consistent gap spacing (gap-8).

## Animation and Transitions

### Sidebar Toggle
- **Duration**: 300ms
- **Easing**: CSS transitions with ease curves

### General Interactions
- **Hover**: 200ms transitions
- **Focus**: Instant visual feedback
- **State Changes**: Smooth color transitions

## Implementation Notes

1. All components use the Inter font family
2. Color system is implemented through Tailwind CSS custom colors
3. Components are built with accessibility in mind
4. Consistent spacing and sizing throughout
5. Material Icons provide consistent iconography
6. Responsive design adapts to different screen sizes

## File Structure

```
src/
├── assets/
│   └── icon/ (Material and custom icons)
├── components/
│   ├── Sidebar.vue
│   └── SidebarLink.vue
├── views/
│   └── ProjectsView.vue
├── style.css (Global styles and design tokens)
└── App.vue (Main layout)
```

This design system ensures consistency across the application while providing flexibility for future enhancements.
