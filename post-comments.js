/**
 * Reads the reCAPTCHA v3 site key from the <script> tag URL at runtime.
 * The build inlines the key into the src attribute; this avoids duplicating
 * it as a hardcoded string inside this file.
 *
 *   <script src="https://www.google.com/recaptcha/api.js?render=SITE_KEY">
 */
function getRecaptchaSiteKey() {
  const el = document.querySelector('script[src*="recaptcha/api.js"]');
  if (!el) return null;
  const match = el.src.match(/[?&]render=([^&]+)/);
  return match ? match[1] : null;
}

/**
 * <post-comments post="slug"> Web Component
 *
 * Renders a comments thread for a blog post using Firebase Auth (GitHub + Google)
 * and Firestore for storage. Handles sign-in, comment submission, real-time updates,
 * and light/dark theming.
 *
 * Usage in template:
 *   <post-comments post="{{SLUG}}"></post-comments>
 *
 * Requires: Firebase SDK loaded globally, firebase-config.json parsed into window.firebaseConfig
 */

/**
 * <subscribe-form> Web Component
 *
 * Renders an email subscription form that stores emails in Firestore.
 * Handles double-opt-in (confirmation email via Cloud Function).
 * Light/dark theme-aware.
 *
 * Usage in template:
 *   <subscribe-form></subscribe-form>
 *
 * Requires: Firebase SDK loaded globally, Firestore rules allowing email writes
 */

class PostComments extends HTMLElement {
  constructor() {
    super();
    this.post = null;
    this.user = null;
    this.comments = [];
    this.unsubscribe = null;
    this.isLoadingAuth = true;

    // Likes data
    this.postLikesData = { count: 0, userLiked: false };  // Post likes
    this.commentLikes = {};  // Map of commentId -> { count, userLiked }
    this.unsubscribes = [];  // Track top-level listeners (comments, post likes, thread) for cleanup
    this.commentLikeUnsubs = {};  // Map of commentId -> unsubscribe fn for per-comment like listeners
  }

  async connectedCallback() {
    // Read the attribute here (guaranteed available in connectedCallback)
    this.post = this.getAttribute('post');
    if (!this.post) {
      console.error('post-comments: missing "post" attribute');
      return;
    }

    // Inject styles
    this.injectStyles();

    // Render shell
    this.render();

    // Wait for firebase-config.json loader (in template) to finish initializing
    // window.firebaseAuth and window.firebaseDb before proceeding.
    await this.waitForFirebase();

    // Listen to auth state changes (fires once on load, even when signed out).
    // render() rebinds listeners itself, so no explicit attach needed here.
    window.firebaseAuth.onAuthStateChanged((user) => {
      this.user = user;
      this.isLoadingAuth = false;
      this.render();
    });

    // Listen to comments in real-time
    this.listenToComments();

    // Listen to post likes and comment likes in real-time
    this.listenToPostLikes();
    this.listenToCommentLikes();
  }

  async waitForFirebase() {
    return new Promise((resolve) => {
      const check = () => {
        if (window.firebaseAuth && window.firebaseDb) {
          resolve();
        } else {
          setTimeout(check, 50);
        }
      };
      check();
    });
  }

  listenToComments() {
    if (!window.firebaseDb) return;

    const commentsRef = window.firebaseDb
      .collection('comments')
      .doc(this.post)
      .collection('thread')
      .orderBy('createdAt', 'asc');

    this.unsubscribe = commentsRef.onSnapshot((snapshot) => {
      this.comments = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      this.render();
    }, (error) => {
      console.error('Error listening to comments:', error);
    });
  }

  listenToPostLikes() {
    if (!window.firebaseDb) return;

    const likesRef = window.firebaseDb
      .collection('posts')
      .doc(this.post)
      .collection('likes');

    const unsubscribe = likesRef.onSnapshot((snapshot) => {
      this.postLikesData.count = snapshot.size;
      this.postLikesData.userLiked = this.user
        ? snapshot.docs.some(doc => doc.id === this.user.uid)
        : false;
      this.render();
    }, (error) => {
      console.error('Error listening to post likes:', error);
    });

    this.unsubscribes.push(unsubscribe);
  }

