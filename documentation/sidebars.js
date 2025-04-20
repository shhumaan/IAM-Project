/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'doc',
      id: 'about',
      label: 'About AzureShield IAM',
    },
    {
      type: 'category',
      label: 'Installation',
      link: {
        type: 'doc',
        id: 'installation/index',
      },
      items: [
        'installation/local-development',
        'installation/docker-deployment',
        'installation/production-deployment',
      ],
    },
    {
      type: 'doc',
      id: 'architecture/index',
      label: 'Architecture',
    },
    {
      type: 'doc',
      id: 'troubleshooting',
      label: 'Troubleshooting',
    },
    {
      type: 'category',
      label: 'API Reference',
      link: {
        type: 'doc',
        id: 'api/index',
      },
      items: [
        'api/authentication',
        'api/mfa',
        'api/authorization',
        'api/users',
        'api/roles',
        'api/permissions',
        'api/rbac',
        'api/abac',
        'api/policies',
        'api/audit',
        'api/monitoring',
      ],
    },
  ],
};

module.exports = sidebars; 