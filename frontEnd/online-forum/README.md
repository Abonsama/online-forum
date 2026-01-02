# Community Forum Platform - Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** December 30, 2024  
**Project Status:** MVP Development Phase  
**Team:** 2 developers (Frontend: Next.js | Backend: 3 years experience)

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Project Goals & Vision](#project-goals--vision)
3. [MVP Scope](#mvp-scope)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Backend Requirements](#backend-requirements)
6. [Frontend Requirements](#frontend-requirements)
7. [API Contract](#api-contract)
8. [Database Schema](#database-schema)
9. [Development Workflow](#development-workflow)
10. [Testing Checklist](#testing-checklist)
11. [Future Enhancements](#future-enhancements)

---

## Product Overview

### What We're Building

A **minimal, fast, and welcoming community forum platform** where users can create and discover discussions on any topic. Think of it as a streamlined Reddit-style platform with a focus on simplicity and user experience.

### Key Characteristics

- **Minimal:** Clean interface, no clutter, fast loading
- **Welcoming:** Low barrier to entry, intuitive UX
- **Fast:** Optimized performance, quick interactions
- **Diverse:** Support for any topic/community

### Core User Flow
```
1. User visits homepage → Sees feed of posts
2. User can browse/search without account
3. User registers/logs in → Can create posts & vote
4. User creates post → Selects topic → Post appears in feed
5. Other users vote/engage → Content is ranked
```

---

## Project Goals & Vision

### MVP Goals (Current Phase)

- ✅ Build a working forum with core functionality
- ✅ Practice Next.js (Frontend) and backend API development
- ✅ Create a solid foundation for future features
- ✅ Learn collaborative development workflow

### Long-term Vision (Post-MVP)

- Add nested comments system
- Implement AI-powered topic detection
- Build personalized recommendation algorithm
- Support images, videos, and rich media
- Scale to handle thousands of users

---

## MVP Scope

### What's IN the MVP ✅

- User registration and authentication
- Text-only post creation
- Topic/thread categorization
- Post feed with sorting (Hot/New/Top)
- Upvote/downvote system
- Search functionality
- Report content feature
- Basic post management (edit/delete)

### What's OUT of the MVP ❌

- Comments (coming in Phase 2)
- User profiles (bio, avatar, history)
- Image/video uploads
- AI features
- Notifications
- Direct messaging
- Karma/reputation system
- Advanced moderation tools

---

## User Roles & Permissions
```

| Feature        | Anonymous Users | Registered Users | Post Owner |
|----------------|-----------------|------------------|------------|
| View posts     |        ✅       |        ✅       |      ✅    |
| Search content |        ✅       |        ✅       |      ✅    |
| Create posts   |        ❌       |        ✅       |      ✅    |
| Vote (up/down) |        ❌       |        ✅       |      ✅    |
| Report posts   |        ❌       |        ✅       |      ✅    |
| Edit posts     |        ❌       |        ❌       |      ✅    |
| Delete posts   |        ❌       |        ❌       |      ✅    |
```
**Note:** Anonymous users can only browse and search. All interactions require registration.

---

## Backend Requirements

> **Backend Developer:** This section is for you! Everything you need to build is documented here.

### Technology Stack (Suggested)

- **Language:** Node.js (Express), Python (FastAPI/Django), or your preference
- **Database:** PostgreSQL (recommended) or MongoDB
- **Authentication:** JWT tokens or session-based
- **ORM:** Prisma, TypeORM, SQLAlchemy, or raw SQL

---

### 1. Authentication System

#### Endpoints to Build

##### `POST /api/auth/register`

**Purpose:** Create a new user account

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```

**Validation Rules:**
- `username`: 
  - Required
  - 3-20 characters
  - Alphanumeric + underscore only
  - Must be unique (case-insensitive)
- `password`:
  - Required
  - Minimum 8 characters
  - Hash with bcrypt/argon2 before storing
- `email`:
  - Required
  - Valid email format
  - Must be unique (case-insensitive)
  - Used for account security/2FA only (NOT for login)

**Success Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-12-30T10:30:00Z"
  },
  "token": "jwt_token_here"
}
```

**Error Responses:**
```json
// 400 - Username taken
{
  "error": "Username already exists",
  "code": "USERNAME_TAKEN"
}

// 400 - Email taken
{
  "error": "Email already registered",
  "code": "EMAIL_TAKEN"
}

// 400 - Validation error
{
  "error": "Password must be at least 8 characters",
  "code": "INVALID_PASSWORD"
}
```

---

##### `POST /api/auth/login`

**Purpose:** Authenticate user and return session token

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "token": "jwt_token_here"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid username or password",
  "code": "INVALID_CREDENTIALS"
}
```

**Rate Limiting:** 5 attempts per 15 minutes per IP address

---

##### `POST /api/auth/logout`

**Purpose:** Invalidate user session

**Headers Required:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

##### `GET /api/auth/me`

**Purpose:** Get current authenticated user info

**Headers Required:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-12-30T10:30:00Z"
}
```

**Error Response (401):**
```json
{
  "error": "Not authenticated",
  "code": "UNAUTHORIZED"
}
```

---

### 2. Posts Management

#### Endpoints to Build

##### `GET /api/posts`

**Purpose:** Get paginated feed of posts

**Query Parameters:**
- `sort` (optional): `"hot"` | `"new"` | `"top"` (default: `"hot"`)
- `topic_id` (optional): UUID to filter by topic
- `limit` (optional): Number of posts (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Example Request:**
```
GET /api/posts?sort=hot&limit=20&offset=0
```

**Success Response (200):**
```json
{
  "posts": [
    {
      "id": "uuid",
      "title": "What's your favorite programming language?",
      "content": "I'm curious what everyone prefers and why...",
      "author": {
        "id": "uuid",
        "username": "john_doe"
      },
      "topic": {
        "id": "uuid",
        "name": "Technology"
      },
      "vote_count": 42,
      "user_vote": 1,
      "created_at": "2024-12-30T08:15:00Z",
      "updated_at": "2024-12-30T08:15:00Z"
    }
  ],
  "total": 150,
  "has_more": true
}
```

**Field Explanations:**
- `user_vote`: Only included if user is authenticated
  - `1` = user upvoted
  - `-1` = user downvoted
  - `0` or `null` = user hasn't voted
- `vote_count`: Net votes (upvotes - downvotes)
- `has_more`: Boolean indicating if more posts exist

**Sorting Algorithms:**

**Hot (Default):**
```
score = (upvotes - downvotes) / (hours_since_posted + 2)^1.5
```
Order by score DESC

**New:**
```
Order by created_at DESC
```

**Top:**
```
Order by vote_count DESC
```

---

##### `POST /api/posts`

**Purpose:** Create a new post

**Headers Required:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "topic_id": "uuid"
}
```

**Validation Rules:**
- `title`: Required, 5-300 characters
- `content`: Required, 10-10,000 characters
- `topic_id`: Required, must be valid topic UUID

**Success Response (201):**
```json
{
  "post": {
    "id": "uuid",
    "title": "What's your favorite programming language?",
    "content": "I'm curious what everyone prefers and why...",
    "author": {
      "id": "uuid",
      "username": "john_doe"
    },
    "topic": {
      "id": "uuid",
      "name": "Technology"
    },
    "vote_count": 0,
    "created_at": "2024-12-30T10:45:00Z",
    "updated_at": "2024-12-30T10:45:00Z"
  }
}
```

**Error Responses:**
```json
// 401 - Not authenticated
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED"
}

// 400 - Invalid topic
{
  "error": "Invalid topic ID",
  "code": "INVALID_TOPIC"
}

// 400 - Validation error
{
  "error": "Title must be between 5-300 characters",
  "code": "INVALID_TITLE"
}
```

**Rate Limiting:** 10 posts per hour per user

---

##### `GET /api/posts/:id`

**Purpose:** Get a single post by ID

**Success Response (200):**
```json
{
  "id": "uuid",
  "title": "What's your favorite programming language?",
  "content": "I'm curious what everyone prefers and why...",
  "author": {
    "id": "uuid",
    "username": "john_doe"
  },
  "topic": {
    "id": "uuid",
    "name": "Technology"
  },
  "vote_count": 42,
  "user_vote": 1,
  "created_at": "2024-12-30T08:15:00Z",
  "updated_at": "2024-12-30T08:15:00Z"
}
```

**Error Response (404):**
```json
{
  "error": "Post not found",
  "code": "POST_NOT_FOUND"
}
```

---

##### `PUT /api/posts/:id`

**Purpose:** Update a post (owner only)

**Headers Required:**
```
Authorization: Bearer <token>
```

**Request Body (all optional):**
```json
{
  "title": "string",
  "content": "string"
}
```

**Authorization:** Must be post owner

**Success Response (200):**
```json
{
  "post": {
    "id": "uuid",
    "title": "Updated title",
    "content": "Updated content",
    "author": {
      "id": "uuid",
      "username": "john_doe"
    },
    "topic": {
      "id": "uuid",
      "name": "Technology"
    },
    "vote_count": 42,
    "created_at": "2024-12-30T08:15:00Z",
    "updated_at": "2024-12-30T10:50:00Z"
  }
}
```

**Error Response (403):**
```json
{
  "error": "You don't have permission to edit this post",
  "code": "FORBIDDEN"
}
```

---

##### `DELETE /api/posts/:id`

**Purpose:** Delete a post (owner only)

**Headers Required:**
```
Authorization: Bearer <token>
```

**Authorization:** Must be post owner

**Success Response (200):**
```json
{
  "message": "Post deleted successfully"
}
```

**Error Response (403):**
```json
{
  "error": "You don't have permission to delete this post",
  "code": "FORBIDDEN"
}
```

---

### 3. Voting System

#### Endpoint to Build

##### `POST /api/posts/:id/vote`

**Purpose:** Upvote, downvote, or remove vote from a post

**Headers Required:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "vote": 1
}
```

**Vote Values:**
- `1` = Upvote
- `-1` = Downvote
- `0` = Remove vote (unvote)

**Business Logic:**
```
IF user has no existing vote:
  - Create new vote with value
  - Update post.vote_count (+1 or -1)

ELSE IF user has existing vote:
  IF new vote == existing vote:
    - Delete vote (toggle off)
    - Update post.vote_count (-1 or +1)
  ELSE IF new vote == 0:
    - Delete vote
    - Update post.vote_count (opposite of existing)
  ELSE:
    - Update vote to new value
    - Update post.vote_count (+2 or -2)
```

**Success Response (200):**
```json
{
  "vote_count": 43,
  "user_vote": 1
}
```

**Error Response (401):**
```json
{
  "error": "Authentication required to vote",
  "code": "UNAUTHORIZED"
}
```

**Rate Limiting:** 100 votes per hour per user

---

### 4. Topics/Threads

#### Endpoint to Build

##### `GET /api/topics`

**Purpose:** Get list of all available topics

**Success Response (200):**
```json
{
  "topics": [
    {
      "id": "uuid",
      "name": "General",
      "description": "General discussions about anything",
      "post_count": 1250,
      "created_at": "2024-12-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "name": "Technology",
      "description": "Discussions about tech, programming, and gadgets",
      "post_count": 450,
      "created_at": "2024-12-01T00:00:00Z"
    }
  ]
}
```

**Initial Topics to Seed in Database:**
```
1. General - General discussions about anything
2. Technology - Tech, programming, and gadgets
3. Gaming - Video games and gaming culture
4. Movies & TV - Film and television discussions
5. Sports - All sports discussions
6. Music - Music discussion and sharing
7. Books - Book recommendations and reviews
8. Food - Recipes, restaurants, and cooking
9. Travel - Travel stories and recommendations
10. Ask Community - Questions for the community
```

**Note:** "General" should be the default topic when none is selected

---

### 5. Search

#### Endpoint to Build

##### `GET /api/posts/search`

**Purpose:** Search posts by keywords

**Query Parameters:**
- `q` (required): Search query string
- `limit` (optional): Number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Example Request:**
```
GET /api/posts/search?q=javascript&limit=20&offset=0
```

**Search Logic:**
- Search in both `title` and `content` fields
- Case-insensitive
- Match partial words (e.g., "java" matches "javascript")
- Order by relevance (title matches ranked higher than content matches)
- Then order by vote_count DESC

**Success Response (200):**
```json
{
  "posts": [
    {
      "id": "uuid",
      "title": "JavaScript vs TypeScript",
      "content": "What are your thoughts on...",
      "author": {
        "id": "uuid",
        "username": "jane_doe"
      },
      "topic": {
        "id": "uuid",
        "name": "Technology"
      },
      "vote_count": 28,
      "created_at": "2024-12-29T14:20:00Z"
    }
  ],
  "total": 45,
  "has_more": true,
  "query": "javascript"
}
```

---

### 6. Reports

#### Endpoint to Build

##### `POST /api/posts/:id/report`

**Purpose:** Report a post for moderation

**Headers Required:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "reason": "spam",
  "details": "This post is clearly advertising a product"
}
```

**Reason Values (Enum):**
- `"spam"` - Spam or advertising
- `"harassment"` - Harassment or bullying
- `"inappropriate"` - Inappropriate content
- `"misinformation"` - False or misleading information
- `"other"` - Other reason (details required)

**Validation:**
- `reason`: Required, must be one of the enum values
- `details`: Optional, max 500 characters (required if reason is "other")

**Success Response (201):**
```json
{
  "message": "Report submitted successfully",
  "report_id": "uuid"
}
```

**Error Response (400):**
```json
{
  "error": "You have already reported this post",
  "code": "DUPLICATE_REPORT"
}
```

**Business Logic:**
- Users can only report each post once
- Store report in database with status "pending"
- Reports are for admin review (admin panel is post-MVP)

---

### 7. Security Requirements

#### Authentication

**JWT Tokens (Recommended):**
- Algorithm: HS256 or RS256
- Expiry: 7 days
- Include in header: `Authorization: Bearer <token>`
- Token payload should include:
```json
  {
    "user_id": "uuid",
    "username": "string",
    "iat": 1234567890,
    "exp": 1234567890
  }
```

**Session-Based Auth (Alternative):**
- Use secure HTTP-only cookies
- Session expiry: 7 days
- Store sessions in Redis or database

#### Password Security

- **Hash Algorithm:** bcrypt (cost factor: 10-12) or argon2
- **Never store plaintext passwords**
- **Never return password hashes in API responses**

#### Input Validation & Sanitization

**SQL Injection Prevention:**
- Use parameterized queries or ORM
- Never concatenate user input into SQL

**XSS Prevention:**
- Sanitize HTML tags from user input
- Escape special characters
- Strip `<script>` tags

**Validation:**
- Validate all string lengths
- Validate email format
- Validate UUID format
- Trim whitespace from strings

#### Rate Limiting

Implement rate limiting on these endpoints:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/auth/login` | 5 attempts | 15 minutes per IP |
| `/api/auth/register` | 3 accounts | 1 hour per IP |
| `/api/posts` (POST) | 10 posts | 1 hour per user |
| `/api/posts/:id/vote` | 100 votes | 1 hour per user |
| `/api/posts/:id/report` | 10 reports | 1 hour per user |

#### CORS Configuration

Allow requests from:
- `http://localhost:3000` (development)
- Your production frontend domain (when deployed)

---

### 8. Error Handling

**Standard Error Response Format:**
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

**HTTP Status Codes:**

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Not authenticated (no token or invalid token) |
| 403 | Forbidden | Authenticated but not authorized (e.g., editing someone else's post) |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side errors |

**Common Error Codes:**
```javascript
// Authentication
UNAUTHORIZED = "User not authenticated"
INVALID_CREDENTIALS = "Invalid username or password"
TOKEN_EXPIRED = "Authentication token expired"

// Validation
INVALID_INPUT = "Invalid input data"
INVALID_EMAIL = "Invalid email format"
INVALID_USERNAME = "Username must be 3-20 alphanumeric characters"
INVALID_PASSWORD = "Password must be at least 8 characters"

// Resources
NOT_FOUND = "Resource not found"
POST_NOT_FOUND = "Post not found"
USER_NOT_FOUND = "User not found"
TOPIC_NOT_FOUND = "Topic not found"

// Permissions
FORBIDDEN = "You don't have permission to perform this action"

// Duplicates
USERNAME_TAKEN = "Username already exists"
EMAIL_TAKEN = "Email already registered"
DUPLICATE_REPORT = "You have already reported this post"

// Rate Limiting
RATE_LIMIT_EXCEEDED = "Too many requests, please try again later"
```

---

## Database Schema

> **Backend Developer:** Here are all the tables you need to create

### Tables Overview
```
users
├── id (PK)
├── username
├── email
├── password_hash
└── created_at

topics
├── id (PK)
├── name
├── description
└── created_at

posts
├── id (PK)
├── user_id (FK → users)
├── topic_id (FK → topics)
├── title
├── content
├── vote_count
├── created_at
└── updated_at

votes
├── id (PK)
├── user_id (FK → users)
├── post_id (FK → posts)
└── vote_type

reports
├── id (PK)
├── reporter_id (FK → users)
├── post_id (FK → posts)
├── reason
├── details
├── status
└── created_at
```

---

### Detailed Schema

#### `users` Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Constraints
  CONSTRAINT username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 20),
  CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_]+$'),
  CONSTRAINT email_format CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$')
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Field Descriptions:**
- `id`: Unique identifier (UUID)
- `username`: Case-insensitive unique username
- `email`: Case-insensitive unique email
- `password_hash`: Hashed password (bcrypt/argon2)
- `created_at`: Account creation timestamp

---

#### `topics` Table
```sql
CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_topics_name ON topics(name);
```

**Seed Data (run on first setup):**
```sql
INSERT INTO topics (name, description) VALUES
  ('General', 'General discussions about anything'),
  ('Technology', 'Tech, programming, and gadgets'),
  ('Gaming', 'Video games and gaming culture'),
  ('Movies & TV', 'Film and television discussions'),
  ('Sports', 'All sports discussions'),
  ('Music', 'Music discussion and sharing'),
  ('Books', 'Book recommendations and reviews'),
  ('Food', 'Recipes, restaurants, and cooking'),
  ('Travel', 'Travel stories and recommendations'),
  ('Ask Community', 'Questions for the community');
```

---

#### `posts` Table
```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE SET NULL,
  title VARCHAR(300) NOT NULL,
  content TEXT NOT NULL,
  vote_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Constraints
  CONSTRAINT title_length CHECK (LENGTH(title) >= 5 AND LENGTH(title) <= 300),
  CONSTRAINT content_length CHECK (LENGTH(content) >= 10 AND LENGTH(content) <= 10000)
);

-- Indexes for performance (IMPORTANT!)
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_topic_id ON posts(topic_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_vote_count ON posts(vote_count DESC);
CREATE INDEX idx_posts_hot_score ON posts((vote_count / POWER(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at)) / 3600 + 2, 1.5)) DESC);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('english', title || ' ' || content));
```

**Field Descriptions:**
- `id`: Unique post identifier
- `user_id`: Author of the post
- `topic_id`: Topic/thread the post belongs to
- `title`: Post title (5-300 chars)
- `content`: Post body text (10-10,000 chars)
- `vote_count`: Net votes (upvotes - downvotes), cached for performance
- `created_at`: When post was created
- `updated_at`: When post was last edited

**Trigger for updated_at:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

#### `votes` Table
```sql
CREATE TABLE votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  vote_type INTEGER NOT NULL CHECK (vote_type IN (-1, 1)),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- User can only vote once per post
  CONSTRAINT unique_user_post_vote UNIQUE (user_id, post_id)
);

-- Indexes
CREATE INDEX idx_votes_post_id ON votes(post_id);
CREATE INDEX idx_votes_user_id ON votes(user_id);
```

**Field Descriptions:**
- `vote_type`: `1` for upvote, `-1` for downvote
- Constraint ensures one vote per user per post

**Trigger to update post.vote_count automatically:**
```sql
-- Function to update vote count
CREATE OR REPLACE FUNCTION update_post_vote_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE posts SET vote_count = vote_count + NEW.vote_type WHERE id = NEW.post_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE posts SET vote_count = vote_count - OLD.vote_type WHERE id = OLD.post_id;
  ELSIF TG_OP = 'UPDATE' THEN
    UPDATE posts SET vote_count = vote_count - OLD.vote_type + NEW.vote_type WHERE id = NEW.post_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER vote_insert AFTER INSERT ON votes
FOR EACH ROW EXECUTE FUNCTION update_post_vote_count();

CREATE TRIGGER vote_delete AFTER DELETE ON votes
FOR EACH ROW EXECUTE FUNCTION update_post_vote_count();

CREATE TRIGGER vote_update AFTER UPDATE ON votes
FOR EACH ROW EXECUTE FUNCTION update_post_vote_count();
```

---

#### `reports` Table
```sql
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  reason VARCHAR(50) NOT NULL CHECK (reason IN ('spam', 'harassment', 'inappropriate', 'misinformation', 'other')),
  details TEXT CHECK (LENGTH(details) <= 500),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'dismissed')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- User can only report each post once
  CONSTRAINT unique_user_post_report UNIQUE (reporter_id, post_id)
);

-- Indexes
CREATE INDEX idx_reports_post_id ON reports(post_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
```

**Field Descriptions:**
- `reporter_id`: User who submitted the report (nullable if user deleted)
- `post_id`: Post being reported
- `reason`: Reason category (enum)
- `details`: Additional context (optional, max 500 chars)
- `status`: Review status (pending/reviewed/dismissed)

---

### Database Relationships
```
users (1) ──< (many) posts
users (1) ──< (many) votes
users (1) ──< (many) reports

topics (1) ──< (many) posts

posts (1) ──< (many) votes
posts (1) ──< (many) reports
```

**Cascade Rules:**
- Delete user → Delete their posts, votes, and reports
- Delete post → Delete associated votes and reports
- Delete topic → Set posts.topic_id to NULL (or reassign to "General")

---

## Frontend Requirements

> **Frontend Developer:** This section is for you! Everything you need to build is documented here.

### Technology Stack

- **Framework:** Next.js 14+ (App Router or Pages Router)
- **Styling:** Tailwind CSS
- **State Management:** React Context, Zustand, or Redux (your choice)
- **API Calls:** Fetch API, Axios, or SWR/React Query (recommended)
- **Form Handling:** React Hook Form (recommended)
- **Routing:** Next.js built-in routing

---

### Project Structure (Suggested)
```suggested
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.jsx           # Home feed (/)
│   │   ├── login/
│   │   │   └── page.jsx       # Login page
│   │   ├── register/
│   │
│   └── page.jsx       # Register page
│   │   ├── create/
│   │   │   └── page.jsx       # Create post page
│   │   ├── post/
│   │   │   └── [id]/
│   │   │       └── page.jsx   # Single post view
│   │   └── search/
│   │       └── page.jsx       # Search results page
│   │
│   ├── components/             # Reusable components
│   │   ├── PostCard.jsx       # Individual post card
│   │   ├── PostFeed.jsx       # List of posts
│   │   ├── VoteButtons.jsx    # Upvote/downvote UI
│   │   ├── SortDropdown.jsx   # Hot/New/Top selector
│   │   ├── SearchBar.jsx      # Search input
│   │   ├── Navbar.jsx         # Navigation bar
│   │   ├── AuthForm.jsx       # Login/register form
│   │   ├── CreatePostForm.jsx # Post creation form
│   │   └── OptionsMenu.jsx    # Three-dot menu
│   │
│   ├── lib/
│   │   ├── api.js             # API helper functions
│   │   └── auth.js            # Auth utilities
│   │
│   ├── context/
│   │   └── AuthContext.jsx    # Global auth state
│   │
│   └── styles/
│       └── globals.css        # Global styles + Tailwind
│
├── package.json
└── tailwind.config.js
---
```

### Pages to Build

#### 1. Home Page (`/`)

**File:** `src/app/page.jsx`

**Purpose:** Main feed showing all posts

**What to display:**
- Navbar (with login/register or user menu)
- Sort dropdown (Hot/New/Top)
- Post feed (list of PostCard components)
- Infinite scroll or "Load More" button

**API Calls:**
```javascript
// On page load
GET /api/posts?sort=hot&limit=20&offset=0

// On sort change
GET /api/posts?sort=new&limit=20&offset=0

// On scroll/load more
GET /api/posts?sort=hot&limit=20&offset=20
```

**State to manage:**
- `posts` - Array of post objects
- `sort` - Current sort option ('hot', 'new', 'top')
- `loading` - Loading state
- `hasMore` - Whether more posts exist

---

#### 2. Login Page (`/login`)

**File:** `src/app/login/page.jsx`

**Purpose:** User login form

**Form fields:**
- Username (text input)
- Password (password input)
- Submit button

**API Call:**
```javascript
POST /api/auth/login
Body: { username, password }
```

**On success:**
1. Store token in localStorage or cookie
2. Update global auth context
3. Redirect to home page

**On error:**
- Display error message below form
- Clear password field

---

#### 3. Register Page (`/register`)

**File:** `src/app/register/page.jsx`

**Purpose:** User registration form

**Form fields:**
- Username (text input, 3-20 chars)
- Email (email input)
- Password (password input, min 8 chars)
- Confirm Password (password input)
- Submit button

**Validation (client-side):**
- Username: 3-20 chars, alphanumeric + underscore
- Email: Valid format
- Password: Minimum 8 characters
- Passwords match

**API Call:**
```javascript
POST /api/auth/register
Body: { username, email, password }
```

**On success:**
1. Store token
2. Update auth context
3. Redirect to home

---

#### 4. Create Post Page (`/create`)

**File:** `src/app/create/page.jsx`

**Purpose:** Form to create new post

**Auth required:** Yes (redirect to login if not authenticated)

**Form fields:**
- Title (text input, 5-300 chars)
- Content (textarea, 10-10,000 chars)
- Topic (dropdown select)
- Submit button

**API Calls:**
```javascript
// Load topics on mount
GET /api/topics

// Submit post
POST /api/posts
Body: { title, content, topic_id }
```

**On success:**
- Redirect to the new post page (`/post/[id]`)

---

#### 5. Single Post Page (`/post/[id]`)

**File:** `src/app/post/[id]/page.jsx`

**Purpose:** View a single post in detail

**What to display:**
- Full post card with all details
- Vote buttons
- Options menu (if owner)
- Comments section (placeholder for now - Phase 2)

**API Call:**
```javascript
GET /api/posts/:id
```

**Dynamic route:** Use Next.js dynamic routing with `[id]`

---

#### 6. Search Page (`/search`)

**File:** `src/app/search/page.jsx`

**Purpose:** Search results page

**What to display:**
- Search bar (pre-filled with query)
- Results count
- List of matching posts (PostCard components)

**API Call:**
```javascript
GET /api/posts/search?q=keyword&limit=20&offset=0
```

**URL structure:** `/search?q=javascript`

---

### Components to Build

#### 1. Navbar Component

**File:** `src/components/Navbar.jsx`

**Purpose:** Site navigation and user menu

**What to display:**

**If user NOT logged in:**
[Logo] Forum                    [Search] [Login] [Register]
**If user IS logged in:**
[Logo] Forum        [Search] [Create Post] [@username ▼]
└─ Profile
└─ Logout
**Features:**
- Logo/title links to home
- Search bar (navigates to `/search?q=...`)
- Login/Register buttons (if not authenticated)
- Create Post button (if authenticated)
- User dropdown menu (if authenticated)

---

#### 2. PostCard Component

**File:** `src/components/PostCard.jsx`

**Purpose:** Display individual post in card format

**Props:**
```javascript
{
  id: "uuid",
  title: "string",
  content: "string",
  author: { id, username },
  topic: { id, name },
  vote_count: number,
  user_vote: 1 | -1 | 0,
  created_at: "timestamp"
}
```

**Layout:**
┌─────────────────────────────────────────────────┐
│ 👤 username  •  Technology  •  2 hours ago      │  ⋮
├─────────────────────────────────────────────────┤
│                                                  │
│ What's your favorite programming language?      │ ← Title (bold, large)
│                                                  │
│ I'm curious what everyone prefers and why...    │ ← Content (preview)
│                                                  │
├─────────────────────────────────────────────────┤
│  ▲ 42 ▼                                         │ ← Vote buttons & count
└─────────────────────────────────────────────────┘
**Features:**
- Click anywhere on card → Navigate to `/post/[id]`
- Vote buttons:
  - Upvote arrow (highlighted if user_vote === 1)
  - Vote count in middle
  - Downvote arrow (highlighted if user_vote === -1)
  - Disabled if not authenticated
- Options menu (⋮):
  - Report (always visible)
  - Edit (if owner)
  - Delete (if owner)
- Time display: "2 hours ago", "3 days ago", etc.
- Content preview: Show first 200 characters + "..."

**States:**
- Default
- Hovered (slight shadow/lift)
- Upvoted (upvote arrow orange/colored)
- Downvoted (downvote arrow blue/colored)

---

#### 3. VoteButtons Component

**File:** `src/components/VoteButtons.jsx`

**Purpose:** Upvote/downvote interface

**Props:**
```javascript
{
  post_id: "uuid",
  vote_count: number,
  user_vote: 1 | -1 | 0 | null,
  onVoteChange: (newVoteCount, newUserVote) => void
}
```

**Layout:**
▲  (upvote arrow)
42 (vote count)
▼  (downvote arrow)
**Behavior:**
- If not authenticated: Show tooltip "Login to vote"
- On upvote click:
  - If user_vote === 1: Remove vote (toggle off) → API call with vote: 0
  - Else: Upvote → API call with vote: 1
- On downvote click:
  - If user_vote === -1: Remove vote → API call with vote: 0
  - Else: Downvote → API call with vote: -1

**API Call:**
```javascript
POST /api/posts/:id/vote
Body: { vote: 1 | -1 | 0 }
```

**On success:**
- Update local state immediately (optimistic update)
- Call `onVoteChange` callback to update parent

---

#### 4. SortDropdown Component

**File:** `src/components/SortDropdown.jsx`

**Purpose:** Let users sort feed

**Options:**
- Hot (default)
- New
- Top

**Props:**
```javascript
{
  currentSort: "hot" | "new" | "top",
  onSortChange: (newSort) => void
}
```

**UI:**
Sort by: [Hot ▼]
└─ Hot
└─ New
└─ Top
**Behavior:**
- On selection change, call `onSortChange(newSort)`
- Parent component refetches posts with new sort

---

#### 5. SearchBar Component

**File:** `src/components/SearchBar.jsx`

**Purpose:** Search input with debouncing

**Features:**
- Text input
- Search icon
- Debouncing (300ms delay before triggering search)
- Clear button (X) when text is entered

**Behavior:**
```javascript
// Pseudo-code
const [query, setQuery] = useState('');

// Debounce search
useEffect(() => {
  const timer = setTimeout(() => {
    if (query.length >= 2) {
      router.push(`/search?q=${query}`);
    }
  }, 300);
  
  return () => clearTimeout(timer);
}, [query]);
```

---

#### 6. PostFeed Component

**File:** `src/components/PostFeed.jsx`

**Purpose:** Display list of posts with infinite scroll

**Props:**
```javascript
{
  posts: Array<Post>,
  loading: boolean,
  hasMore: boolean,
  onLoadMore: () => void
}
```

**Features:**
- Map through `posts` and render `PostCard` for each
- Show loading spinner at bottom if `loading === true`
- Infinite scroll or "Load More" button
- Empty state if no posts: "No posts yet. Be the first to post!"

---

#### 7. OptionsMenu Component

**File:** `src/components/OptionsMenu.jsx`

**Purpose:** Three-dot menu on post cards

**Props:**
```javascript
{
  post_id: "uuid",
  is_owner: boolean,
  onEdit: () => void,
  onDelete: () => void
}
```

**Menu items:**
- Report (always visible)
- Edit (only if `is_owner === true`)
- Delete (only if `is_owner === true`)

**Behavior:**
- Click three-dot icon → Show dropdown menu
- Report: Open modal/dialog with report form
- Edit: Navigate to edit page or inline editing
- Delete: Show confirmation dialog → Call DELETE API

---

### State Management

**Global State (Auth Context):**
```javascript
// src/context/AuthContext.jsx
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in (check token)
    const token = localStorage.getItem('token');
    if (token) {
      // Fetch current user
      fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setUser(data))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

**Usage in components:**
```javascript
const { user, login, logout } = useAuth();

// Check if logged in
if (user) {
  // User is authenticated
}
```

---

### API Helper Functions

**File:** `src/lib/api.js`
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper to get auth token
function getToken() {
  return localStorage.getItem('token');
}

// Helper to build headers
function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

// GET request
export async function apiGet(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }
  
  return response.json();
}

// POST request
export async function apiPost(endpoint, data) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }
  
  return response.json();
}

// PUT request
export async function apiPut(endpoint, data) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }
  
  return response.json();
}

// DELETE request
export async function apiDelete(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }
  
  return response.json();
}
```

**Usage:**
```javascript
import { apiGet, apiPost } from '@/lib/api';

// Get posts
const data = await apiGet('/api/posts?sort=hot');

// Create post
const newPost = await apiPost('/api/posts', {
  title: 'My Post',
  content: 'Content here',
  topic_id: 'uuid'
});
```

---

### Design Guidelines

#### Color Scheme (Suggested)
```css
/* Light Mode */
--background: #ffffff
--card-bg: #f8f9fa
--text-primary: #1a1a1a
--text-secondary: #6c757d
--border: #dee2e6
--upvote: #ff4500      /* Reddit orange */
--downvote: #7193ff    /* Reddit blue */
--accent: #0066ff      /* Links, buttons */

/* Dark Mode (optional) */
--background: #1a1a1a
--card-bg: #2d2d2d
--text-primary: #ffffff
--text-secondary: #b0b0b0
--border: #404040
```

#### Typography
```css
/* Headings */
font-family: 'Inter', 'Helvetica Neue', sans-serif
h1: 32px, bold
h2: 24px, bold
h3: 20px, semibold

/* Body */
body: 16px, regular
small: 14px, regular

/* Post title */
18px, bold

/* Post content */
15px, regular
```

#### Spacing
```css
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px
```

#### Card Design
```css
.post-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

---

### Responsive Design

**Breakpoints:**
```css
/* Mobile */
@media (max-width: 640px) {
  /* Stack content vertically */
  /* Hide some secondary info */
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  /* 2-column layouts */
}

/* Desktop */
@media (min-width: 1025px) {
  /* 3-column layouts */
  /* Max content width: 1200px */
}
```

**Mobile-first approach:**
- Design for mobile first
- Enhance for larger screens
- Touch-friendly buttons (min 44x44px)

---

## API Contract

> **Both Frontend & Backend:** This is the contract between you

### Base URL

**Development:**
http://localhost:8000/api
**Production:**
https://your-domain.com/api
---

### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/auth/register` | No | Create new account |
| POST | `/auth/login` | No | Login user |
| POST | `/auth/logout` | Yes | Logout user |
| GET | `/auth/me` | Yes | Get current user |

---

### Post Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/posts` | No | Get paginated feed |
| POST | `/posts` | Yes | Create new post |
| GET | `/posts/:id` | No | Get single post |
| PUT | `/posts/:id` | Yes (owner) | Update post |
| DELETE | `/posts/:id` | Yes (owner) | Delete post |
| POST | `/posts/:id/vote` | Yes | Vote on post |
| POST | `/posts/:id/report` | Yes | Report post |
| GET | `/posts/search` | No | Search posts |

---

### Topic Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/topics` | No | Get all topics |

---

### Request/Response Examples

See detailed examples in the Backend Requirements section above.

---

## Development Workflow

### Step-by-Step Implementation Plan

#### Phase 1: Foundation (Week 1)

**Backend:**
- [ ] Set up project structure
- [ ] Configure database
- [ ] Create database schema and migrations
- [ ] Implement authentication endpoints (`/auth/register`, `/auth/login`)
- [ ] Test auth with Postman/Insomnia

**Frontend:**
- [ ] Set up Next.js project
- [ ] Configure Tailwind CSS
- [ ] Create AuthContext
- [ ] Build Login page
- [ ] Build Register page
- [ ] Test authentication flow

**Milestone:** Users can register and login

---

#### Phase 2: Posts CRUD (Week 2)

**Backend:**
- [ ] Implement `GET /posts` endpoint with sorting
- [ ] Implement `POST /posts` endpoint
- [ ] Implement `GET /posts/:id` endpoint
- [ ] Implement `PUT /posts/:id` endpoint
- [ ] Implement `DELETE /posts/:id` endpoint
- [ ] Seed topics in database

**Frontend:**
- [ ] Build PostCard component
- [ ] Build PostFeed component
- [ ] Build Home page with feed
- [ ] Build CreatePostForm component
- [ ] Build Create Post page
- [ ] Build Single Post page

**Milestone:** Users can create, view, edit, and delete posts

---

#### Phase 3: Voting & Sorting (Week 3)

**Backend:**
- [ ] Implement `POST /posts/:id/vote` endpoint
- [ ] Add vote triggers to update post.vote_count
- [ ] Optimize sorting queries (Hot/New/Top)

**Frontend:**
- [ ] Build VoteButtons component
- [ ] Integrate voting into PostCard
- [ ] Build SortDropdown component
- [ ] Add sort functionality to feed
- [ ] Implement optimistic UI updates

**Milestone:** Users can vote and sort posts

---

#### Phase 4: Search & Reports (Week 4)

**Backend:**
- [ ] Implement `GET /posts/search` endpoint
- [ ] Optimize search with full-text indexes
- [ ] Implement `POST /posts/:id/report` endpoint

**Frontend:**
- [ ] Build SearchBar component
- [ ] Build Search page
- [ ] Add debouncing to search
- [ ] Build OptionsMenu component
- [ ] Add report modal/dialog

**Milestone:** Users can search and report posts

---

#### Phase 5: Polish & Testing (Week 5)

**Backend:**
- [ ] Add rate limiting
- [ ] Add input validation
- [ ] Add error handling
- [ ] Write API documentation
- [ ] Test all endpoints

**Frontend:**
- [ ] Add loading states
- [ ] Add error messages
- [ ] Improve responsive design
- [ ] Add empty states
- [ ] Test all user flows

**Milestone:** MVP is complete and ready for deployment

---

### Git Workflow

**Branch Strategy:**
main (production-ready code)
├── develop (integration branch)
├── feature/auth
├── feature/posts
├── feature/voting
└── feature/search
**Workflow:**

1. Create feature branch from `develop`:
```bash
   git checkout develop
   git checkout -b feature/auth
```

2. Work on feature and commit:
```bash
   git add .
   git commit -m "feat: implement user registration"
```

3. Push and create Pull Request:
```bash
   git push origin feature/auth
```

4. Review and merge to `develop`

5. When ready, merge `develop` to `main`

**Commit Message Convention:**
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update dependencies
---

### Communication

**Daily Standups (async):**
- What did you work on yesterday?
- What will you work on today?
- Any blockers?

**Tools:**
- **Slack/Discord:** Daily communication
- **GitHub:** Code reviews, issues
- **Notion/Google Docs:** Documentation
- **Postman/Insomnia:** API testing

---

## Testing Checklist

### Backend Tests

#### Authentication
- [ ] User can register with valid credentials
- [ ] Registration fails with duplicate username
- [ ] Registration fails with duplicate email
- [ ] Registration fails with invalid password
- [ ] User can login with correct credentials
- [ ] Login fails with wrong password
- [ ] Login fails with non-existent username
- [ ] JWT token is generated on successful login
- [ ] Token expires after 7 days
- [ ] Protected routes require authentication

#### Posts
- [ ] Authenticated user can create post
- [ ] Unauthenticated user cannot create post
- [ ] Post requires valid topic_id
- [ ] Post title validates length (5-300 chars)
- [ ] Post content validates length (10-10,000 chars)
- [ ] User can only edit their own posts
- [ ] User can only delete their own posts
- [ ] Posts return correct author info
- [ ] Posts return correct topic info

#### Voting
- [ ] User can upvote post
- [ ] User can downvote post
- [ ] User can remove vote (toggle)
- [ ] User can change vote (up to down or vice versa)
- [ ] User cannot vote multiple times
- [ ] Vote count updates correctly
- [ ] Unauthenticated users cannot vote

#### Sorting
- [ ] Hot sort works correctly
- [ ] New sort returns newest posts first
- [ ] Top sort returns highest voted posts first
- [ ] Pagination works (limit & offset)

#### Search
- [ ] Search finds posts by title
- [ ] Search finds posts by content
- [ ] Search is case-insensitive
- [ ] Search returns no results for non-matching query
- [ ] Search pagination works

#### Reports
- [ ] User can report post
- [ ] User cannot report same post twice
- [ ] Report requires valid reason
- [ ] Report stores all required data

---

### Frontend Tests

#### Authentication
- [ ] Registration form validates input
- [ ] Registration shows error for duplicate username
- [ ] Registration redirects to home on success
- [ ] Login form validates input
- [ ] Login shows error for wrong credentials
- [ ] Login redirects to home on success
- [ ] Logout clears user session
- [ ] Protected routes redirect to login

#### Posts
- [ ] Home feed loads posts
- [ ] Post cards display all information correctly
- [ ] Clicking post card navigates to post page
- [ ] Create post form validates input
- [ ] Create post requires authentication
- [ ] Create post redirects to new post on success
- [ ] Edit button only shows for post owner
- [ ] Delete button only shows for post owner
- [ ] Delete shows confirmation dialog

#### Voting
- [ ] Upvote button works
- [ ] Downvote button works
- [ ] Vote count updates in real-time
- [ ] Vote buttons disabled for unauthenticated users
- [ ] Upvoted posts show highlighted upvote button
- [ ] Downvoted posts show highlighted downvote button

#### Sorting
- [ ] Sort dropdown changes feed
- [ ] Hot sort is default
- [ ] Changing sort refetches posts
- [ ] Sort persists on page navigation

#### Search
- [ ] Search bar has debouncing
- [ ] Search navigates to search page
- [ ] Search results display correctly
- [ ] Empty search shows message
- [ ] Clear button clears search input

#### UI/UX
- [ ] Loading spinners show during API calls
- [ ] Error messages display clearly
- [ ] Forms show validation errors
- [ ] Buttons have hover states
- [ ] Post cards have hover effects
- [ ] Responsive design works on mobile
- [ ] Responsive design works on tablet
- [ ] Responsive design works on desktop

---

## Future Enhancements

> **Note:** These features are NOT in the MVP. Add them after MVP is complete and working.

### Phase 2: Comments System

**Backend:**
- New `comments` table
- Nested comments (parent_id reference)
- Comment voting
- Comment CRUD endpoints

**Frontend:**
- Comments section on post page
- Nested comment threads (reddit-style)
- Comment forms
- Comment voting UI

---

### Phase 3: User Profiles

**Backend:**
- Update users table (add bio, avatar_url fields)
- User profile endpoint
- User post history endpoint
- Upload avatar (image storage)

**Frontend:**
- Profile page showing user info
- User's post history
- Edit profile form
- Avatar upload

---

### Phase 4: AI Features

**Backend:**
- Integrate AI API for topic detection
- Auto-categorize posts based on content
- Content moderation (detect spam, inappropriate content)

**Frontend:**
- Show AI-suggested topics when creating post
- Auto-fill topic based on content

---

### Phase 5: Recommendation Algorithm

**Backend:**
- Track user behavior (views, votes, time spent)
- Build recommendation model
- Personalized feed endpoint

**Frontend:**
- "For You" feed (personalized)
- "Popular" feed (trending across platform)
- Feed toggle between algorithmic and chronological

---

### Phase 6: Rich Media

**Backend:**
- Image upload (AWS S3, Cloudinary)
- Video upload
- Image/video processing
- CDN integration

**Frontend:**
- Image upload in post form
- Image display in posts
- Video player
- Image gallery

---

### Phase 7: Notifications

**Backend:**
- Notifications table
- Notification triggers (new comment, vote, mention)
- WebSocket or polling for real-time updates

**Frontend:**
- Notification bell icon
- Notification dropdown
- Mark as read functionality
- Real-time updates

---

### Phase 8: Advanced Moderation

**Backend:**
- Moderator roles
- Ban/mute users
- Approve/remove posts
- Moderation queue
- Moderation logs

**Frontend:**
- Moderator dashboard
- Moderation tools on posts
- User management interface
- Reports review interface

---

## Glossary

**Terms used in this document:**

- **MVP:** Minimum Viable Product - The simplest version with core features
- **JWT:** JSON Web Token - Token-based authentication method
- **CRUD:** Create, Read, Update, Delete - Basic database operations
- **UUID:** Universally Unique Identifier - Unique ID for database records
- **API:** Application Programming Interface - How frontend and backend communicate
- **Endpoint:** URL path that performs a specific action (e.g., `/api/posts`)
- **Rate Limiting:** Restricting number of requests to prevent abuse
- **Debouncing:** Delaying action until user stops typing
- **Optimistic Update:** Update UI before server confirms (then rollback if fails)
- **Pagination:** Breaking large result sets into pages
- **Seed Data:** Initial data added to database for testing/development

---

## Questions & Support

**If you're confused about anything:**

1. **Check this document first** - Most answers are here
2. **Ask your partner** - Discuss and clarify together
3. **Create a GitHub Issue** - Document questions for future reference
4. **Update this PRD** - Add clarifications as you learn

**Remember:** It's okay to not know everything. This is a learning project!

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-12-30 | Initial PRD created | Team |

---

**Ready to start building? Let's go! 🚀**