  listenToCommentLikes() {
    if (!window.firebaseDb) return;

    const threadRef = window.firebaseDb
      .collection('comments')
      .doc(this.post)
      .collection('thread');

    // For each comment, listen to its likes subcollection. Rather than tearing
    // down and rebuilding every per-comment listener on each thread change
    // (which leaks listeners), we reconcile: subscribe only to newly added
    // comments and unsubscribe from removed ones. commentLikeUnsubs holds the
    // live listener per commentId so we never double-subscribe or orphan one.
    const unsubscribe = threadRef.onSnapshot((snapshot) => {
      const currentIds = new Set(snapshot.docs.map(d => d.id));

      // Drop listeners (and cached data) for comments that no longer exist.
      Object.keys(this.commentLikeUnsubs).forEach((commentId) => {
        if (!currentIds.has(commentId)) {
          this.commentLikeUnsubs[commentId]();
          delete this.commentLikeUnsubs[commentId];
          delete this.commentLikes[commentId];
        }
      });

      // Add listeners for comments we're not already watching.
      snapshot.docs.forEach((commentDoc) => {
        const commentId = commentDoc.id;
        if (this.commentLikeUnsubs[commentId]) return;  // already subscribed

        const likesRef = threadRef.doc(commentId).collection('likes');
        this.commentLikeUnsubs[commentId] = likesRef.onSnapshot((likesSnapshot) => {
          this.commentLikes[commentId] = {
            count: likesSnapshot.size,
            userLiked: this.user
              ? likesSnapshot.docs.some(doc => doc.id === this.user.uid)
              : false
          };
          this.render();
        }, (error) => {
          console.error('Error listening to comment likes:', error);
        });
      });

      this.render();
    }, (error) => {
      console.error('Error listening to thread for likes:', error);
    });

    this.unsubscribes.push(unsubscribe);
  }

  async handleLikePost() {
    if (!this.user) {
      alert('Please sign in to like posts');
      return;
    }

    try {
      // Get reCAPTCHA token for bot protection (invisible)
      const recaptchaSiteKey = getRecaptchaSiteKey();
      const recaptchaToken = (window.grecaptcha && recaptchaSiteKey)
        ? await grecaptcha.execute(recaptchaSiteKey, {action: 'like'})
        : null;

      const likeRef = window.firebaseDb
        .collection('posts')
        .doc(this.post)
        .collection('likes')
        .doc(this.user.uid);

      if (this.postLikesData.userLiked) {
        // Unlike
        await likeRef.delete();
      } else {
        // Like - include reCAPTCHA token for abuse detection
        await likeRef.set({
          userId: this.user.uid,
          createdAt: firebase.firestore.FieldValue.serverTimestamp(),
          recaptchaToken: recaptchaToken  // For future server-side verification
        });
      }
    } catch (error) {
      console.error('Error toggling post like:', error);
      alert('Failed to toggle like: ' + error.message);
    }
  }

  async handleLikeComment(commentId) {
    if (!this.user) {
      alert('Please sign in to like comments');
      return;
    }

    try {
      // Get reCAPTCHA token for bot protection (invisible)
      const recaptchaSiteKey = getRecaptchaSiteKey();
      const recaptchaToken = (window.grecaptcha && recaptchaSiteKey)
        ? await grecaptcha.execute(recaptchaSiteKey, {action: 'like'})
        : null;

      const likeRef = window.firebaseDb
        .collection('comments')
        .doc(this.post)
        .collection('thread')
        .doc(commentId)
        .collection('likes')
        .doc(this.user.uid);

      const likeData = this.commentLikes[commentId];
      if (likeData && likeData.userLiked) {
        // Unlike
        await likeRef.delete();
      } else {
        // Like - include reCAPTCHA token for abuse detection
        await likeRef.set({
          userId: this.user.uid,
          createdAt: firebase.firestore.FieldValue.serverTimestamp(),
          recaptchaToken: recaptchaToken  // For future server-side verification
        });
      }
    } catch (error) {
      console.error('Error toggling comment like:', error);
      alert('Failed to toggle like: ' + error.message);
    }
  }

  async handleSignIn(provider) {
    try {
      if (provider === 'github') {
        const githubProvider = new firebase.auth.GithubAuthProvider();
        await window.firebaseAuth.signInWithPopup(githubProvider);
      } else if (provider === 'google') {
        const googleProvider = new firebase.auth.GoogleAuthProvider();
        await window.firebaseAuth.signInWithPopup(googleProvider);
      }
    } catch (error) {
      console.error('Sign-in error:', error);
      alert('Failed to sign in: ' + error.message);
    }
  }

  async handleSignOut() {
    try {
      await window.firebaseAuth.signOut();
    } catch (error) {
      console.error('Sign-out error:', error);
    }
  }

