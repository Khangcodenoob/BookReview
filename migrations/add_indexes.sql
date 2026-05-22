-- Migration: Add database indexes for performance
-- Run this to improve query performance

-- Indexes for books table
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_category_id ON books(category_id);
CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at);
CREATE INDEX IF NOT EXISTS idx_books_publisher ON books(publisher);

-- Indexes for reviews table
CREATE INDEX IF NOT EXISTS idx_reviews_book_id_status ON reviews(book_id, status);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status);

-- Indexes for bookmarks table
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_book_id ON bookmarks(book_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at);

-- Indexes for user_shelves table
CREATE INDEX IF NOT EXISTS idx_user_shelves_user_shelf ON user_shelves(user_id, shelf_type);
CREATE INDEX IF NOT EXISTS idx_user_shelves_book_id ON user_shelves(book_id);

-- Indexes for user_follows table
CREATE INDEX IF NOT EXISTS idx_user_follows_follower ON user_follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_user_follows_following ON user_follows(following_id);

-- Indexes for review_votes table
CREATE INDEX IF NOT EXISTS idx_review_votes_review_id ON review_votes(review_id);
CREATE INDEX IF NOT EXISTS idx_review_votes_user_id ON review_votes(user_id);

-- Indexes for review_comments table
CREATE INDEX IF NOT EXISTS idx_review_comments_review_id ON review_comments(review_id);
CREATE INDEX IF NOT EXISTS idx_review_comments_parent_id ON review_comments(parent_id);

-- Indexes for book_tags table
CREATE INDEX IF NOT EXISTS idx_book_tags_book_id ON book_tags(book_id);
CREATE INDEX IF NOT EXISTS idx_book_tags_tag_id ON book_tags(tag_id);

-- Indexes for tags table
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- Indexes for categories table
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- Indexes for orders (e-commerce)
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Indexes for order_items (e-commerce)
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_book_id ON order_items(book_id);

-- Indexes for user_activities table
CREATE INDEX IF NOT EXISTS idx_user_activities_user_created ON user_activities(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_user_activities_type ON user_activities(activity_type);

-- Indexes for reading_challenges table
CREATE INDEX IF NOT EXISTS idx_reading_challenges_active ON reading_challenges(is_active);
CREATE INDEX IF NOT EXISTS idx_reading_challenges_dates ON reading_challenges(start_date, end_date);

-- Indexes for user_challenges table
CREATE INDEX IF NOT EXISTS idx_user_challenges_user ON user_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_challenge ON user_challenges(challenge_id);

-- Indexes for book_views table
CREATE INDEX IF NOT EXISTS idx_book_views_user_book ON book_views(user_id, book_id);
CREATE INDEX IF NOT EXISTS idx_book_views_viewed_at ON book_views(viewed_at);

