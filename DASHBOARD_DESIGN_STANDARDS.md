# 🎨 Dashboard Design Standards - Invensis Hiring Portal

## 📋 **Overview**
This document outlines the standardized design system for all dashboard components across HR, Manager, Admin, and Cluster portals. The goal is to ensure consistency, professionalism, and optimal user experience across all screen sizes.

## 🎯 **Design Principles**

### **1. Consistency**
- Uniform card sizes, spacing, and typography across all portals
- Consistent color coding for status indicators
- Standardized icon usage and placement

### **2. Responsiveness**
- Mobile-first design approach
- Adaptive layouts for tablet and desktop
- Consistent behavior across all screen sizes

### **3. Accessibility**
- High contrast colors for readability
- Consistent icon and text sizing
- Clear visual hierarchy

## 🎨 **Design Tokens**

### **Typography**
```css
/* Card Label */
.card-label {
    font-size: 16px;          /* 14px on mobile */
    font-weight: 500;
    line-height: 1.5;
    color: #6B7280;           /* text-gray-600 */
}

/* Card Value */
.card-value {
    font-size: 32px;          /* 28px on mobile */
    font-weight: 700;
    line-height: 1.2;
    color: #111827;           /* text-gray-900 */
}
```

### **Spacing**
```css
/* Card Container */
.dashboard-card {
    padding: 20px;            /* 16px on mobile */
    border-radius: 16px;      /* 12px on mobile */
    margin-bottom: 24px;      /* 16px on mobile */
}

/* Icon Container */
.card-icon-container {
    width: 48px;              /* 40px on mobile */
    height: 48px;             /* 40px on mobile */
    padding: 12px;            /* 8px on mobile */
    border-radius: 16px;      /* 12px on mobile */
}

/* Content Spacing */
.card-content {
    margin-left: 16px;        /* 12px on mobile */
}
```

### **Colors**
```css
/* Status Color Schemes */
.status-total { @apply bg-blue-100 text-blue-600; }      /* #DBEAFE #2563EB */
.status-pending { @apply bg-yellow-100 text-yellow-600; } /* #FEF3C7 #D97706 */
.status-assigned { @apply bg-green-100 text-green-600; }  /* #D1FAE5 #059669 */
.status-shortlisted { @apply bg-purple-100 text-purple-600; } /* #F3E8FF #7C3AED */
.status-rejected { @apply bg-red-100 text-red-600; }      /* #FEE2E2 #DC2626 */
.status-reassigned { @apply bg-orange-100 text-orange-600; } /* #FFEDD5 #EA580C */
.status-onhold { @apply bg-indigo-100 text-indigo-600; }  /* #E0E7FF #4F46E5 */
.status-hired { @apply bg-emerald-100 text-emerald-600; } /* #D1FAE5 #059669 */
.status-new { @apply bg-gray-100 text-gray-600; }         /* #F3F4F6 #4B5563 */
```

### **Shadows & Borders**
```css
/* Default State */
.dashboard-card {
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    border: 1px solid #F3F4F6;  /* border-gray-100 */
}

/* Hover State */
.dashboard-card:hover {
    box-shadow: 0px 8px 25px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}
```

## 📱 **Responsive Breakpoints**

### **Mobile (≤768px)**
```css
@media (max-width: 768px) {
    .dashboard-card {
        padding: 16px;
        border-radius: 12px;
    }
    
    .card-icon-container {
        width: 40px;
        height: 40px;
        padding: 8px;
    }
    
    .card-icon {
        font-size: 20px;
    }
    
    .card-label {
        font-size: 14px;
    }
    
    .card-value {
        font-size: 28px;
    }
    
    .dashboard-grid {
        gap: 16px;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }
}
```

