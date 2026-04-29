# X (Twitter) — Community Manager Skill

Expert Community Manager harness for X.com. Covers navigation, search, composing,
replying, reposting, bookmarking, timeline reading, and interaction monitoring.

**Requires:** Logged-in Chrome session via browser-harness. All write actions
(post, reply, repost) require **explicit user confirmation** before execution.

---

## 🔒 Safety Protocol — MANDATORY

Every write action MUST follow this flow:

1. **Draft** — compose the content in-memory or in the compose box WITHOUT clicking Post.
2. **Present** — show the user the exact text (and any media) that will be published.
3. **Confirm** — wait for explicit "yes" / "go ahead" / "publish it" before clicking Post.
4. **Verify** — screenshot after posting to confirm success.

**Never** auto-publish. **Never** bypass confirmation. If the user says "post this",
present the draft first, then ask "Confirm publication?".

---

## Auth check

```python
auth = js("""
(() => {
    if (location.href.includes('/login') || location.href.includes('/i/flow/login'))
        return {ok: false, reason: 'login_page'};
    const profile = document.querySelector('a[data-testid="AppTabBar_Profile_Link"]');
    return {
        ok: !!profile,
        username: profile ? profile.getAttribute('href').replace('/','') : null
    };
})()
""")
if not auth["ok"]:
    sys.exit("AUTH_WALL — user must log in to X.com first.")
```

---

## URL patterns

| What | URL |
|------|-----|
| Home timeline | `https://x.com/home` |
| Explore / trending | `https://x.com/explore` |
| Trending tab | `https://x.com/explore/tabs/trending` |
| Search | `https://x.com/search?q={query}&src=typed_query` |
| Search (latest) | `https://x.com/search?q={query}&src=typed_query&f=live` |
| Search (people) | `https://x.com/search?q={query}&src=typed_query&f=user` |
| Search (media) | `https://x.com/search?q={query}&src=typed_query&f=media` |
| User profile | `https://x.com/{username}` |
| User's replies | `https://x.com/{username}/with_replies` |
| User's media | `https://x.com/{username}/media` |
| User's likes | `https://x.com/{username}/likes` |
| Single post | `https://x.com/{username}/status/{id}` |
| Notifications | `https://x.com/notifications` |
| Mentions | `https://x.com/notifications/mentions` |
| Bookmarks | `https://x.com/i/bookmarks` |
| Compose (popup) | Click `[data-testid="SideNav_NewTweet_Button"]` |

---

## DOM anchors (verified live 2026-04-28)

X uses React with stable `data-testid` attributes. These are your primary selectors.

### Navigation

| Target | Selector |
|--------|----------|
| Home link | `a[data-testid="AppTabBar_Home_Link"]` |
| Explore link | `a[data-testid="AppTabBar_Explore_Link"]` |
| Notifications link | `a[data-testid="AppTabBar_Notifications_Link"]` |
| Messages link | `a[data-testid="AppTabBar_DirectMessage_Link"]` |
| Profile link | `a[data-testid="AppTabBar_Profile_Link"]` |
| Compose button (sidebar) | `[data-testid="SideNav_NewTweet_Button"]` |
| Account switcher | `[data-testid="SideNav_AccountSwitcher_Button"]` |
| Search input | `[data-testid="SearchBox_Search_Input"]` |
| Timeline tabs | `[role="tab"]` — text content: "For you", "Following", etc. |

### Tweet structure

| Target | Selector | Notes |
|--------|----------|-------|
| Tweet article | `article[data-testid="tweet"]` | One per tweet in feed |
| Tweet text | `[data-testid="tweetText"]` | Inside the article |
| User name block | `[data-testid="User-Name"]` | Contains display name + @handle + timestamp |
| Reply button | `[data-testid="reply"]` | Inside the article |
| Retweet/Repost button | `[data-testid="retweet"]` | Opens menu with Repost/Quote |
| Like button | `[data-testid="like"]` | Toggles to `[data-testid="unlike"]` when liked |
| Bookmark button | `[data-testid="bookmark"]` | Toggles to `[data-testid="removeBookmark"]` |
| Share button | `[data-testid="share"]` | Opens share menu |
| More menu (⋯) | `[data-testid="caret"]` | Per-tweet overflow menu |

