# Crawl4AI Deep Crawler Application

This application provides a reusable command-line interface for Crawl4AI's deep crawling functionality. It allows you to configure various crawling parameters and filters to customize your web crawling experience.

## Features

### Core Crawling Capabilities
- Configurable crawl depth and page limits
- Domain filtering (allow/block specific domains)
- URL pattern filtering
- Content type filtering including **PDF support**
- Flexible markdown generation:
  - Default markdown generation without content filtering
  - Content filtering with multiple options:
    - PruningContentFilter: Scores nodes by text density, link density, and tag importance
    - BM25ContentFilter: Focuses on textual relevance using BM25 ranking algorithm
    - LLMContentFilter: Uses LLMs for intelligent content filtering and extraction
- Customizable markdown output options
- Intelligent markdown saving: saves only filtered content when using content filters
- Verbose output option
- Structured result display

### 🚀 New 0.7.x Features (Adaptive Intelligence Update)

#### **Virtual Scroll Support** 🌊
- **Complete content capture** from infinite scroll pages (Twitter, Instagram, news feeds)
- **Intelligent deduplication** based on normalized text content
- **Three scrolling scenarios** handled automatically:
  - Content unchanged (continue scrolling)
  - Content appended (traditional infinite scroll)
  - Content replaced (true virtual scroll - social media style)
- **Configurable scroll parameters**: amount, count, and wait times
- **Seamless integration** with existing extraction strategies

#### **Async URL Seeder** 🎣
- **Automated URL discovery** from sitemaps and Common Crawl index
- **BM25 relevance scoring** for query-based URL filtering
- **Multi-domain parallel discovery** with intelligent caching
- **Live URL validation** with HEAD requests
- **Metadata extraction** (JSON-LD, Open Graph)
- **Scale from single URLs to thousands** with intelligent filtering

#### **Enhanced PDF Processing** 📄
- **Native PDF document crawling** and content extraction
- **Seamless integration** with existing content filters
- **Multi-format support**: HTML + PDF in single crawl sessions

#### **Performance & Intelligence Optimizations** ⚡
- **Lighter dependencies** for faster installation
- **Improved Docker support** with optimized images
- **Enhanced CI/CD pipeline** for reliable releases
- **Adaptive pattern learning** for website-specific optimizations

### Advanced Crawling Features
- Rate limiting with configurable delays and automatic backoff
- Memory-adaptive dispatching to prevent system overload
- Streaming mode for real-time result processing
- Real-time monitoring of crawling progress
- Configurable cache modes

## Installation

Ensure you have the Crawl4AI library installed:

```bash
pip install crawl4ai
```

## Usage

### Basic Usage

```bash
python webscraper_crawl4ai.py https://example.com
```

This will crawl `https://example.com` with default settings (max depth of 2, no page limit, no external domains).

### Basic Usage with Default Markdown Generation

```bash
python webscraper_crawl4ai.py https://example.com \
    --save-markdown \
    --output-dir "./markdown_output"
```

This will generate markdown without any content filtering, preserving most of the original content.

### Advanced Usage with Pruning Filter

```bash
python webscraper_crawl4ai.py https://example.com \
    --max-depth 3 \
    --max-pages 50 \
    --include-external \
    --verbose \
    --url-patterns "*blog*" "*news*" \
    --allowed-domains "example.com" "blog.example.com" \
    --blocked-domains "ads.example.com" \
    --allowed-content-types "text/html" "application/json" \
    --content-filter pruning \
    --pruning-threshold 0.5 \
    --threshold-type dynamic \
    --min-word-threshold 10 \
    --save-markdown \
    --output-dir "./markdown_output"
```

This will save only the filtered markdown content (after applying the pruning filter).

### Advanced Usage with BM25 Filter

```bash
python webscraper_crawl4ai.py https://example.com \
    --max-depth 2 \
    --content-filter bm25 \
    --user-query "machine learning tutorial" \
    --bm25-threshold 1.2 \
    --use-stemming \
    --save-markdown \
    --output-dir "./bm25_output"
```

This will save only the filtered markdown content (after applying the BM25 filter).

### Advanced Usage with LLM Filter