### **Tablet (769px - 1024px)**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .dashboard-grid {
        gap: 20px;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }
}
```

### **Desktop (≥1025px)**
```css
@media (min-width: 1025px) {
    .dashboard-grid {
        gap: 24px;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
}
```

## 🧩 **Component Structure**

### **Dashboard Card Component**
```html
<div class="dashboard-card fade-in">
    <div class="flex items-center">
        <!-- Icon Container -->
        <div class="card-icon-container status-[status-name]">
            <i class="fas fa-[icon-name] card-icon"></i>
        </div>
        
        <!-- Content -->
        <div class="card-content">
            <p class="card-label">[Card Label]</p>
            <p class="card-value">[Card Value]</p>
        </div>
    </div>
</div>
```

### **Grid Layout**
```html
<!-- Standard Grid -->
<div class="dashboard-grid">
    <!-- Cards here -->
</div>

<!-- Compact Grid (for more cards) -->
<div class="dashboard-grid-compact">
    <!-- Cards here -->
</div>
```

## 🚀 **Implementation Guide**

### **1. Add CSS to Base Template**
```css
/* Add to templates/base.html */
.dashboard-card { /* ... */ }
.card-icon-container { /* ... */ }
.card-icon { /* ... */ }
.card-content { /* ... */ }
.card-label { /* ... */ }
.card-value { /* ... */ }
.status-[status] { /* ... */ }
.dashboard-grid { /* ... */ }
```

### **2. Update Template Structure**
```html
<!-- Replace old card structure -->
<div class="bg-white rounded-xl shadow-lg p-6 fade-in">
    <div class="flex items-center">
        <div class="p-3 rounded-full bg-[color]-100 text-[color]-600">
            <i class="fas fa-[icon] text-xl"></i>
        </div>
        <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">[Label]</p>
            <p class="text-2xl font-bold text-gray-900">[Value]</p>
        </div>
    </div>
</div>

<!-- With new standardized structure -->
<div class="dashboard-card fade-in">
    <div class="flex items-center">
        <div class="card-icon-container status-[status]">
            <i class="fas fa-[icon] card-icon"></i>
        </div>
        <div class="card-content">
            <p class="card-label">[Label]</p>
            <p class="card-value">[Value]</p>
        </div>
    </div>
</div>
```

### **3. Update Grid Layout**
```html
<!-- Replace old grid -->
<div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-6">

<!-- With new responsive grid -->
<div class="dashboard-grid">
```

## 📊 **Portal-Specific Implementations**

### **HR Dashboard**
- **Cards**: Total, Pending, Assigned, Shortlisted, Rejected, Reassigned, On Hold
- **Status Colors**: Consistent with candidate lifecycle
- **Layout**: 7 cards in responsive grid

### **Manager Dashboard**
- **Cards**: Assigned, Reviewed, Shortlisted, Rejected, On Hold
- **Status Colors**: Focus on review process
- **Layout**: 5 cards in responsive grid

### **Admin Dashboard**
- **Cards**: HR Users, Manager Users, Cluster Users, Total Users
- **Status Colors**: User management focused
- **Layout**: 4 cards in responsive grid

### **Cluster Dashboard**
- **Cards**: Total, Shortlisted, Hired, Pending, On Hold, Rejected
- **Status Colors**: Strategic overview focused
- **Layout**: 6 cards in responsive grid

## ✅ **Quality Assurance Checklist**

### **Visual Consistency**
- [ ] All cards use `.dashboard-card` class
- [ ] All icons use `.card-icon` class
- [ ] All labels use `.card-label` class
- [ ] All values use `.card-value` class
- [ ] Status colors match design tokens

### **Responsive Behavior**
- [ ] Mobile layout (≤768px) displays correctly
- [ ] Tablet layout (769px-1024px) displays correctly
- [ ] Desktop layout (≥1025px) displays correctly
- [ ] Grid adapts to screen size
- [ ] Card sizes adjust appropriately

### **Accessibility**
- [ ] High contrast colors maintained
- [ ] Consistent icon sizing
- [ ] Clear visual hierarchy
- [ ] Proper spacing between elements

### **Performance**
- [ ] CSS classes are reusable
- [ ] No inline styles
- [ ] Efficient grid layouts
- [ ] Smooth hover animations

## 🔄 **Maintenance & Updates**

### **Adding New Status Colors**
```css
/* Add to base template CSS */
.status-[new-status] { @apply bg-[color]-100 text-[color]-600; }
```

### **Modifying Card Sizes**
```css
/* Update responsive breakpoints in base template */
@media (max-width: 768px) {
    .dashboard-card { /* new mobile styles */ }
}
```

### **Adding New Icons**
```html
<!-- Use Font Awesome icons with card-icon class -->
<i class="fas fa-[icon-name] card-icon"></i>
```

## 📚 **Resources**

### **Font Awesome Icons**
- Users: `fa-users`
- Clock: `fa-clock`
- Check: `fa-check`
- Star: `fa-star`
- Times: `fa-times-circle`
- Pause: `fa-pause-circle`
- Random: `fa-random`
- User-tie: `fa-user-tie`
- Chart-line: `fa-chart-line`
- Users-cog: `fa-users-cog`

### **Tailwind CSS Classes**
- Colors: `bg-[color]-100`, `text-[color]-600`
- Spacing: `p-5`, `m-4`, `gap-6`
- Typography: `text-sm`, `text-2xl`, `font-medium`, `font-bold`
- Layout: `flex`, `items-center`, `grid`, `rounded-2xl`

---

**Last Updated**: August 13, 2025  
**Version**: 1.0  
**Maintained By**: Development Team