  async handleSubmitComment(e) {
    e.preventDefault();
    if (!this.user) {
      alert('Please sign in to comment');
      return;
    }

    const textarea = this.querySelector('textarea[name="body"]');
    const body = textarea?.value?.trim();

    if (!body) {
      alert('Comment cannot be empty');
      return;
    }

    const submitBtn = this.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Posting...';

    try {
      await window.firebaseDb
        .collection('comments')
        .doc(this.post)
        .collection('thread')
        .add({
          author: this.user.displayName || this.user.email || 'Anonymous',
          uid: this.user.uid,
          photo: this.user.photoURL || '',
          body: body,  // Stored raw; escaped on render (escapeHtml) so out-of-band writes are safe too
          createdAt: firebase.firestore.FieldValue.serverTimestamp(),
          approved: true, // Auto-approve for now; implement moderation later
          provider: this.user.providerData[0]?.providerId || 'unknown'
        });

      textarea.value = '';
      this.render();
    } catch (error) {
      console.error('Error posting comment:', error);
      alert('Failed to post comment: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Post Comment';
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Escape a value destined for a double-quoted HTML attribute. textContent
  // doesn't escape quotes, so a crafted photo URL could break out of src="...".
  escapeAttr(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }

  injectStyles() {
    if (document.getElementById('post-comments-styles')) return;

    const style = document.createElement('style');
    style.id = 'post-comments-styles';
    style.textContent = `
      post-comments {
        display: block;
        margin: 2rem 0;
      }

      .comments-section {
        border-top: 1px solid var(--border-color, #e0e0e0);
        padding-top: 2rem;
      }

      [data-theme="dark"] .comments-section {
        border-top-color: #333;
      }

      .comments-section h2 {
        font-size: 1.5rem;
        margin: 0 0 1.5rem 0;
        font-family: "Source Serif 4", serif;
        font-weight: 600;
      }

      .comments-auth {
        background: var(--bg-secondary, #f5f5f5);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
      }

      [data-theme="dark"] .comments-auth {
        background-color: #2a2a2a;
      }

      .comments-auth p {
        margin: 0 0 0.75rem 0;
        font-size: 0.95rem;
        color: var(--text-secondary, #666);
      }

      [data-theme="dark"] .comments-auth p {
        color: #aaa;
      }

      .comments-auth-buttons {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
      }

      .comments-auth-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: white;
        border: 1px solid #ddd;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
      }

      [data-theme="dark"] .comments-auth-btn {
        background-color: #333;
        border-color: #555;
      }

      .comments-auth-btn:hover {
        background-color: #f0f0f0;
        border-color: #999;
      }

      [data-theme="dark"] .comments-auth-btn:hover {
        background-color: #444;
        border-color: #666;
      }

      .comments-user-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: var(--bg-secondary, #f5f5f5);
        border-radius: 6px;
      }

      [data-theme="dark"] .comments-user-info {
        background-color: #2a2a2a;
      }

      .comments-user-info-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
      }

      .comments-user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #ddd;
        object-fit: cover;
      }

      .comments-user-name {
        font-weight: 500;
        font-size: 0.95rem;
      }

      .comments-signout-btn {
        padding: 0.4rem 0.8rem;
        background: transparent;
        border: 1px solid #ccc;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: all 0.2s;
      }

      [data-theme="dark"] .comments-signout-btn {
        border-color: #666;
      }

      .comments-signout-btn:hover {
        background: #f0f0f0;
      }

      [data-theme="dark"] .comments-signout-btn:hover {
        background: #333;
      }

      .comments-form {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-bottom: 2rem;
      }

      .comments-textarea {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-family: inherit;
        font-size: 0.95rem;
        resize: vertical;
        min-height: 100px;
        background: white;
        color: black;
      }

      [data-theme="dark"] .comments-textarea {
        background-color: #2a2a2a;
        border-color: #555;
        color: #fff;
      }

      .comments-textarea:focus {
        outline: none;
        border-color: #0066cc;
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
      }

      .comments-form-buttons {
        display: flex;
        gap: 0.5rem;
      }

      .comments-submit-btn {
        padding: 0.6rem 1.2rem;
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
        transition: background 0.2s;
      }

      .comments-submit-btn:hover {
        background: #0052a3;
      }

      .comments-submit-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
      }

      .comments-list {
        list-style: none;
        padding: 0;
        margin: 0;
      }

      .comments-item {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: var(--bg-secondary, #f9f9f9);
        border-radius: 8px;
        border-left: 3px solid #0066cc;
      }

      [data-theme="dark"] .comments-item {
        background-color: #2a2a2a;
      }

      .comments-item-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
      }

      .comments-item-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #ddd;
        object-fit: cover;
      }

      .comments-item-meta {
        flex: 1;
      }

      .comments-item-author {
        font-weight: 600;
        font-size: 0.95rem;
      }

      .comments-item-date {
        font-size: 0.8rem;
        color: var(--text-secondary, #666);
      }

      [data-theme="dark"] .comments-item-date {
        color: #aaa;
      }

      .comments-item-body {
        color: var(--text-color, #333);
        font-size: 0.95rem;
        line-height: 1.5;
        word-break: break-word;
      }

      [data-theme="dark"] .comments-item-body {
        color: #e0e0e0;
      }

      .comments-empty {
        padding: 2rem 1rem;
        text-align: center;
        color: var(--text-secondary, #666);
        font-style: italic;
      }

      [data-theme="dark"] .comments-empty {
        color: #aaa;
      }

      .comments-loading {
        padding: 1rem;
        text-align: center;
        color: var(--text-secondary, #666);
      }

      [data-theme="dark"] .comments-loading {
        color: #aaa;
      }

      .post-likes-section {
        margin: 1.5rem 0;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-color, #e0e0e0);
      }

      [data-theme="dark"] .post-likes-section {
        border-bottom-color: #333;
      }

      .like-btn, .comment-like-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.4rem 0.9rem;
        background: transparent;
        border: 1px solid var(--border-color, #ddd);
        border-radius: 20px;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
        color: var(--text, #333);
      }

      [data-theme="dark"] .like-btn, [data-theme="dark"] .comment-like-btn {
        border-color: #555;
        color: #ddd;
      }

      .like-btn:hover, .comment-like-btn:hover {
        background-color: rgba(255, 100, 100, 0.08);
        border-color: #ff6b6b;
      }

      [data-theme="dark"] .like-btn:hover, [data-theme="dark"] .comment-like-btn:hover {
        background-color: rgba(255, 100, 100, 0.15);
        border-color: #ff8787;
      }

      .like-btn[data-liked="true"], .comment-like-btn[data-liked="true"] {
        color: #ff4d4d;
        border-color: #ff4d4d;
        background-color: rgba(255, 77, 77, 0.08);
      }

      [data-theme="dark"] .like-btn[data-liked="true"], [data-theme="dark"] .comment-like-btn[data-liked="true"] {
        color: #ff8787;
        border-color: #ff8787;
        background-color: rgba(255, 135, 135, 0.15);
      }

      .like-btn:disabled, .comment-like-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .comments-item-actions {
        margin-top: 0.75rem;
        display: flex;
        gap: 0.5rem;
      }
    `;
    document.head.appendChild(style);
  }

  render() {
    let html = '<section class="comments-section">';
    html += '<h2>Comments</h2>';

    // Anonymous auth exists only to let visitors like without signing in.
    // Commenting requires a real identity (GitHub/Google), so treat an
    // anonymous session the same as signed-out for the comment form.
    const canComment = this.user && !this.user.isAnonymous;

    if (this.isLoadingAuth) {
      html += '<div class="comments-loading">Loading...</div>';
    } else if (!canComment) {
      html += `
        <div class="comments-auth">
          <p>Sign in to post a comment:</p>
          <div class="comments-auth-buttons">
            <button class="comments-auth-btn comments-github-btn" data-provider="github">
              Sign in with GitHub
            </button>
            <button class="comments-auth-btn comments-google-btn" data-provider="google">
              Sign in with Google
            </button>
          </div>
        </div>
      `;
    } else {
      html += `
        <div class="comments-user-info">
          <div class="comments-user-info-left">
            ${this.user.photoURL ? `<img src="${this.escapeAttr(this.user.photoURL)}" alt="${this.escapeAttr(this.user.displayName)}" class="comments-user-avatar">` : '<div class="comments-user-avatar"></div>'}
            <span class="comments-user-name">${this.escapeHtml(this.user.displayName || this.user.email)}</span>
          </div>
          <button class="comments-signout-btn">Sign out</button>
        </div>
        <form class="comments-form">
          <textarea name="body" placeholder="Share your thoughts..."></textarea>
          <div class="comments-form-buttons">
            <button type="submit" class="comments-submit-btn">Post Comment</button>
          </div>
        </form>
      `;
    }

    // Post like button (show even without auth - anonymous users can like)
    html += `
      <div class="post-likes-section">
        <button class="like-btn" data-liked="${this.postLikesData.userLiked}">
          ${this.postLikesData.userLiked ? '❤️' : '🤍'} ${this.postLikesData.count} ${this.postLikesData.count === 1 ? 'like' : 'likes'}
        </button>
      </div>
    `;

    if (this.comments.length > 0) {
      html += '<ul class="comments-list">';
      this.comments.forEach(comment => {
        const date = comment.createdAt?.toDate?.();
        const dateStr = date ? this.formatDate(date) : 'Just now';
        const commentLikeData = this.commentLikes[comment.id] || { count: 0, userLiked: false };
        html += `
          <li class="comments-item">
            <div class="comments-item-header">
              ${comment.photo ? `<img src="${this.escapeAttr(comment.photo)}" alt="${this.escapeAttr(comment.author)}" class="comments-item-avatar">` : '<div class="comments-item-avatar"></div>'}
              <div class="comments-item-meta">
                <div class="comments-item-author">${this.escapeHtml(comment.author)}</div>
                <div class="comments-item-date">${dateStr}</div>
              </div>
            </div>
            <div class="comments-item-body">${this.escapeHtml(comment.body)}</div>
            <div class="comments-item-actions">
              <button class="comment-like-btn" data-comment-id="${comment.id}" data-liked="${commentLikeData.userLiked}">
                ${commentLikeData.userLiked ? '❤️' : '🤍'} ${commentLikeData.count}
              </button>
            </div>
          </li>
        `;
      });
      html += '</ul>';
    } else if (!this.isLoadingAuth) {
      html += '<div class="comments-empty">No comments yet. Be the first to share your thoughts!</div>';
    }

    html += '</section>';
    this.innerHTML = html;

    // Re-bind listeners: render() replaces all DOM nodes, so any prior
    // listeners are gone. Binding here guarantees handlers are always live,
    // no matter which caller triggered the render (auth change, snapshot, submit).
    this.attachEventListeners();
  }

  formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
  }

  attachEventListeners() {
    const githubBtn = this.querySelector('.comments-github-btn');
    if (githubBtn) {
      githubBtn.addEventListener('click', () => this.handleSignIn('github'));
    }

    const googleBtn = this.querySelector('.comments-google-btn');
    if (googleBtn) {
      googleBtn.addEventListener('click', () => this.handleSignIn('google'));
    }

    const signoutBtn = this.querySelector('.comments-signout-btn');
    if (signoutBtn) {
      signoutBtn.addEventListener('click', () => this.handleSignOut());
    }

    const form = this.querySelector('.comments-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmitComment(e));
    }

    // Post like button
    const postLikeBtn = this.querySelector('.like-btn');
    if (postLikeBtn) {
      postLikeBtn.addEventListener('click', () => this.handleLikePost());
    }

    // Comment like buttons
    const commentLikeBtns = this.querySelectorAll('.comment-like-btn');
    commentLikeBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const commentId = btn.getAttribute('data-comment-id');
        this.handleLikeComment(commentId);
      });
    });
  }

  disconnectedCallback() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    // Clean up top-level listeners (post likes, thread-for-likes)
    this.unsubscribes.forEach(unsub => unsub());
    this.unsubscribes = [];
    // Clean up per-comment like listeners
    Object.values(this.commentLikeUnsubs).forEach(unsub => unsub());
    this.commentLikeUnsubs = {};
  }
}