```bash
python webscraper_crawl4ai.py https://example.com \
    --max-depth 2 \
    --content-filter llm \
    --llm-provider "openai/gpt-4o" \
    --llm-api-token "your-api-token" \
    --llm-instruction "Extract the main educational content and code examples. Remove navigation, ads, and footers." \
    --chunk-token-threshold 4096 \
    --llm-verbose \
    --save-markdown \
    --output-dir "./llm_output"
```

This will save only the filtered markdown content (after applying the LLM filter).

### Advanced Usage with Rate Limiting and Memory Management

```bash
python webscraper_crawl4ai.py https://example.com \
    --max-depth 3 \
    --enable-rate-limiter \
    --base-delay 1.5 3.0 \
    --max-delay 30.0 \
    --max-retries 5 \
    --dispatcher memory \
    --memory-threshold 80.0 \
    --max-concurrent 8 \
    --enable-monitor \
    --save-markdown \
    --output-dir "./rate_limited_output"
```

### Advanced Usage with Streaming Mode

```bash
python webscraper_crawl4ai.py https://example.com \
    --max-depth 2 \
    --stream \
    --dispatcher semaphore \
    --max-concurrent 5 \
    --enable-rate-limiter \
    --save-markdown \
    --output-dir "./streaming_output"
```

### Customizing Markdown Output Options

```bash
python webscraper_crawl4ai.py https://example.com \
    --save-markdown \
    --ignore-links \
    --ignore-images \
    --escape-html \
    --body-width 80 \
    --skip-internal-links \
    --output-dir "./custom_markdown"
```

## Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|--------|
| `url` | Starting URL for the crawl | (Required) |
| `--max-depth` | Maximum depth to crawl | 2 |
| `--max-pages` | Maximum number of pages to crawl | No limit |
| `--include-external` | Follow links to external domains | False |
| `--verbose` | Display verbose output during crawling | False |
| `--url-patterns` | URL patterns to include (e.g., '*blog*' '*news*') | None |
| `--allowed-domains` | Domains to allow (e.g., 'example.com') | None |
| `--blocked-domains` | Domains to block (e.g., 'ads.example.com') | None |
| `--allowed-content-types` | Content types to allow (e.g., 'text/html') | None |
| `--include-pdfs` | Include PDF documents in crawling | False |

### 🚀 New 0.7.x Features

#### Virtual Scroll Configuration

| Argument | Description | Default |
|----------|-------------|--------|
| `--enable-virtual-scroll` | Enable virtual scroll for infinite scroll pages | False |
| `--scroll-amount` | Amount to scroll in pixels | 1000 |
| `--max-scrolls` | Maximum number of scrolls | 10 |
| `--scroll-wait-time` | Wait time between scrolls in seconds | 2.0 |

#### URL Seeder Configuration

| Argument | Description | Default |
|----------|-------------|--------|
| `--enable-url-seeder` | Use URL seeder for automated URL discovery | False |
| `--seeder-query` | Search query for URL seeder BM25 filtering | None |
| `--seeder-sources` | URL discovery sources (`sitemap`, `cc`, `sitemap+cc`) | sitemap |
| `--seeder-score-threshold` | Minimum relevance score for seeded URLs | 0.5 |
| `--seeder-max-urls` | Maximum URLs to discover via seeder | 100 |

### Content Filter Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--content-filter` | Content filter type to use (`pruning`, `bm25`, or `llm`) | None (Optional) |

#### Pruning Filter Parameters

| Argument | Description | Default |
|----------|-------------|--------|
| `--pruning-threshold` | Threshold for content pruning (0.0-1.0) | 0.45 |
| `--threshold-type` | Threshold type for content pruning (fixed/dynamic) | dynamic |
| `--min-word-threshold` | Minimum word threshold for content pruning | 5 |

#### BM25 Filter Parameters

| Argument | Description | Default |
|----------|-------------|--------|
| `--user-query` | Search query for BM25 content filtering | None |
| `--bm25-threshold` | BM25 score threshold | 1.2 |
| `--use-stemming` | Enable word stemming for BM25 filtering | False |

#### LLM Filter Parameters

