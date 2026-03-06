
---

# 📕 **API_DASHBOARD_DOC.md**  
*(توثيق كامل لكل CRUD في لوحة التحكم)*

```md
# 🔐 Dashboard API Documentation
كل الـ endpoints التالية تتطلب JWT Token  
المستخدم يجب أن يكون على الأقل **Editor** أو **Admin** أو **Super Admin**  
(حسب القسم)

---

# 👤 1. Accounts Module

## 1.1 إنشاء أول سوبر أدمن
### **POST /api/accounts/setup/**
*(مرة واحدة فقط)*

## 1.2 تسجيل الدخول
### **POST /api/accounts/login/**

## 1.3 جميع المستخدمين (Super Admin فقط)
### **GET /api/accounts/users/**

## 1.4 إنشاء مستخدم جديد
### **POST /api/accounts/users/create/**

## 1.5 تعديل مستخدم
### **PATCH /api/accounts/users/{id}/**

## 1.6 حذف مستخدم
### **DELETE /api/accounts/users/{id}/**

---

# ⚙️ 2. Settings Module (Admin + Super Admin)

## 2.1 Get Site Settings  
### **GET /api/settings/**

## 2.2 Update Settings  
### **PUT /api/settings/**

---

# 🖼️ 3. CMS Module (Editor + Admin + Super Admin)

### Heroes
- **GET /api/cms/admin/heroes/**
- **POST /api/cms/admin/heroes/**
- **GET /api/cms/admin/heroes/{id}/**
- **PATCH /api/cms/admin/heroes/{id}/**
- **DELETE /api/cms/admin/heroes/{id}/**

### Pages
- **GET /api/cms/admin/pages/**
- **POST /api/cms/admin/pages/**
- **GET /api/cms/admin/pages/{id}/**
- **PATCH /api/cms/admin/pages/{id}/**
- **DELETE /api/cms/admin/pages/{id}/**

### Footer Columns + Links  
*(داخل Django Admin الآن، لأنها ثابتة)*

---

# 📰 4. Blog Module (Editor + Admin + Super Admin)

### Categories
- GET /api/blog/admin/categories/
- POST /api/blog/admin/categories/
- PATCH /api/blog/admin/categories/{id}/
- DELETE /api/blog/admin/categories/{id}/

### Tags
- GET /api/blog/admin/tags/
- POST /api/blog/admin/tags/
- PATCH /api/blog/admin/tags/{id}/
- DELETE /api/blog/admin/tags/{id}/

### Blog Posts
- GET /api/blog/admin/posts/
- POST /api/blog/admin/posts/
- GET /api/blog/admin/posts/{id}/
- PATCH /api/blog/admin/posts/{id}/
- DELETE /api/blog/admin/posts/{id}/

---

# 👥 5. Team Module (Editor + Admin + Super Admin)

- GET /api/team/admin/
- POST /api/team/admin/
- GET /api/team/admin/{id}/
- PATCH /api/team/admin/{id}/
- DELETE /api/team/admin/{id}/

---

# ⚖️ 6. Legal Pages (Editor + Admin + Super Admin)

- GET /api/legal/admin/
- POST /api/legal/admin/
- GET /api/legal/admin/{id}/
- PATCH /api/legal/admin/{id}/
- DELETE /api/legal/admin/{id}/

---

# 🔧 7. Services Module (Editor + Admin + Super Admin)

### Practice Areas
- GET /api/services/admin/areas/
- POST /api/services/admin/areas/
- PATCH /api/services/admin/areas/{id}/
- DELETE /api/services/admin/areas/{id}/

### Services
- GET /api/services/admin/items/
- POST /api/services/admin/items/
- PATCH /api/services/admin/items/{id}/
- DELETE /api/services/admin/items/{id}/

---

# 🔍 8. SEO Module (Admin + Super Admin)

### Default SEO
- GET /api/seo/admin/default/
- PUT /api/seo/admin/default/

### Page SEO
- GET /api/seo/admin/pages/
- POST /api/seo/admin/pages/
- GET /api/seo/admin/pages/{id}/
- PATCH /api/seo/admin/pages/{id}/
- DELETE /api/seo/admin/pages/{id}/

---

# 📨 9. Messaging Module (Admin + Super Admin)

### Get all messages
- GET /api/messaging/admin/messages/

### Single message view/update
- GET /api/messaging/admin/messages/{id}/
- PATCH /api/messaging/admin/messages/{id}/