customElements.define('post-comments', PostComments);

// ═══════════════════════════════════════════════════════════════════════════
// SUBSCRIBE FORM WEB COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class SubscribeForm extends HTMLElement {
  constructor() {
    super();
    this.isSubmitting = false;
  }

  async connectedCallback() {
    this.injectStyles();
    this.render();

    // Wait for Firebase to be available
    await this.waitForFirebase();

    this.attachEventListeners();
  }

  async waitForFirebase() {
    return new Promise((resolve) => {
      const check = () => {
        if (window.firebaseDb) {
          resolve();
        } else {
          setTimeout(check, 50);
        }
      };
      check();
    });
  }

  async handleSubscribe(e) {
    e.preventDefault();
    if (this.isSubmitting) return;

    const input = this.querySelector('input[type="email"]');
    const email = input?.value?.trim();

    if (!email) {
      alert('Please enter your email');
      return;
    }

    this.isSubmitting = true;
    const submitBtn = this.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Subscribing...';

    try {
      // Use the email (base64-encoded) as the document ID so Firestore naturally
      // prevents duplicates: a second submission hits 'update' (blocked by rules)
      // and we catch the permission-denied to show a friendly message.
      const docId = btoa(email).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');

      await window.firebaseDb
        .collection('subscribers')
        .doc(docId)
        .set({
          email: email,
          subscribedAt: firebase.firestore.FieldValue.serverTimestamp(),
          confirmed: false,
          confirmationToken: this.generateToken(),
          tags: ['blog'],
          source: 'website'
        });

      // Clear input and show success
      input.value = '';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Subscribed!';

      // Reset button after 3 seconds
      setTimeout(() => {
        submitBtn.textContent = 'Subscribe';
        submitBtn.disabled = false;
      }, 3000);

      alert('Thanks for subscribing! Check your email to confirm.');
    } catch (error) {
      if (error.code === 'permission-denied') {
        // update is blocked by rules → doc already exists → already subscribed
        alert('This email is already subscribed!');
      } else {
        console.error('Subscribe error:', error);
        alert('Failed to subscribe: ' + error.message);
      }
      submitBtn.disabled = false;
      submitBtn.textContent = 'Subscribe';
    } finally {
      this.isSubmitting = false;
    }
  }

  generateToken() {
    // Generate a random token for email confirmation link
    return Math.random().toString(36).substring(2, 15) +
           Math.random().toString(36).substring(2, 15);
  }

  injectStyles() {
    if (document.getElementById('subscribe-form-styles')) return;

    const style = document.createElement('style');
    style.id = 'subscribe-form-styles';
    style.textContent = `
      subscribe-form {
        display: block;
        margin-top: 20px;
        padding-top: 18px;
        border-top: 1px solid var(--border-color, #e0e0e0);
      }

      [data-theme="dark"] subscribe-form {
        border-top-color: #333;
      }

      .subscribe-form-wrap {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
      }

      .subscribe-form-wrap input {
        flex: 1;
        min-width: 200px;
        padding: 9px 14px;
        border: 1px solid var(--border, #ddd);
        border-radius: 6px;
        background: var(--bg, white);
        color: var(--ink, #333);
        font-family: var(--sans, sans-serif);
        font-size: 14px;
        transition: border-color 0.2s;
      }

      [data-theme="dark"] .subscribe-form-wrap input {
        background-color: #2a2a2a;
        border-color: #555;
        color: #fff;
      }

      .subscribe-form-wrap input:focus {
        outline: none;
        border-color: var(--accent, #0066cc);
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
      }

      [data-theme="dark"] .subscribe-form-wrap input::placeholder {
        color: #aaa;
      }

      .subscribe-form-wrap button {
        padding: 9px 18px;
        background: var(--accent, #0066cc);
        color: var(--on-accent, white);
        border: none;
        border-radius: 100px;
        font-family: var(--sans, sans-serif);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
        white-space: nowrap;
      }

      .subscribe-form-wrap button:hover:not(:disabled) {
        background: var(--accent-hover, #0052a3);
      }

      .subscribe-form-wrap button:disabled {
        background: #ccc;
        cursor: not-allowed;
      }

      [data-theme="dark"] .subscribe-form-wrap button {
        background: var(--accent, #8B83E8);
      }

      [data-theme="dark"] .subscribe-form-wrap button:hover:not(:disabled) {
        background: var(--accent-hover, #b6aef7);
      }

      @media (max-width: 560px) {
        .subscribe-form-wrap {
          flex-direction: column;
          align-items: stretch;
        }
        .subscribe-form-wrap input {
          min-width: unset;
        }
      }
    `;
    document.head.appendChild(style);
  }

  render() {
    this.innerHTML = `
      <form class="subscribe-form-wrap">
        <input type="email" placeholder="Email address" required aria-label="Subscribe to newsletter">
        <button type="submit">Subscribe</button>
      </form>
    `;
  }

  attachEventListeners() {
    const form = this.querySelector('.subscribe-form-wrap');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubscribe(e));
    }
  }
}