| Argument | Description | Default |
|----------|-------------|--------|
| `--llm-provider` | LLM provider for content filtering | openai/gpt-4o |
| `--llm-api-token` | API token for LLM provider | None |
| `--llm-instruction` | Custom instruction for LLM content filtering | Extract main content... |
| `--chunk-token-threshold` | Token threshold for chunk processing | 4096 |
| `--llm-verbose` | Enable verbose output for LLM filtering | False |

### Markdown Generator Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--ignore-links` | Remove all hyperlinks in the markdown output | False |
| `--ignore-images` | Remove all image references in the markdown output | False |
| `--escape-html` | Turn HTML entities into text | False |
| `--body-width` | Wrap text at N characters (0 means no wrapping) | 0 |
| `--skip-internal-links` | Omit local anchors or internal links referencing the same page | False |

### Output Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--save-markdown` | Save markdown content for each URL | False |
| `--output-dir` | Directory to save markdown files | ./output |

### Rate Limiter Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--enable-rate-limiter` | Enable rate limiting for requests | False |
| `--base-delay` | Base delay range in seconds between requests | [1.0, 3.0] |
| `--max-delay` | Maximum delay in seconds for rate limiting | 60.0 |
| `--max-retries` | Maximum number of retries for rate-limited requests | 3 |

### Dispatcher Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--dispatcher` | Type of dispatcher to use (memory/semaphore) | memory |
| `--memory-threshold` | Memory threshold percentage for adaptive dispatcher | 90.0 |
| `--check-interval` | Memory check interval in seconds | 1.0 |
| `--max-concurrent` | Maximum number of concurrent tasks/sessions | 10 |

### Streaming and Monitoring Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--stream` | Enable streaming mode to process results as they become available | False |
| `--enable-monitor` | Enable real-time monitoring of crawling progress | False |

### Cache Options

| Argument | Description | Default |
|----------|-------------|--------|
| `--cache-mode` | Cache mode for requests (enabled/bypass/refresh) | bypass |

## Examples

### Crawl a website with depth limit

```bash
python webscraper_crawl4ai.py https://example.com --max-depth 3
```

### Limit the number of pages crawled

```bash
python webscraper_crawl4ai.py https://example.com --max-pages 100
```

### Only crawl specific content types

```bash
python webscraper_crawl4ai.py https://example.com --allowed-content-types "text/html" "application/pdf"
```

### Filter by URL patterns

```bash
python webscraper_crawl4ai.py https://example.com --url-patterns "*blog*" "*article*"
```

### Stay within specific domains

```bash
python webscraper_crawl4ai.py https://example.com --allowed-domains "example.com" "docs.example.com"
```

### Generate and save basic markdown content (no content filtering)

```bash
python webscraper_crawl4ai.py https://example.com --save-markdown
```

### Generate and save markdown content with pruning filter

```bash
python webscraper_crawl4ai.py https://example.com --content-filter pruning --save-markdown --pruning-threshold 0.5
```

### Generate and save markdown content with BM25 filter

```bash
python webscraper_crawl4ai.py https://example.com --content-filter bm25 --user-query "python tutorial" --save-markdown
```

## 🚀 New 0.7.x Feature Examples

### Virtual Scroll for Infinite Scroll Pages

Capture complete content from social media feeds, news sites, and other infinite scroll pages:

```bash
# Basic virtual scroll for Twitter-like feeds
python webscraper_crawl4ai.py https://twitter.com/user/timeline \
    --enable-virtual-scroll \
    --max-scrolls 20 \
    --scroll-amount 1000 \
    --scroll-wait-time 3.0 \
    --save-markdown
```

```bash
# Advanced virtual scroll with content filtering
python webscraper_crawl4ai.py https://news-site.com \
    --enable-virtual-scroll \
    --max-scrolls 15 \
    --scroll-amount 800 \
    --content-filter bm25 \
    --user-query "breaking news technology" \
    --save-markdown
```

### URL Seeder for Automated Discovery

Discover and crawl hundreds of relevant URLs automatically:

```bash
# Discover URLs from sitemap with relevance filtering
python webscraper_crawl4ai.py https://example.com \
    --enable-url-seeder \
    --seeder-query "machine learning tutorial" \
    --seeder-sources sitemap \
    --seeder-score-threshold 0.7 \
    --seeder-max-urls 50 \
    --save-markdown
```

