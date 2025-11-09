#!/usr/bin/env node
/**
 * URL Cleaner - Node.js Implementation
 *
 * THE GOLDEN RULE: Never use regex to parse URLs!
 *
 * Node.js has native URL and URLSearchParams classes that are
 * designed specifically for this. They handle all edge cases correctly.
 */

const fs = require('fs');
const path = require('path');

/**
 * List of tracking/analytics parameters to remove
 */
const TRACKER_PARAMS = [
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_term',
    'utm_content',
    'utm_id',
    'fbclid',      // Facebook Click ID
    'gclid',       // Google Click ID
    'msclkid',     // Microsoft Click ID
    'mc_cid',      // Mailchimp Campaign ID
    'mc_eid',      // Mailchimp Email ID
    '_ga',         // Google Analytics
    '_gid',        // Google Analytics
    '_hsenc',      // HubSpot
    '_hsmi',       // HubSpot
    'mkt_tok',     // Marketo
    'ref',         // Generic referrer
    'source'       // Generic source
];

/**
 * Clean and normalize a URL using proper URL parsing (NO REGEX!)
 *
 * @param {string} urlString - The URL to clean
 * @param {object} options - Cleaning options
 * @returns {string} - Clean, normalized URL
 */
function cleanURL(urlString, options = {}) {
    const {
        removeTrackers = true,
        removeFragment = true,
        lowercaseHostname = true,
        removeWWW = true,
        removeTrailingSlash = true,
        sortQueryParams = true,
        removeDefaultPorts = true
    } = options;

    // Parse the URL using native URL class - THE CORRECT WAY
    const url = new URL(urlString);

    // Remove tracking parameters
    if (removeTrackers) {
        TRACKER_PARAMS.forEach(param => {
            url.searchParams.delete(param);
        });
    }

    // Sort query parameters alphabetically
    if (sortQueryParams) {
        const params = Array.from(url.searchParams.entries())
            .sort((a, b) => a[0].localeCompare(b[0]));

        url.search = '';
        params.forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
    }

    // Lowercase hostname
    if (lowercaseHostname) {
        url.hostname = url.hostname.toLowerCase();
    }

    // Remove www prefix
    if (removeWWW && url.hostname.startsWith('www.')) {
        url.hostname = url.hostname.substring(4);
    }

    // Remove default ports
    if (removeDefaultPorts) {
        if ((url.protocol === 'http:' && url.port === '80') ||
            (url.protocol === 'https:' && url.port === '443')) {
            url.port = '';
        }
    }

    // Remove trailing slash from pathname (but keep '/' for root)
    if (removeTrailingSlash && url.pathname.length > 1 && url.pathname.endsWith('/')) {
        url.pathname = url.pathname.slice(0, -1);
    }

    // Remove fragment
    if (removeFragment) {
        url.hash = '';
    }

    // Return the clean URL
    return url.href;
}

/**
 * Extract URL components without using regex
 *
 * @param {string} urlString - URL to analyze
 * @returns {object} - URL components
 */
function extractComponents(urlString) {
    const url = new URL(urlString);

    const pathSegments = url.pathname
        .split('/')
        .filter(segment => segment.length > 0);

    const queryParams = {};
    url.searchParams.forEach((value, key) => {
        if (!queryParams[key]) {
            queryParams[key] = [];
        }
        queryParams[key].push(value);
    });

    return {
        protocol: url.protocol.replace(':', ''),
        hostname: url.hostname,
        port: url.port || null,
        pathname: url.pathname,
        pathSegments: pathSegments,
        pathDepth: pathSegments.length,
        queryParams: queryParams,
        queryParamCount: url.searchParams.size,
        fragment: url.hash.replace('#', ''),
        hasQuery: url.search.length > 0,
        hasFragment: url.hash.length > 0,
        fullDomain: url.host
    };
}

/**
 * Get domain parts (subdomain, domain, TLD)
 *
 * @param {string} urlString - URL to analyze
 * @returns {object} - Domain parts
 */
function getDomainParts(urlString) {
    const url = new URL(urlString);
    const parts = url.hostname.split('.');

    let subdomain = '';
    let domain = '';
    let tld = '';

    if (parts.length >= 3) {
        // e.g., archives.hartford.edu -> {subdomain: 'archives', domain: 'hartford', tld: 'edu'}
        subdomain = parts.slice(0, -2).join('.');
        domain = parts[parts.length - 2];
        tld = parts[parts.length - 1];
    } else if (parts.length === 2) {
        // e.g., hartford.edu -> {subdomain: '', domain: 'hartford', tld: 'edu'}
        domain = parts[0];
        tld = parts[1];
    } else if (parts.length === 1) {
        domain = parts[0];
    }

    return { subdomain, domain, tld };
}

/**
 * Process JSONL file and clean all URLs
 *
 * @param {string} inputPath - Path to input JSONL file
 * @param {string} outputPath - Path to output JSONL file
 */
function processJSONL(inputPath, outputPath) {
    const input = fs.readFileSync(inputPath, 'utf8');
    const lines = input.split('\n').filter(line => line.trim());

    const results = lines.map(line => {
        const record = JSON.parse(line);

        // Clean the URL
        const cleanedURL = cleanURL(record.url);

        // Extract components
        const components = extractComponents(record.url);

        // Get domain parts
        const domainParts = getDomainParts(record.url);

        return {
            ...record,
            url_cleaned: cleanedURL,
            url_components: components,
            domain_parts: domainParts
        };
    });

    // Write results
    const outputLines = results.map(r => JSON.stringify(r)).join('\n');
    fs.writeFileSync(outputPath, outputLines + '\n');

    console.log(`✓ Processed ${results.length} URLs`);
    console.log(`✓ Output written to: ${outputPath}`);
}

/**
 * Demo: Show URL cleaning in action
 */
function demo() {
    console.log('='.repeat(80));
    console.log('URL CLEANING DEMO - Node.js (NO REGEX!)');
    console.log('='.repeat(80));

    const messyURL = "http://catalog.hartford.edu/preview_program.php?catoid=20&poid=4445&utm_source=facebook&fbclid=IwAR123#details";

    console.log(`\nOriginal messy URL:\n  ${messyURL}\n`);

    // Clean it
    const cleanedURL = cleanURL(messyURL);
    console.log(`Cleaned URL:\n  ${cleanedURL}\n`);

    // Extract components
    const components = extractComponents(messyURL);
    console.log('Extracted components:');
    console.log(JSON.stringify(components, null, 2));

    // Domain parts
    const domainParts = getDomainParts(messyURL);
    console.log('\nDomain parts:');
    console.log(JSON.stringify(domainParts, null, 2));

    console.log('\n' + '='.repeat(80));
    console.log('See? Native URL class handles everything. No regex needed!');
    console.log('='.repeat(80));
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args[0] === 'demo') {
        demo();
    } else if (args[0] === 'process' && args[1] && args[2]) {
        processJSONL(args[1], args[2]);
    } else {
        console.log('Usage:');
        console.log('  node url_cleaner.js demo');
        console.log('  node url_cleaner.js process <input.jsonl> <output.jsonl>');
    }
}

module.exports = { cleanURL, extractComponents, getDomainParts, processJSONL };