customElements.define('subscribe-form', SubscribeForm);

// ═══════════════════════════════════════════════════════════════════════════
// SUBSCRIBE POPUP WEB COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

/**
 * <subscribe-popup> Web Component
 *
 * Renders a scroll-triggered modal popup for email subscription. Appears once
 * the user has scrolled 60% down the page. Includes a close button and
 * localStorage tracking to not annoy repeat visitors.
 *
 * Usage in template:
 *   <subscribe-popup></subscribe-popup>
 *
 * Requires: Firebase SDK loaded globally, Firestore rules allowing email writes
 */

class SubscribePopup extends HTMLElement {
  constructor() {
    super();
    this.isSubmitting = false;
    this.hasShown = false;
    this.scrollListener = null;
  }

  async connectedCallback() {
    this.injectStyles();
    this.render();

    // Wait for Firebase to be available
    await this.waitForFirebase();

    // Set up scroll listener to show popup at 60% scroll depth
    this.setupScrollListener();
    this.attachEventListeners();
  }

  async waitForFirebase() {
    return new Promise((resolve) => {
      const check = () => {
        if (window.firebaseDb) {
          resolve();
        } else {
          setTimeout(check, 50);
        }
      };
      check();
    });
  }

  setupScrollListener() {
    // Don't show the popup if user has dismissed it recently (24 hours)
    const lastDismissed = localStorage.getItem('subscribe-popup-dismissed');
    const now = Date.now();
    const dayInMs = 24 * 60 * 60 * 1000;

    if (lastDismissed && now - parseInt(lastDismissed) < dayInMs) {
      return;  // Don't show; user dismissed recently
    }

    this.scrollListener = () => {
      if (this.hasShown) return;

      const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      if (scrollPercent >= 60) {
        this.showPopup();
        this.hasShown = true;
      }
    };

    window.addEventListener('scroll', this.scrollListener);
  }