```bash
# Advanced URL seeding with multiple sources
python webscraper_crawl4ai.py https://docs.python.org \
    --enable-url-seeder \
    --seeder-query "python programming guide" \
    --seeder-sources sitemap cc \
    --seeder-score-threshold 0.6 \
    --seeder-max-urls 100 \
    --max-depth 2 \
    --content-filter pruning \
    --save-markdown
```

### PDF Document Processing

Include PDF documents in your crawling sessions:

```bash
# Crawl both HTML and PDF content
python webscraper_crawl4ai.py https://research-site.com \
    --include-pdfs \
    --allowed-content-types "text/html" "application/pdf" \
    --save-markdown \
    --output-dir "./research_docs"
```

```bash
# Advanced PDF + HTML crawling with URL seeder
python webscraper_crawl4ai.py https://academic-site.edu \
    --enable-url-seeder \
    --seeder-query "research papers artificial intelligence" \
    --include-pdfs \
    --seeder-max-urls 75 \
    --content-filter llm \
    --llm-provider "openai/gpt-4o" \
    --llm-instruction "Extract key research findings and methodologies" \
    --save-markdown
```

### Combined Advanced Features

Leverage multiple 0.7.x features together for maximum efficiency:

```bash
# Ultimate crawling setup with all new features
python webscraper_crawl4ai.py https://tech-blog.com \
    --enable-url-seeder \
    --seeder-query "artificial intelligence deep learning" \
    --seeder-sources sitemap+cc \
    --seeder-max-urls 200 \
    --enable-virtual-scroll \
    --max-scrolls 10 \
    --include-pdfs \
    --content-filter bm25 \
    --user-query "AI machine learning tutorial" \
    --bm25-threshold 1.5 \
    --enable-rate-limiter \
    --base-delay 2.0 4.0 \
    --dispatcher memory \
    --memory-threshold 85.0 \
    --stream \
    --save-markdown \
    --output-dir "./ai_research"
```

### Generate and save markdown content with LLM filter

```bash
python webscraper_crawl4ai.py https://example.com --content-filter llm --llm-instruction "Focus on technical content and code examples" --save-markdown
```

### Customize markdown output format

```bash
python webscraper_crawl4ai.py https://example.com --save-markdown --ignore-links --body-width 80
```

### Enable rate limiting and memory management

```bash
python webscraper_crawl4ai.py https://example.com --enable-rate-limiter --base-delay 2.0 4.0 --dispatcher memory --memory-threshold 85.0
```

### Use streaming mode with a semaphore dispatcher

```bash
python webscraper_crawl4ai.py https://example.com --stream --dispatcher semaphore --max-concurrent 5
```

### Enable real-time monitoring

```bash
python webscraper_crawl4ai.py https://example.com --enable-monitor
```

## Output

The application displays results grouped by crawl depth, showing the total number of pages crawled and example URLs at each depth level.

When the `--save-markdown` option is enabled, the application will generate and save markdown content for each crawled URL:

- With no content filter: Only raw markdown is generated
- With a content filter: Only filtered markdown is generated

### Markdown Generation

The application supports four approaches to markdown generation:

#### Default Markdown Generation

When using `--save-markdown` without specifying a content filter, the DefaultMarkdownGenerator converts HTML content to markdown without any filtering. This preserves most of the original content and structure of the page.

You can customize the output using various options like `--ignore-links`, `--body-width`, etc.

#### PruningContentFilter

The PruningContentFilter scores each HTML node based on text density, link density, and tag importance, discarding those below the specified threshold. This results in cleaner, more focused markdown output.

- **Pruning Threshold**: Controls how aggressively content is pruned (0.0-1.0). Lower values retain more content, higher values prune more aggressively.
- **Threshold Type**: 
  - `fixed`: Each node must exceed the threshold value
  - `dynamic`: Node scoring adjusts according to tag type, text/link density, etc.
- **Min Word Threshold**: Blocks with fewer words than this value are pruned

#### BM25ContentFilter

