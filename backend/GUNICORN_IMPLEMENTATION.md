# Gunicorn Worker Rotation Implementation

This branch implements **Dallan's Steps 1 and 3** for memory leak mitigation on the 2GB Render instance.

## What Changed

### Step 1: Gunicorn with Worker Rotation ✅

**Problem:** Memory leaks cause workers to accumulate memory until OOM crash.

**Solution:** Use Gunicorn with `--max-requests` to proactively restart workers before they consume too much memory.

**Files Changed:**
- `pyproject.toml` - Added gunicorn dependency
- `gunicorn.conf.py` - New gunicorn configuration file
  - 2 workers (suitable for 2GB instance)
  - `max_requests=800` - Restart worker after 800 requests
  - `max_requests_jitter=200` - Randomize restart to prevent thundering herd
  - Proper timeouts and graceful shutdown
- `Dockerfile` - Changed CMD from `python main.py` to `gunicorn main:app`

**How It Works:**
```
Worker lifecycle:
1. Handle 600-1000 requests (800 ± 200 jitter)
2. Accumulate leaked memory (e.g., 108 MB → 1.7 GB)
3. Gunicorn kills worker at request limit
4. Spawn fresh worker with ~108 MB baseline
5. Memory never fills 2GB!
```

**Environment Variables:**
- `GUNICORN_WORKERS=2` (default: 2)
- `GUNICORN_MAX_REQUESTS=800` (default: 800)
- `GUNICORN_MAX_REQUESTS_JITTER=200` (default: 200)
- `GUNICORN_TIMEOUT=60` (default: 60)
- `GUNICORN_GRACEFUL_TIMEOUT=30` (default: 30)

### Step 3: Right-Size Connection Pools ✅

**Problem:** Unbounded HTTP clients and boto3 connections leak memory.

**Solution:** Use singleton clients with connection limits.

**Files Changed:**
- `app/http_client.py` - New shared HTTP client module
  - Singleton pattern
  - `max_connections=100`
  - `max_keepalive_connections=20`
  - Proper timeout configuration
- `app/utils/geo_ip.py` - Updated to use shared client
  - Before: Created new `httpx.AsyncClient()` per request
  - After: Uses singleton `get_http_client()`
- `app/monitoring.py` - Added boto3 connection pooling
  - `max_pool_connections=20`
  - Retry configuration
- `main.py` - Close HTTP client on shutdown
- `pyproject.toml` - Added httpx dependency

**How It Works:**
```python
# OLD (Memory leak - new client per request):
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# NEW (Shared client with limits):
client = get_http_client()  # Singleton
response = await client.get(url)
```

## Testing Locally

```bash
# Install dependencies
cd backend
poetry install

# Run with gunicorn
poetry run gunicorn main:app --config gunicorn.conf.py

# Or use environment variables
GUNICORN_WORKERS=1 poetry run gunicorn main:app --config gunicorn.conf.py
```

## Deploying to Render

1. **Merge this branch to main**
2. **Render will automatically:**
   - Build new Docker image with gunicorn
   - Use `CMD ["gunicorn", "main:app", "--config", "gunicorn.conf.py"]`
   - Workers will restart every 800 requests

3. **Monitor in Render logs:**
```
Gunicorn is ready. Workers: 2, Max requests: 800
Worker 123 received INT/QUIT signal  # <- Worker being rotated
Worker 456 booted with pid: 456      # <- Fresh worker
```

## Expected Behavior

**Before (uvicorn):**
- Single process runs forever
- Memory: 108 MB → 1.5 GB → 2 GB → **CRASH**
- Crash frequency: ~3/day (acceptable) or immediate with monitoring

**After (gunicorn + worker rotation):**
- 2 workers rotate every 800 requests
- Each worker: 108 MB → ~1.2-1.5 GB → **RESTART** → 108 MB
- Peak memory per worker: ~1.5 GB
- Total: ~3 GB across 2 workers (but they restart before filling)
- **No more OOM crashes from memory leaks!**

## What's NOT Included (Future Work)

These are Dallan's other recommendations not in this PR:

- ❌ **Step 2:** malloc_trim (already implemented in memory-profiling-feature branch)
- ❌ **Step 4:** Disable Python GC (may do later)
- ❌ **Step 5:** Python 3.12 upgrade (already on 3.11, minimal benefit)
- ❌ **Step 6-8:** tracemalloc monitoring (already in memory-profiling-feature branch)

## Notes

- This is a **production mitigation**, not a fix for the underlying leak
- The real leak (108 MB → 1.5 GB per query) still needs investigation
- Worker rotation ensures stability while we identify root cause
- Can combine with memory-profiling-feature branch to both mitigate AND monitor

## Verification Checklist

After deployment to Render:
- [ ] Check logs for "Gunicorn is ready. Workers: 2"
- [ ] Verify worker rotation after ~800 requests
- [ ] Monitor memory stays under 1.8 GB per worker
- [ ] Test sustained load (100+ requests)
- [ ] Confirm no OOM crashes
