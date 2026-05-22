# Kế hoạch cải thiện dự án Hybi Books

## Mục tiêu
Cải thiện code quality, performance, security và maintainability của dự án.

## Các bước thực hiện

### Phase 1: Code Organization (Ưu tiên cao)
- [ ] Tách `app.py` thành modules
- [ ] Tạo Blueprint cho các routes
- [ ] Tách utilities functions
- [ ] Tạo config module

### Phase 2: Security (Ưu tiên cao)
- [ ] Di chuyển SECRET_KEY sang environment variables
- [ ] Thêm CSRF protection
- [ ] Cải thiện input validation
- [ ] Thêm rate limiting cho sensitive endpoints

### Phase 3: Performance (Ưu tiên trung bình)
- [ ] Thêm database indexes
- [ ] Implement caching
- [ ] Optimize queries
- [ ] Lazy load images

### Phase 4: Features (Ưu tiên trung bình)
- [ ] RESTful API
- [ ] Export/Import data
- [ ] Notifications system
- [ ] Advanced search

### Phase 5: Testing & Documentation (Ưu tiên thấp)
- [ ] Unit tests
- [ ] Integration tests
- [ ] API documentation
- [ ] Code comments

## Bắt đầu với Phase 1

### Bước 1: Tạo cấu trúc thư mục mới
```
app/
├── __init__.py
├── config.py
├── routes/
│   ├── __init__.py
│   ├── books.py
│   ├── auth.py
│   ├── reviews.py
│   ├── admin.py
│   └── api.py
└── utils/
    ├── __init__.py
    ├── db.py
    ├── auth.py
    ├── markdown.py
    └── images.py
```

### Bước 2: Tạo config.py
- Load từ environment variables
- Default values cho development
- Validation

### Bước 3: Tách routes
- Books routes -> routes/books.py
- Auth routes -> routes/auth.py
- Review routes -> routes/reviews.py
- Admin routes -> routes/admin.py
- API routes -> routes/api.py

### Bước 4: Tách utilities
- Database helpers -> utils/db.py
- Auth helpers -> utils/auth.py
- Markdown processing -> utils/markdown.py
- Image handling -> utils/images.py

## Notes
- Giữ backward compatibility trong quá trình refactor
- Test từng module sau khi tách
- Commit thường xuyên
- Document các thay đổi
