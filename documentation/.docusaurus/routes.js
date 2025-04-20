import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'a4a'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '529'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '088'),
            routes: [
              {
                path: '/docs/about',
                component: ComponentCreator('/docs/about', '97c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/',
                component: ComponentCreator('/docs/api/', '5e5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/abac',
                component: ComponentCreator('/docs/api/abac', 'dcc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/audit',
                component: ComponentCreator('/docs/api/audit', '984'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/authentication',
                component: ComponentCreator('/docs/api/authentication', '733'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/authorization',
                component: ComponentCreator('/docs/api/authorization', '13c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/mfa',
                component: ComponentCreator('/docs/api/mfa', 'be4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/monitoring',
                component: ComponentCreator('/docs/api/monitoring', '826'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/permissions',
                component: ComponentCreator('/docs/api/permissions', 'bd4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/policies',
                component: ComponentCreator('/docs/api/policies', '8b7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/rbac',
                component: ComponentCreator('/docs/api/rbac', '337'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/roles',
                component: ComponentCreator('/docs/api/roles', 'ba5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/users',
                component: ComponentCreator('/docs/api/users', '31c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/',
                component: ComponentCreator('/docs/architecture/', '178'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/installation/',
                component: ComponentCreator('/docs/installation/', 'dbe'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/installation/docker-deployment',
                component: ComponentCreator('/docs/installation/docker-deployment', '4e8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/installation/local-development',
                component: ComponentCreator('/docs/installation/local-development', '58c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/installation/production-deployment',
                component: ComponentCreator('/docs/installation/production-deployment', 'c7d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/troubleshooting',
                component: ComponentCreator('/docs/troubleshooting', 'e02'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