### Compose box (inline at top of /home)

| Target | Selector |
|--------|----------|
| Compose text area | `[data-testid="tweetTextarea_0"]` |
| Post button (inline) | `[data-testid="tweetButtonInline"]` |
| Compose placeholder | The "What's happening?" text |

### Compose dialog (from sidebar button)

| Target | Selector |
|--------|----------|
| Dialog text area | `[data-testid="tweetTextarea_0"]` (same testid) |
| Post button (dialog) | `[data-testid="tweetButton"]` |
| Close dialog | `[data-testid="app-bar-close"]` |
| Add media | `[data-testid="fileInput"]` (hidden input[type="file"]) |
| Emoji picker | `[data-testid="emojiButton"]` |

---

## 1. Read timeline

```python
new_tab("https://x.com/home")
wait_for_load()
wait(3)

tweets = js(r"""
(() => {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    return Array.from(articles).slice(0, 15).map(el => {
        const nameEl = el.querySelector('[data-testid="User-Name"]');
        const parts = nameEl ? nameEl.textContent : '';
        const textEl = el.querySelector('[data-testid="tweetText"]');
        const links = textEl ? Array.from(textEl.querySelectorAll('a')).map(a => a.href) : [];
        const metrics = Array.from(el.querySelectorAll('[data-testid="reply"], [data-testid="retweet"], [data-testid="like"]'))
            .map(b => b.getAttribute('aria-label'));
        return {
            user: parts.substring(0, 80),
            text: textEl ? textEl.textContent.substring(0, 500) : '',
            links: links,
            metrics: metrics
        };
    });
})()
""")
for t in tweets:
    print(f"@{t['user'][:40]}: {t['text'][:120]}")
```

### Scroll for more tweets

```python
seen = {}
for i in range(10):
    batch = js(r"""
    Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(el => {
        const text = el.querySelector('[data-testid="tweetText"]');
        const name = el.querySelector('[data-testid="User-Name"]');
        const link = el.querySelector('a[href*="/status/"]');
        return {
            id: link ? link.getAttribute('href') : null,
            user: name ? name.textContent.substring(0, 80) : '',
            text: text ? text.textContent.substring(0, 500) : ''
        };
    }).filter(t => t.id)
    """) or []
    for t in batch:
        seen.setdefault(t["id"], t)
    if len(seen) >= 30:
        break
    scroll(640, 400, dy=800)
    wait(2)
```

### Expand long posts ("Show more")

Long posts truncate their text and show a "Show more" button. Run this before extraction to get the full text.

```python
# Click all "Show more" buttons visible in the timeline
js("""
    var btns = document.querySelectorAll('article[data-testid="tweet"] [role="button"]');
    for (var b of btns) {
        var text = b.textContent.trim();
        if (text === 'Show more' || text === 'Mostrar más') {
            b.click();
        }
    }
""")
wait(2) # Give React time to fetch and render the full text
```

---

## 2. Search

### Search for posts

```python
import urllib.parse
query = urllib.parse.quote("browser-use AI agent")
new_tab(f"https://x.com/search?q={query}&src=typed_query&f=live")
wait_for_load()
wait(3)
# Then extract tweets with the same article[data-testid="tweet"] pattern
```

### Search for people

```python
new_tab(f"https://x.com/search?q={query}&src=typed_query&f=user")
wait_for_load()
wait(3)

users = js(r"""
Array.from(document.querySelectorAll('[data-testid="UserCell"]')).map(cell => {
    const name = cell.querySelector('[data-testid="User-Name"]');
    const bio = cell.querySelector('[data-testid="UserDescription"]');
    const link = cell.querySelector('a[href^="/"]');
    return {
        name: name ? name.textContent.substring(0, 60) : '',
        bio: bio ? bio.textContent.substring(0, 200) : '',
        url: link ? link.getAttribute('href') : ''
    };
})
""")
```