  showPopup() {
    const modal = this.querySelector('.subscribe-popup-modal');
    if (modal) {
      modal.style.display = 'flex';
    }
    // Emit GTM event
    if (window.gtag) {
      gtag('event', 'subscribe_popup_shown', {
        event_category: 'engagement',
        event_label: 'popup_modal'
      });
    }
  }

  hidePopup() {
    const modal = this.querySelector('.subscribe-popup-modal');
    if (modal) {
      modal.style.display = 'none';
    }
    // Record dismissal
    localStorage.setItem('subscribe-popup-dismissed', Date.now().toString());
    // Remove scroll listener to save cycles
    if (this.scrollListener) {
      window.removeEventListener('scroll', this.scrollListener);
    }
    // Emit GTM event
    if (window.gtag) {
      gtag('event', 'subscribe_popup_dismissed', {
        event_category: 'engagement',
        event_label: 'popup_modal'
      });
    }
  }

  async handleSubscribe(e) {
    e.preventDefault();
    if (this.isSubmitting) return;

    const input = this.querySelector('.subscribe-popup-input');
    const email = input?.value?.trim();

    if (!email) {
      this.showMessage('Please enter your email', 'error');
      return;
    }

    this.isSubmitting = true;
    const submitBtn = this.querySelector('.subscribe-popup-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Subscribing...';

    try {
      const docId = btoa(email).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');

      await window.firebaseDb
        .collection('subscribers')
        .doc(docId)
        .set({
          email: email,
          subscribedAt: firebase.firestore.FieldValue.serverTimestamp(),
          confirmed: false,
          confirmationToken: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
        });

      input.value = '';
      submitBtn.textContent = 'Confirmed! Check your email';
      submitBtn.disabled = false;
      this.isSubmitting = false;

      // Emit GTM event
      if (window.gtag) {
        gtag('event', 'subscribe_popup_success', {
          event_category: 'engagement',
          event_label: 'popup_modal'
        });
      }

      // Auto-close after success
      setTimeout(() => this.hidePopup(), 2000);
    } catch (error) {
      let errorType = 'unknown';
      let errorMessage = '';

      if (error.code === 'permission-denied') {
        submitBtn.textContent = 'Subscribe';
        errorType = 'already_subscribed';
        errorMessage = 'You\'re already subscribed! Check your email.';
      } else {
        console.error('Error subscribing:', error);
        submitBtn.textContent = 'Subscribe';
        errorType = 'subscription_failed';
        errorMessage = 'Failed to subscribe. Please try again.';
      }

      this.showMessage(errorMessage, 'error');

      // Emit GTM event for error
      if (window.gtag) {
        gtag('event', 'subscribe_popup_error', {
          event_category: 'engagement',
          event_label: 'popup_modal',
          error_type: errorType
        });
      }

      submitBtn.disabled = false;
      this.isSubmitting = false;
    }
  }

  showMessage(text, type = 'info') {
    // Remove any existing message
    const existingMsg = this.querySelector('.subscribe-popup-message');
    if (existingMsg) {
      existingMsg.remove();
    }

    const content = this.querySelector('.subscribe-popup-content');
    if (!content) return;

    const messageEl = document.createElement('div');
    messageEl.className = `subscribe-popup-message subscribe-popup-message-${type}`;
    messageEl.textContent = text;

    // Insert after the close button
    content.insertBefore(messageEl, content.querySelector('h3'));

    // Auto-remove after 4 seconds (unless it's a success, which closes the popup)
    if (type !== 'success') {
      setTimeout(() => {
        messageEl.remove();
      }, 4000);
    }
  }

  render() {
    this.innerHTML = `
      <div class="subscribe-popup-modal" style="display: none;">
        <div class="subscribe-popup-overlay"></div>
        <div class="subscribe-popup-content">
          <button class="subscribe-popup-close">×</button>
          <h3>Stay updated</h3>
          <p>Get new posts in your inbox</p>
          <form class="subscribe-popup-form">
            <input
              type="email"
              class="subscribe-popup-input"
              placeholder="your@email.com"
              required
            />
            <button type="submit" class="subscribe-popup-submit">Subscribe</button>
          </form>
        </div>
      </div>
    `;
  }

  injectStyles() {
    if (document.getElementById('subscribe-popup-styles')) return;

    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const isDark = theme === 'dark';

    const style = document.createElement('style');
    style.id = 'subscribe-popup-styles';
    style.textContent = `
      .subscribe-popup-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      }

      .subscribe-popup-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
      }

      .subscribe-popup-content {
        position: relative;
        background: ${isDark ? '#1a1a1a' : '#fff'};
        color: ${isDark ? '#e0e0e0' : '#000'};
        border-radius: 8px;
        padding: 2rem;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease-out;
      }

      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .subscribe-popup-close {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: none;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        color: ${isDark ? '#999' : '#666'};
        padding: 0;
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .subscribe-popup-close:hover {
        color: ${isDark ? '#e0e0e0' : '#000'};
      }

      .subscribe-popup-content h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.25rem;
        font-weight: 600;
      }

      .subscribe-popup-content p {
        margin: 0 0 1.5rem 0;
        font-size: 0.95rem;
        color: ${isDark ? '#aaa' : '#666'};
      }

      .subscribe-popup-form {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
      }

      .subscribe-popup-input {
        padding: 0.75rem;
        border: 1px solid ${isDark ? '#444' : '#ddd'};
        border-radius: 4px;
        background: ${isDark ? '#2a2a2a' : '#f9f9f9'};
        color: ${isDark ? '#e0e0e0' : '#000'};
        font-size: 0.95rem;
      }

      .subscribe-popup-input:focus {
        outline: none;
        border-color: #007bff;
        background: ${isDark ? '#333' : '#fff'};
      }

      .subscribe-popup-input::placeholder {
        color: ${isDark ? '#777' : '#999'};
      }

      .subscribe-popup-submit {
        padding: 0.75rem;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s ease;
      }

      .subscribe-popup-submit:hover:not(:disabled) {
        background: #0056b3;
      }

      .subscribe-popup-submit:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .subscribe-popup-message {
        padding: 0.75rem 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        animation: slideDown 0.3s ease-out;
      }

      @keyframes slideDown {
        from {
          opacity: 0;
          transform: translateY(-10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .subscribe-popup-message-error {
        background: ${isDark ? '#3a2020' : '#ffe6e6'};
        color: ${isDark ? '#ff6b6b' : '#d32f2f'};
        border-left: 3px solid ${isDark ? '#ff6b6b' : '#d32f2f'};
      }

      .subscribe-popup-message-info {
        background: ${isDark ? '#203a3a' : '#e3f2fd'};
        color: ${isDark ? '#64b5f6' : '#1976d2'};
        border-left: 3px solid ${isDark ? '#64b5f6' : '#1976d2'};
      }

      .subscribe-popup-message-success {
        background: ${isDark ? '#203a25' : '#e8f5e9'};
        color: ${isDark ? '#66bb6a' : '#2e7d32'};
        border-left: 3px solid ${isDark ? '#66bb6a' : '#2e7d32'};
      }

      @media (max-width: 600px) {
        .subscribe-popup-content {
          padding: 1.5rem;
          max-width: 100%;
          margin: 0 1rem;
        }

        .subscribe-popup-content h3 {
          font-size: 1.1rem;
        }
      }
    `;

    document.head.appendChild(style);
  }

  attachEventListeners() {
    const closeBtn = this.querySelector('.subscribe-popup-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.hidePopup());
    }

    const overlay = this.querySelector('.subscribe-popup-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this.hidePopup());
    }

    const form = this.querySelector('.subscribe-popup-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubscribe(e));
    }
  }

  disconnectedCallback() {
    if (this.scrollListener) {
      window.removeEventListener('scroll', this.scrollListener);
    }
  }
}

customElements.define('subscribe-popup', SubscribePopup);
