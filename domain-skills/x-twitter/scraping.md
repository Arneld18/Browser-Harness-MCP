# X (Twitter) — Scraping & Data Extraction

Read-only extraction patterns for X.com. No auth-risk write actions.

## JSON-like extraction via DOM (logged-in)

X has no public JSON API. All extraction goes through the logged-in browser DOM
using `data-testid` selectors. The React app is an SPA — always `wait(3)` after
`wait_for_load()`.

## Extract tweets from any feed page

Works on: `/home`, `/search?q=...`, `/{user}`, `/notifications/mentions`.

```python
tweets = js(r"""
(() => {
    // Helper to convert "4.5K reposts" -> 4500
    const parseMetric = (label) => {
        if (!label) return 0;
        const match = label.match(/([\d\.]+)([KM]?)/i);
        if (!match) return 0;
        let num = parseFloat(match[1]);
        if (match[2].toUpperCase() === 'K') num *= 1000;
        if (match[2].toUpperCase() === 'M') num *= 1000000;
        return Math.floor(num);
    };

    return Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(el => {
        const nameBlock = el.querySelector('[data-testid="User-Name"]');
        const textBlock = el.querySelector('[data-testid="tweetText"]');
        const statusLink = el.querySelector('a[href*="/status/"]');
        const timeEl = el.querySelector('time');
        const imgEls = el.querySelectorAll('img[src*="pbs.twimg.com/media"]');
        const replyBtn = el.querySelector('[data-testid="reply"]');
        const rtBtn = el.querySelector('[data-testid="retweet"]');
        const likeBtn = el.querySelector('[data-testid="like"], [data-testid="unlike"]');
        
        return {
            url: statusLink ? 'https://x.com' + statusLink.getAttribute('href') : null,
            user: nameBlock ? nameBlock.textContent.substring(0, 80) : '',
            text: textBlock ? textBlock.textContent.substring(0, 1000) : '',
            time: timeEl ? timeEl.getAttribute('datetime') : '',
            images: Array.from(imgEls).map(i => i.src),
            replies: parseMetric(replyBtn ? replyBtn.getAttribute('aria-label') : ''),
            reposts: parseMetric(rtBtn ? rtBtn.getAttribute('aria-label') : ''),
            likes: parseMetric(likeBtn ? likeBtn.getAttribute('aria-label') : ''),
            is_liked: !!el.querySelector('[data-testid="unlike"]'),
            is_bookmarked: !!el.querySelector('[data-testid="removeBookmark"]'),
        };
    }).filter(t => t.url);
})()
""")
```

## Extract a single tweet thread

```python
new_tab("https://x.com/{user}/status/{id}")
wait_for_load()
wait(3)

thread = js(r"""
(() => {
    const main = document.querySelector('[data-testid="tweet"]');
    const replies = Array.from(document.querySelectorAll('article[data-testid="tweet"]')).slice(1);
    function extract(el) {
        const t = el.querySelector('[data-testid="tweetText"]');
        const n = el.querySelector('[data-testid="User-Name"]');
        return {
            user: n ? n.textContent.substring(0, 80) : '',
            text: t ? t.textContent.substring(0, 2000) : ''
        };
    }
    return {
        main: main ? extract(main) : null,
        replies: replies.slice(0, 20).map(extract)
    };
})()
""")
```

## Search operators (use in the `q=` param)

| Operator | Example | Effect |
|----------|---------|--------|
| `from:` | `from:elonmusk` | Tweets from a specific user |
| `to:` | `to:openai` | Replies to a user |
| `@` | `@anthropic` | Mentions of a user |
| `#` | `#buildinpublic` | Hashtag |
| `min_faves:` | `min_faves:100` | Min likes |
| `min_retweets:` | `min_retweets:50` | Min reposts |
| `since:` | `since:2026-04-01` | After date |
| `until:` | `until:2026-04-28` | Before date |
| `filter:links` | `AI agents filter:links` | Only tweets with links |
| `filter:media` | `startup filter:media` | Only tweets with images/video |
| `-filter:replies` | `AI -filter:replies` | Exclude replies |
| `lang:` | `lang:es` | Language filter |

Combine: `from:sama AI since:2026-04-01 min_faves:50`

## Gotchas

- **aria-label on engagement buttons** contains the count as text (e.g., "42 replies"). Parse the leading number.
- **Quoted tweets** create a nested article — deduplicate by `href` containing `/status/`.
- **Promoted tweets** have an extra "Ad" badge but same `article[data-testid="tweet"]` structure. Filter by checking for `[data-testid="placementTracking"]` ancestor.
- **Time attribute** is ISO 8601 (`datetime` attr on `<time>`) — use it over the display text ("15h", "Apr 20").
- **Images** from `pbs.twimg.com/media` can be fetched directly; append `?format=jpg&name=large` for full resolution.