### Trending topics

```python
new_tab("https://x.com/explore/tabs/trending")
wait_for_load()
wait(3)

trends = js(r"""
Array.from(document.querySelectorAll('[data-testid="trend"]')).map(el => ({
    text: el.textContent.substring(0, 120),
}))
""")
```

---

## 3. Compose & publish a post (with safety)

X enforces a strict character limit (~280 chars for non-premium). Drafts exceeding this will cause the post button to disable or highlight red.
Additionally, React state prevents clearing the draft via standard DOM text manipulation (`document.execCommand("delete")` may fail). The safest way to replace a draft is to close the dialog, discard, and reopen.

```python
import random

def human_wait():
    wait(random.uniform(2.0, 5.0))

# Step 1: Open compose dialog
js('document.querySelector("[data-testid=SideNav_NewTweet_Button]").click()')
human_wait()

# Step 2: Type the draft (ensure it's under 280 chars if non-premium)
draft_text = "Your short, concise post content here."
js('document.querySelector("[data-testid=tweetTextarea_0]").focus()')
type_text(draft_text)
human_wait()

# Step 3: Take screenshot and present to user for confirmation
capture_screenshot()
print(f"DRAFT READY: '{draft_text}'")
print("⚠️ Awaiting user confirmation before posting. Check screenshot for character limit warnings.")
# >>> STOP HERE — do NOT click Post until user confirms <<<

# Step 4: After user confirms, click Post
js('document.querySelector("[data-testid=tweetButton]").click()')
human_wait()
capture_screenshot()  # verify success
```

### Clear a broken draft (Discard)