The BM25ContentFilter uses the BM25 ranking algorithm (similar to what search engines use) to identify which text chunks best match a specified query. This is especially useful when you have a specific topic or question in mind.

- **User Query**: The search query to focus on (e.g., "machine learning" or "food nutrition")
- **BM25 Threshold**: Higher values keep fewer chunks but more relevant ones; lower values are more inclusive
- **Stemming**: When enabled, variations of words match (e.g., "learn," "learning," "learnt")

#### LLMContentFilter

The LLMContentFilter leverages large language models to intelligently filter and extract relevant content while preserving the original meaning and structure. This provides high-quality markdown generation with customizable instructions.

- **LLM Provider**: The LLM provider and model to use (e.g., "openai/gpt-4o")
- **API Token**: Your API token for the LLM provider (can also be set via environment variables)
- **Instruction**: Custom instructions to guide the LLM in filtering content
- **Chunk Token Threshold**: Controls how content is processed in chunks (smaller values enable parallel processing)
- **Verbose Mode**: Provides detailed output during the filtering process

## Using Environment Variables for LLM API Tokens

Instead of passing your API token directly through the command line (which might expose it in your command history), you can set it as an environment variable. The application will automatically use the appropriate environment variable based on your selected LLM provider.

### Supported Environment Variables

| Provider | Environment Variable |
|----------|----------------------|
| openai   | OPENAI_API_KEY       |
| groq     | GROQ_API_KEY         |
| anthropic| ANTHROPIC_API_KEY    |
| gemini   | GEMINI_API_KEY       |
| deepseek | DEEPSEEK_API_KEY     |

### Setting Environment Variables

#### Windows (Command Prompt)
```cmd
set OPENAI_API_KEY=your-api-token-here
```

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY = "your-api-token-here"
```

#### Linux/macOS
```bash
export OPENAI_API_KEY=your-api-token-here
```

### Example Usage with Environment Variables

```bash
# First set the environment variable
export OPENAI_API_KEY=your-openai-api-key

# Then run the command without --llm-api-token
python webscraper_crawl4ai.py https://example.com \
    --content-filter llm \
    --llm-provider "openai/gpt-4o" \
    --save-markdown
```

## Important Notes

- When using `--save-markdown` without a content filter, only raw markdown is generated
- When using `--save-markdown` with a content filter, only filtered markdown is generated
- Markdown generator options (like `--ignore-links`) work with or without content filters
- When using the LLM filter, you need to provide an API token either via the `--llm-api-token` argument or through environment variables

## Advanced Features

### Rate Limiting

The Rate Limiter helps manage the pace of requests to avoid overloading servers or getting blocked due to rate limits.

- **Base Delay**: Random delay between consecutive requests to the same domain
- **Max Delay**: Maximum allowable delay when rate-limiting errors occur
- **Max Retries**: Maximum number of retries if rate-limiting errors occur
- **Rate Limit Codes**: HTTP status codes that trigger the rate-limiting logic (default: 429, 503)

When servers return rate-limit responses, the delay increases exponentially with jitter, up to the max delay.

### Dispatcher Types

#### Memory Adaptive Dispatcher

Automatically manages concurrency based on system memory usage:

- **Memory Threshold**: Pauses crawling if system memory exceeds this percentage
- **Check Interval**: How often to check memory usage (in seconds)
- **Max Concurrent**: Maximum number of concurrent crawling tasks allowed

#### Semaphore Dispatcher

Provides simple concurrency control with a fixed limit:

- **Max Concurrent**: Maximum number of concurrent crawling tasks allowed

### Streaming Mode

Enables processing results as soon as they're available, rather than waiting for all crawling to complete:

- Process each result immediately as it's crawled
- Save markdown files in real-time
- Useful for real-time analytics or progressive data storage
- Particularly valuable for large crawls where you want to start processing data immediately

### Monitoring

The Crawler Monitor provides real-time visibility into crawling operations:

- **Enable Monitor**: Enable real-time monitoring of crawling progress

### Cache Modes

Control how the crawler handles caching:

- **Enabled**: Use cached responses when available
- **Bypass**: Always make fresh requests
- **Refresh**: Validate cached responses with the server
