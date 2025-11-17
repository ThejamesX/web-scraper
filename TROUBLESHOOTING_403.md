# Troubleshooting HTTP 403 Errors

If you're experiencing HTTP 403 Forbidden errors when searching e-commerce sites, this guide will help you resolve the issue.

## What is HTTP 403?

HTTP 403 Forbidden means the website is blocking your requests, typically due to anti-bot protection mechanisms. This is common on e-commerce sites that want to prevent automated scraping.

## Built-in Solutions

The scraper includes several built-in mechanisms to handle 403 errors:

### 1. Automatic Retry with Exponential Backoff
The scraper automatically retries failed requests up to 3 times with increasing delays:
- First retry: ~2 seconds delay
- Second retry: ~4 seconds delay
- Third retry: ~8 seconds delay

Random jitter is added to make the retries appear more natural.

### 2. Enhanced HTTP Headers
The scraper uses realistic browser headers including:
- Modern Chrome User-Agent
- Czech language preference (cs-CZ) for Czech sites
- Sec-Fetch-* headers to mimic real browser behavior
- Referer headers for subsequent requests
- Cache-Control headers

### 3. Mock Mode (Fallback Option)

If you continue to experience 403 errors and need to test the application, you can enable mock mode:

1. Create or edit your `.env` file:
```env
SCRAPER_MOCK_MODE=true
```

2. Restart the application

When mock mode is enabled:
- Search requests that fail will return mock product data
- Product tracking will work with mock prices
- You can test the full application functionality without making real HTTP requests

**Note**: Mock mode is intended for testing and development. For production use, the real scraping should work with the built-in retry mechanisms.

## Additional Tips

### 1. Respect Rate Limits
Avoid making too many requests in a short time period. The scraper includes built-in delays, but if you're making many searches manually, space them out.

### 2. Check Your Network
Sometimes 403 errors can be caused by:
- Corporate firewalls or proxies
- VPN services that are blocked by the e-commerce site
- Your IP address being temporarily blocked due to excessive requests

Try:
- Disabling VPN temporarily
- Using a different network connection
- Waiting a few hours before trying again

### 3. Verify Site Accessibility
Make sure you can access the e-commerce site directly in your browser:
- Alza.cz: https://www.alza.cz/
- Smarty.cz: https://www.smarty.cz/
- Allegro.pl: https://allegro.pl/

If the site is blocking you in a regular browser, the scraper will also be blocked.

### 4. Browser Cookies
The scraper maintains session cookies automatically through httpx. If you're still experiencing issues after clearing the application and restarting, the cookies will be refreshed.

## Technical Details

### How the Retry Logic Works

```python
# Pseudo-code of the retry mechanism
for attempt in range(3):
    try:
        # Add random delay to appear human-like
        if attempt > 0:
            delay = exponential_backoff(attempt) * random_jitter()
            wait(delay)
        
        # Make request with enhanced headers
        response = make_request(url, headers={
            'User-Agent': 'Chrome 120',
            'Accept-Language': 'cs-CZ',
            'Sec-Fetch-Dest': 'document',
            'Referer': site_homepage,
            # ... more headers
        })
        
        return response
    except HTTP403:
        if last_attempt:
            # If mock mode enabled, return mock data
            if SCRAPER_MOCK_MODE:
                return mock_data()
            raise
        # Otherwise, retry
```

### Headers Sent

The scraper sends the following headers to appear as a real browser:

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Language: cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate, br
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Cache-Control: max-age=0
Referer: https://www.alza.cz/ (for Alza requests)
```

## Still Having Issues?

If you've tried all the above and still experience 403 errors:

1. **Enable mock mode temporarily** to verify the rest of your setup works
2. **Check application logs** for detailed error messages
3. **Report the issue** with:
   - The exact error message
   - Which site you're trying to scrape (Alza, Smarty, Allegro)
   - Your network setup (VPN, proxy, etc.)
   - Whether the site works in a regular browser

## Prevention

To minimize the risk of 403 errors:
- Don't make excessive requests in a short time
- Use the price tracking feature (automatic checks every 4 hours) instead of manual repeated searches
- Enable mock mode for development and testing
- Only scrape when you actually need real data

## Configuration Reference

### Environment Variables

```env
# Enable mock mode to bypass 403 errors during testing
SCRAPER_MOCK_MODE=false

# Request timeout in milliseconds
SCRAPER_TIMEOUT=30000

# Price check interval (for tracked products)
PRICE_CHECK_INTERVAL_HOURS=4
```

See `.env.example` for all available configuration options.