If a draft needs to be completely replaced (e.g. it's too long), trying to backspace is unreliable. Close the modal, discard, and restart.

```python
# Close compose dialog
js('document.querySelector("[data-testid=app-bar-close]")?.click()')
human_wait()

# If "Discard" / "Descartar" confirmation appears:
js("""
    var btns = document.querySelectorAll('[role="button"]');
    for (var b of btns) {
        var text = b.textContent.trim();
        if (text === 'Discard' || text === 'Descartar') { 
            b.click(); 
            break; 
        }
    }
""")
human_wait()
# You can now click SideNav_NewTweet_Button again to start fresh.
```

### Upload Media

X uses a hidden file input for media uploads. Use the `upload_file` CDP helper from `helpers.py` to securely attach files without breaking React's synthetic events.

```python
import os
image_path = os.path.abspath("post_image.png")

# Navigate to compose, then:
upload_file('[data-testid="fileInput"]', image_path)
human_wait()
print("Media file successfully attached to draft.")
```

---

## 4. Reply to a post

```python
# Navigate to the target tweet
new_tab("https://x.com/{user}/status/{tweet_id}")
wait_for_load()
wait(2)

# Click Reply
js('document.querySelector("[data-testid=reply]").click()')
wait(1)

# Type reply
reply_text = "Great insight! 🚀"
js('document.querySelector("[data-testid=tweetTextarea_0]").focus()')
type_text(reply_text)
wait(0.5)

# >>> Screenshot + confirm with user before posting <<<
capture_screenshot()
print(f"REPLY DRAFT: '{reply_text}'")

# After confirmation:
js('document.querySelector("[data-testid=tweetButton]").click()')
wait(2)
capture_screenshot()
```

---

## 5. Repost (retweet)

```python
# Find the repost button on the target tweet
# For the first tweet in the timeline:
js('document.querySelector("article[data-testid=tweet] [data-testid=retweet]").click()')
wait(0.5)

# Menu appears with "Repost" and "Quote" options
# >>> Confirm with user: "Repost this tweet?" <<<

# After confirmation — click Repost
js("""
    var items = document.querySelectorAll('[role="menuitem"]');
    for (var item of items) {
        if (item.textContent.includes('Repost')) { item.click(); break; }
    }
""")
wait(1)
capture_screenshot()
```

### Quote post

```python
js('document.querySelector("[data-testid=retweet]").click()')
wait(0.5)
js("""
    var items = document.querySelectorAll('[role="menuitem"]');
    for (var item of items) {
        if (item.textContent.includes('Quote')) { item.click(); break; }
    }
""")
wait(1)
# Now compose box opens — type your quote text
js('document.querySelector("[data-testid=tweetTextarea_0]").focus()')
type_text("My thoughts on this thread 👇")
# >>> Confirm before posting <<<
```

---

## 6. Like / Bookmark

```python
# Like — no confirmation needed (easily reversible)
js('document.querySelector("article[data-testid=tweet] [data-testid=like]").click()')

# Unlike
js('document.querySelector("article[data-testid=tweet] [data-testid=unlike]").click()')

# Bookmark
js('document.querySelector("article[data-testid=tweet] [data-testid=bookmark]").click()')

# Remove bookmark
js('document.querySelector("article[data-testid=tweet] [data-testid=removeBookmark]").click()')
```

---

## 7. Monitor notifications & mentions

```python
new_tab("https://x.com/notifications/mentions")
wait_for_load()
wait(3)

mentions = js(r"""
Array.from(document.querySelectorAll('article[data-testid="tweet"]')).slice(0, 10).map(el => {
    const name = el.querySelector('[data-testid="User-Name"]');
    const text = el.querySelector('[data-testid="tweetText"]');
    const link = el.querySelector('a[href*="/status/"]');
    return {
        from: name ? name.textContent.substring(0, 60) : '',
        text: text ? text.textContent.substring(0, 300) : '',
        url: link ? 'https://x.com' + link.getAttribute('href') : ''
    };
})
""")
for m in mentions:
    print(f"{m['from']}: {m['text'][:100]}")
```

### Notification badge count

```python
badge = js("""
    var el = document.querySelector('[data-testid="AppTabBar_Notifications_Link"]');
    var badge = el ? el.textContent.replace('Notifications', '').trim() : '0';
    return badge || '0';
""")
```

---

## 8. Profile inspection

```python
new_tab("https://x.com/{username}")
wait_for_load()
wait(3)

profile = js(r"""
(() => {
    const name = document.querySelector('[data-testid="UserName"]');
    const bio = document.querySelector('[data-testid="UserDescription"]');
    const loc = document.querySelector('[data-testid="UserLocation"]');
    const url = document.querySelector('[data-testid="UserUrl"]');
    const joined = document.querySelector('[data-testid="UserJoinDate"]');
    const following = document.querySelector('a[href$="/following"] span span');
    const followers = document.querySelector('a[href$="/verified_followers"] span span, a[href$="/followers"] span span');
    return {
        name: name ? name.textContent : '',
        bio: bio ? bio.textContent : '',
        location: loc ? loc.textContent : '',
        website: url ? url.textContent : '',
        joined: joined ? joined.textContent : '',
        following: following ? following.textContent : '',
        followers: followers ? followers.textContent : ''
    };
})()
""")
```

---

## Rate-limit discipline

- **≥2s between scroll-collects** inside feed loops
- **≥3s between navigations** to different profiles/pages
- **Max ~20 profile visits per hour** for sustained monitoring
- **Max ~10 search queries per hour** to avoid soft-throttle
- **Don't repeat the same search within 5 minutes**

Symptoms of over-pacing: empty feeds where you expect content, redirect to
`/i/flow/login`, or tweets rendering as "Something went wrong". If any fire,
**stop** and wait 2–5 minutes before retrying.

---

## Self-inspection block

Run when selectors stop working:

```python
print(js(r"""
({
    tweets: document.querySelectorAll('article[data-testid="tweet"]').length,
    tweetText: document.querySelectorAll('[data-testid="tweetText"]').length,
    userName: document.querySelectorAll('[data-testid="User-Name"]').length,
    reply: document.querySelectorAll('[data-testid="reply"]').length,
    retweet: document.querySelectorAll('[data-testid="retweet"]').length,
    like: document.querySelectorAll('[data-testid="like"]').length,
    compose: !!document.querySelector('[data-testid="SideNav_NewTweet_Button"]'),
    search: !!document.querySelector('[data-testid="SearchBox_Search_Input"]'),
    profile_link: !!document.querySelector('[data-testid="AppTabBar_Profile_Link"]'),
})
"""))
```

---

## 9. Direct Messages (DMs)

Handling the private inbox. **Always use Human-in-the-loop before sending DMs**.

### Read Inbox

```python
new_tab("https://x.com/messages")
wait_for_load()
wait(3)

chats = js(r"""
Array.from(document.querySelectorAll('[data-testid="conversation"]')).map(el => {
    const name = el.querySelector('[data-testid="conversation"] span');
    return {
        name: name ? name.textContent : 'Unknown',
    };
})
""")
for c in chats:
    print(c)
```

### Send a DM (with safety)

```python
import random
def human_wait(): wait(random.uniform(2.0, 5.0))

# Navigate to specific chat by clicking on it in the inbox first
js('document.querySelector("[data-testid=conversation]").click()')
human_wait()

draft_msg = "Hello! Thanks for reaching out."
js('document.querySelector("[data-testid=dmComposerTextInput]").focus()')
type_text(draft_msg)
human_wait()

capture_screenshot()
print("DM DRAFT READY. Awaiting user confirmation.")
# >>> STOP HERE <<<

# After user confirms:
js('document.querySelector("[data-testid=dmComposerSendButton]").click()')
human_wait()
```

---

## 10. Health Check / Rate Limit Detection

If you hit a rate limit, X will sometimes shadow-throttle your feed or force a login redirect.

```python
def check_x_health():
    health = js(r"""
    (() => {
        if (location.href.includes('/login')) return { ok: false, reason: 'forced_login' };
        
        const emptyState = document.querySelector('[data-testid="emptyState"]');
        if (emptyState && emptyState.textContent.includes('Something went wrong')) {
            return { ok: false, reason: 'rate_limit_empty_state' };
        }
        
        const retryBtn = Array.from(document.querySelectorAll('span')).find(s => s.textContent === 'Retry');
        if (retryBtn) {
            return { ok: false, reason: 'retry_button_present' };
        }
        
        return { ok: true, reason: 'clean' };
    })()
    """)
    if not health["ok"]:
        print(f"⚠️ HEALTH CHECK FAILED: {health['reason']}. Stopping automation to prevent ban.")
        return False
    return True

check_x_health()
```

---

## Gotchas

- **`wait_for_load()` is not enough.** X's React app hydrates after DOMContentLoaded. Always add `wait(2)`–`wait(3)` after `wait_for_load()`.
- **Tweet text can be empty.** Image-only or video-only tweets have no `[data-testid="tweetText"]` element. Null-check before `.textContent`.
- **Repost button opens a menu, not a toggle.** You must click the "Repost" menu item after clicking `[data-testid="retweet"]`.
- **Compose textarea is `contenteditable`, not `<input>`.** Use `type_text()`, never set `.value`. Clear with Ctrl+A then Backspace/Delete.
- **Like/Unlike share the same position** but have different testids (`like` vs `unlike`). Check which one is visible before clicking.
- **Draft discard dialog** — closing compose with text triggers a "Discard" confirmation. Handle it or the dialog blocks further interaction.
- **Timeline tabs are dynamic.** Users configure custom lists as tabs ("NoCode", "VibeCoders", etc.). Don't hardcode tab names beyond "For you" and "Following".
- **Notification badge text** is concatenated with the link text (e.g., "2Notifications"). Parse the leading digits.
- **Media uploads** use a hidden `input[type="file"]` with testid `fileInput`. Use `upload_file('[data-testid="fileInput"]', path)`.
- **Thread/long posts** render with a "Show more" that must be clicked before full text is visible.
- **Quoted tweets** nest an inner `article` — your selectors may double-match. Use `:scope > ...` or filter by depth.
