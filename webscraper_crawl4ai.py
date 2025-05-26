#!/usr/bin/env python3

import asyncio
import argparse
import sys
import traceback
import os
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    BFSDeepCrawlStrategy,
    CrawlResult,
    FilterChain,
    DomainFilter,
    URLPatternFilter,
    ContentTypeFilter,
    LLMConfig,
    CacheMode,
    RateLimiter,
    CrawlerMonitor,
)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher, SemaphoreDispatcher
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter, LLMContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


def get_filename_from_url(url):
    """Extract a meaningful filename from a URL.
    
    For example, https://console.groq.com/docs/libraries -> docs_libraries
    """
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the path and remove trailing slash if present
    path = parsed_url.path.rstrip('/')
    
    # Extract the last part of the path and its parent
    if path and '/' in path:
        path_parts = path.split('/')
        # Get the last component
        last_part = path_parts[-1]
        # Get the parent path component if available
        parent_part = path_parts[-2] if len(path_parts) >= 2 else ''
        
        # Combine parent and last part if parent exists
        if parent_part:
            filename = f"{parent_part}_{last_part}"
        else:
            filename = last_part
    elif path:
        filename = path
    else:
        # If no path or empty path, use the domain name
        filename = parsed_url.netloc.split('.')[-2]  # e.g., 'example' from 'example.com'
    
    # Clean the filename - remove any query parameters or fragments
    filename = re.sub(r'[\?#].*$', '', filename)
    
    # If filename is empty (e.g., for root URLs like https://example.com/), use 'index'
    if not filename:
        filename = 'index'
    
    # Ensure the filename is valid
    filename = re.sub(r'[^\w\-\.]', '_', filename)
    
    return filename


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Crawl4AI Deep Crawler Application")
    parser.add_argument("url", type=str, help="Starting URL for the crawl")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum depth to crawl (default: 2)")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to crawl")
    parser.add_argument("--include-external", action="store_true", help="Follow links to external domains")
    parser.add_argument("--verbose", action="store_true", help="Display verbose output")
    parser.add_argument("--url-patterns", type=str, nargs="*", help="URL patterns to include")
    parser.add_argument("--allowed-domains", type=str, nargs="*", help="Domains to allow")
    parser.add_argument("--blocked-domains", type=str, nargs="*", help="Domains to block")
    parser.add_argument("--allowed-content-types", type=str, nargs="*", help="Content types to allow")
    
    # Content filter type selection - optional
    parser.add_argument("--content-filter", type=str, choices=["pruning", "bm25", "llm"], 
                        help="Content filter type to use (optional)")
    
    # Pruning filter parameters
    parser.add_argument("--pruning-threshold", type=float, default=0.45, 
                        help="Threshold for content pruning (default: 0.45)")
    parser.add_argument("--threshold-type", type=str, default="dynamic", choices=["fixed", "dynamic"], 
                        help="Threshold type for content pruning (default: dynamic)")
    parser.add_argument("--min-word-threshold", type=int, default=5, 
                        help="Minimum word threshold for content pruning (default: 5)")
    
    # BM25 filter parameters
    parser.add_argument("--user-query", type=str, 
                        help="Search query for BM25 content filtering")
    parser.add_argument("--bm25-threshold", type=float, default=1.2, 
                        help="BM25 score threshold (default: 1.2)")
    parser.add_argument("--use-stemming", action="store_true", 
                        help="Enable word stemming for BM25 filtering")
    
    # LLM filter parameters
    parser.add_argument("--llm-provider", type=str, default="openai/gpt-4o", 
                        help="LLM provider for content filtering (default: openai/gpt-4o)")
    parser.add_argument("--llm-api-token", type=str, 
                        help="API token for LLM provider (if not set, will use environment variables like OPENAI_API_KEY, GROQ_API_KEY, etc. based on provider)")
    parser.add_argument("--llm-instruction", type=str, 
                        default="Extract the main content while preserving its original wording and substance. "
                                "Remove navigation elements, sidebars, footers, and ads. "
                                "Format the output as clean markdown with proper code blocks and headers.",
                        help="Custom instruction for LLM content filtering")
    parser.add_argument("--chunk-token-threshold", type=int, default=4096, 
                        help="Token threshold for chunk processing in LLM filtering (default: 4096)")
    parser.add_argument("--llm-verbose", action="store_true", 
                        help="Enable verbose output for LLM content filtering")
    
    # Markdown generator options
    parser.add_argument("--ignore-links", action="store_true", 
                        help="Remove all hyperlinks in the markdown output")
    parser.add_argument("--ignore-images", action="store_true", 
                        help="Remove all image references in the markdown output")
    parser.add_argument("--escape-html", action="store_true", 
                        help="Turn HTML entities into text")
    parser.add_argument("--body-width", type=int, default=0, 
                        help="Wrap text at N characters (0 means no wrapping)")
    parser.add_argument("--skip-internal-links", action="store_true", 
                        help="Omit local anchors or internal links referencing the same page")
    
    # Output parameters
    parser.add_argument("--save-markdown", action="store_true", 
                        help="Save markdown content for each URL")
    parser.add_argument("--output-dir", type=str, default="./output", 
                        help="Directory to save markdown files (default: ./output)")
    
    # Rate limiter parameters
    parser.add_argument("--enable-rate-limiter", action="store_true",
                        help="Enable rate limiting for requests")
    parser.add_argument("--base-delay", type=float, nargs=2, default=[1.0, 3.0],
                        help="Base delay range in seconds between requests (default: 1.0 3.0)")
    parser.add_argument("--max-delay", type=float, default=60.0,
                        help="Maximum delay in seconds for rate limiting (default: 60.0)")
    parser.add_argument("--max-retries", type=int, default=3,
                        help="Maximum number of retries for rate-limited requests (default: 3)")
    
    # Memory adaptive dispatcher parameters
    parser.add_argument("--dispatcher", type=str, choices=["memory", "semaphore"], default="memory",
                        help="Type of dispatcher to use (default: memory)")
    parser.add_argument("--memory-threshold", type=float, default=90.0,
                        help="Memory threshold percentage for adaptive dispatcher (default: 90.0)")
    parser.add_argument("--check-interval", type=float, default=1.0,
                        help="Memory check interval in seconds (default: 1.0)")
    parser.add_argument("--max-concurrent", type=int, default=10,
                        help="Maximum concurrent tasks/sessions (default: 10)")
    
    # Streaming mode
    parser.add_argument("--stream", action="store_true",
                        help="Enable streaming mode to process results as they become available")
    
    # Monitor parameters
    parser.add_argument("--enable-monitor", action="store_true",
                        help="Enable real-time monitoring of crawling progress")
    
    # Cache mode
    parser.add_argument("--cache-mode", type=str, choices=["enabled", "bypass", "refresh"], default="bypass",
                        help="Cache mode for requests (default: bypass)")
    
    args = parser.parse_args()
    
    try:
        # Build filters if specified
        filters = []
        
        if args.url_patterns:
            filters.append(URLPatternFilter(patterns=args.url_patterns))
        
        if args.allowed_domains or args.blocked_domains:
            filters.append(DomainFilter(
                allowed_domains=args.allowed_domains or [],
                blocked_domains=args.blocked_domains or []
            ))
        
        if args.allowed_content_types:
            filters.append(ContentTypeFilter(allowed_types=args.allowed_content_types))
        
        # Create filter chain - ALWAYS create a filter chain even if empty
        # This prevents the 'NoneType' has no attribute 'apply' error
        filter_chain = FilterChain(filters=filters)
        
        # Create the deep crawl strategy
        strategy = BFSDeepCrawlStrategy(
            max_depth=args.max_depth,
            include_external=args.include_external,
            filter_chain=filter_chain  # Always provide a filter chain
        )
        
        # Set max_pages separately if specified
        if args.max_pages is not None:
            strategy.max_pages = args.max_pages
        
        # Create markdown generator options dictionary
        markdown_options = {}
        if args.ignore_links:
            markdown_options["ignore_links"] = True
        if args.ignore_images:
            markdown_options["ignore_images"] = True
        if args.escape_html:
            markdown_options["escape_html"] = True
        if args.body_width > 0:
            markdown_options["body_width"] = args.body_width
        if args.skip_internal_links:
            markdown_options["skip_internal_links"] = True
        
        # Create content filter based on user selection
        content_filter = None
        if args.content_filter == "pruning":
            content_filter = PruningContentFilter(
                threshold=args.pruning_threshold,
                threshold_type=args.threshold_type,
                min_word_threshold=args.min_word_threshold
            )
            print(f"Using PruningContentFilter with threshold={args.pruning_threshold}, "
                  f"type={args.threshold_type}, min_words={args.min_word_threshold}")
        elif args.content_filter == "bm25":
            if not args.user_query:
                print("WARNING: No user query provided for BM25 filter. "
                      "The filter will attempt to extract context from page metadata.")
            
            content_filter = BM25ContentFilter(
                user_query=args.user_query,
                bm25_threshold=args.bm25_threshold,
                use_stemming=args.use_stemming
            )
            print(f"Using BM25ContentFilter with query='{args.user_query or 'None'}', "
                  f"threshold={args.bm25_threshold}, stemming={'enabled' if args.use_stemming else 'disabled'}")
        elif args.content_filter == "llm":
            # Create LLM configuration
            llm_config = LLMConfig(
                provider=args.llm_provider,
                api_token=args.llm_api_token
            )
            
            content_filter = LLMContentFilter(
                llm_config=llm_config,
                instruction=args.llm_instruction,
                chunk_token_threshold=args.chunk_token_threshold,
                verbose=args.llm_verbose
            )
            print(f"Using LLMContentFilter with provider={args.llm_provider}, "
                  f"chunk_token_threshold={args.chunk_token_threshold}")
            print(f"LLM Instruction: {args.llm_instruction}")
            
            # Indicate token source
            if args.llm_api_token:
                print("Using API token provided via command line argument")
            else:
                provider_prefix = args.llm_provider.split('/')[0].upper()
                env_var_name = f"{provider_prefix}_API_KEY"
                print(f"Using API token from environment variable {env_var_name} (if available)")
        
        # Create DefaultMarkdownGenerator with or without content filter
        md_generator = DefaultMarkdownGenerator(
            content_filter=content_filter,
            options=markdown_options
        )
        
        if args.save_markdown:
            if args.content_filter:
                print(f"Markdown will be generated with {args.content_filter} content filter")
            else:
                print("Markdown will be generated with DefaultMarkdownGenerator (no content filter)")
                if len(markdown_options) > 0:
                    print(f"Using markdown options: {markdown_options}")
        
        # Configure the crawler
        config = CrawlerRunConfig(
            deep_crawl_strategy=strategy,
            verbose=args.verbose,
            markdown_generator=md_generator if args.save_markdown else None,
            stream=args.stream,
            cache_mode=getattr(CacheMode, args.cache_mode.upper())
        )
        
        # Create rate limiter if enabled
        rate_limiter = None
        if args.enable_rate_limiter:
            rate_limiter = RateLimiter(
                base_delay=tuple(args.base_delay),
                max_delay=args.max_delay,
                max_retries=args.max_retries
            )
            print(f"Rate limiter enabled with base_delay={tuple(args.base_delay)}, "
                  f"max_delay={args.max_delay}, max_retries={args.max_retries}")
        
        # Create monitor if enabled
        monitor = None
        if args.enable_monitor:
            monitor = CrawlerMonitor()
            print(f"Monitor enabled")
        
        # Create dispatcher based on user selection
        dispatcher = None
        if args.dispatcher == "memory":
            dispatcher = MemoryAdaptiveDispatcher(
                memory_threshold_percent=args.memory_threshold,
                check_interval=args.check_interval,
                max_session_permit=args.max_concurrent,
                rate_limiter=rate_limiter,
                monitor=monitor
            )
            print(f"Using MemoryAdaptiveDispatcher with memory_threshold={args.memory_threshold}%, "
                  f"max_concurrent={args.max_concurrent}")
        else:  # semaphore
            dispatcher = SemaphoreDispatcher(
                max_session_permit=args.max_concurrent,
                rate_limiter=rate_limiter,
                monitor=monitor
            )
            print(f"Using SemaphoreDispatcher with max_concurrent={args.max_concurrent}")
        
        # Run the crawler
        async with AsyncWebCrawler() as crawler:
            if args.stream:
                # Streaming mode - process results as they become available
                print("\n===== STREAMING MODE ENABLED =====\n")
                print("Processing results as they become available...\n")
                
                # Create output directory if saving markdown and it doesn't exist
                if args.save_markdown:
                    os.makedirs(args.output_dir, exist_ok=True)
                
                # Initialize counters
                total_pages = 0
                markdown_count = 0
                pages_by_depth = {}
                
                # Process results as they arrive
                async for result in await crawler.arun(args.url, config=config, dispatcher=dispatcher):
                    total_pages += 1
                    
                    # Update depth statistics
                    depth = result.metadata.get("depth", 0)
                    if depth not in pages_by_depth:
                        pages_by_depth[depth] = []
                    pages_by_depth[depth].append(result.url)
                    
                    # Display progress
                    print(f"Processed page {total_pages}: {result.url} (depth {depth})")
                    
                    # Save markdown if requested
                    if args.save_markdown and result.success and hasattr(result, 'markdown') and result.markdown:
                        # Get a meaningful filename from the URL
                        filename = get_filename_from_url(result.url)
                        
                        # If content filter is used, only save fit_markdown
                        if args.content_filter and hasattr(result.markdown, 'fit_markdown'):
                            # Get markdown content
                            md_content = f"# {result.url}\n\n{result.markdown.fit_markdown or ''}"
                            
                            # Save filtered markdown
                            md_path = os.path.join(args.output_dir, f"{filename}.md")
                            with open(md_path, 'w', encoding='utf-8') as f:
                                f.write(md_content)
                            
                            print(f"  → Saved filtered markdown for {result.url} as {filename}.md")
                        else:
                            # Get markdown content
                            md_content = f"# {result.url}\n\n{result.markdown.raw_markdown or ''}"
                            
                            # Save raw markdown
                            raw_md_path = os.path.join(args.output_dir, f"{filename}.md")
                            with open(raw_md_path, 'w', encoding='utf-8') as f:
                                f.write(md_content)
                            
                            print(f"  → Saved markdown for {result.url} as {filename}.md")
                        
                        markdown_count += 1
                
                # Display final results
                print(f"\n===== CRAWL RESULTS =====\n")
                print(f"Total pages crawled: {total_pages}")
                
                # Display crawl structure by depth
                for depth, urls in sorted(pages_by_depth.items()):
                    print(f"\nDepth {depth}: {len(urls)} pages")
                    # Show first 5 URLs for each depth as examples
                    for url in urls[:5]:
                        print(f"  → {url}")
                    if len(urls) > 5:
                        print(f"  ... and {len(urls) - 5} more")
                
                if args.save_markdown and markdown_count > 0:
                    print(f"\nMarkdown files saved to: {os.path.abspath(args.output_dir)}")
                elif args.save_markdown:
                    print("\nNo markdown content was generated for any of the crawled pages.")
            else:
                # Batch mode - get all results at once
                results = await crawler.arun(args.url, config=config, dispatcher=dispatcher)
                
                # Display results
                print(f"\n===== CRAWL RESULTS =====\n")
                print(f"Total pages crawled: {len(results)}")
                
                # Group results by depth
                pages_by_depth = {}
                for result in results:
                    depth = result.metadata.get("depth", 0)
                    if depth not in pages_by_depth:
                        pages_by_depth[depth] = []
                    pages_by_depth[depth].append(result.url)
                
                # Display crawl structure by depth
                for depth, urls in sorted(pages_by_depth.items()):
                    print(f"\nDepth {depth}: {len(urls)} pages")
                    # Show first 5 URLs for each depth as examples
                    for url in urls[:5]:
                        print(f"  → {url}")
                    if len(urls) > 5:
                        print(f"  ... and {len(urls) - 5} more")
                
                # Save markdown content if requested
                if args.save_markdown:
                    # Create output directory if it doesn't exist
                    os.makedirs(args.output_dir, exist_ok=True)
                    
                    print(f"\n===== SAVING MARKDOWN CONTENT =====\n")
                    markdown_count = 0
                    for i, result in enumerate(results):
                        if result.success and hasattr(result, 'markdown') and result.markdown:
                            # Get a meaningful filename from the URL
                            filename = get_filename_from_url(result.url)
                            
                            # If content filter is used, only save fit_markdown
                            if args.content_filter and hasattr(result.markdown, 'fit_markdown'):
                                # Get markdown content
                                md_content = f"# {result.url}\n\n{result.markdown.fit_markdown or ''}"
                                
                                # Save only fit markdown
                                md_path = os.path.join(args.output_dir, f"{filename}.md")
                                with open(md_path, 'w', encoding='utf-8') as f:
                                    f.write(md_content)
                                
                                print(f"  → Saved filtered markdown for {result.url} as {filename}.md")
                            else:
                                # Get markdown content
                                md_content = f"# {result.url}\n\n{result.markdown.raw_markdown or ''}"
                                
                                # Save raw markdown
                                raw_md_path = os.path.join(args.output_dir, f"{filename}.md")
                                with open(raw_md_path, 'w', encoding='utf-8') as f:
                                    f.write(md_content)
                                
                                print(f"  → Saved markdown for {result.url} as {filename}.md")
                            
                            markdown_count += 1
                    
                    if markdown_count > 0:
                        print(f"\nMarkdown files saved to: {os.path.abspath(args.output_dir)}")
                    else:
                        print("\nNo markdown content was generated for any of the crawled pages.")
    
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        print("\nTraceback:")
        traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    asyncio.run(main())
