# Changelog

## [1.1.0] - 2025-10-25 - Improved Selenium Reliability

### Fixed
- **Generate Button Detection**: Implemented multiple fallback selectors to handle different page structures
  - Try 8 different button selectors (XPath and CSS)
  - JavaScript click fallback if normal click fails
  - Better error messages with debug information
  
- **Prompt Input Detection**: Added multiple input field selectors
  - Try 7 different input/textarea selectors
  - Handle case-insensitive placeholders
  - Improved retry logic

- **Stale Element References**: Elements now refetched inside retry functions
  - Fixed original stale element error
  - More robust element interaction

### Added
- Debug logging for button detection
- Lists all available buttons when detection fails
- Better error messages for troubleshooting

### Changed
- Button detection timeout reduced to 5 seconds per selector (from 15)
- Faster failover between different selectors
- Total retry attempts increased with multiple selectors

## [1.0.0] - 2025-10-25 - Initial Release

### Added
- Flask REST API server
- Two model endpoints: Image 4.0 and Nano Banana
- Selenium-based Dreamina automation
- Cookie-based authentication
- Docker deployment configuration
- Render deployment support
- Comprehensive documentation

### Supported Endpoints
- `GET /api/generate/image` - Default model (Image 4.0)
- `GET /api/generate/image-4.0` - Image 4.0 model
- `GET /api/generate/nano-banana` - Nano Banana model
- `GET /api/health` - Health check
- `GET /` - API information

### Known Limitations
- Browser automation doesn't honor aspect_ratio, quality parameters yet
- Requires Chrome/Chromium
- Slower than direct API calls
- Cookie sessions may expire
