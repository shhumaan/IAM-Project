# AzureShield IAM Documentation

This directory contains the documentation website for the AzureShield IAM platform, built with [Docusaurus](https://docusaurus.io/).

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Navigate to the documentation directory
cd documentation

# Install dependencies
npm install
```

### Local Development

```bash
# Start the development server
npm run start
```

This will start a local development server and open up a browser window. Most changes are reflected live without having to restart the server.

### Build

```bash
# Build the static site
npm run build
```

This command generates static content into the `build` directory that can be served by any static hosting service.

### Deployment

The documentation site can be deployed to any static site hosting service. For GitHub Pages, you can use:

```bash
# Deploy to GitHub Pages
npm run deploy
```

## Documentation Structure

- `/docs/` - Contains all the Markdown files for the documentation
  - `/docs/intro.md` - Main introduction page
  - `/docs/installation/` - Installation guides
  - `/docs/architecture/` - Architecture documentation
  - `/docs/api/` - API documentation
  - `/docs/troubleshooting.md` - Troubleshooting guide

- `/src/` - Contains React components for custom pages
  - `/src/pages/` - Custom React pages
  - `/src/components/` - Reusable React components

- `/static/` - Contains static assets like images
  - `/static/img/` - Image files

## Adding New Content

### Adding a New Document

1. Create a new `.md` file in the appropriate `/docs/` subdirectory
2. Add front matter at the top of the file:
   ```md
   ---
   sidebar_position: 2
   ---

   # Document Title

   Content goes here...
   ```
3. Add the document to the appropriate sidebar by updating `sidebars.js`

### Adding Images

1. Add the image file to `/static/img/`
2. Reference the image in your Markdown file:
   ```md
   ![Alt Text](/img/your-image.png)
   ```

## Contributing

We welcome contributions to improve the documentation. Please follow these steps:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Submit a pull request

## License

This documentation is licensed under the same license as the AzureShield IAM project. 