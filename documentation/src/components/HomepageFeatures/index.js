import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Multi-Factor Authentication',
    description: (
      <>
        Implement state-of-the-art authentication methods including TOTP, backup codes, and more. 
        Fully customizable to meet your security requirements.
      </>
    ),
  },
  {
    title: 'Advanced Role-Based Access Control',
    description: (
      <>
        Manage permissions with a hierarchical role system. Create fine-grained access controls
        with role inheritance and dynamic permission assignment.
      </>
    ),
  },
  {
    title: 'Attribute-Based Access Control',
    description: (
      <>
        Go beyond RBAC with context-aware authorization. Define complex policies based on 
        user attributes, resource properties, and environmental conditions.
      </>
    ),
  },
  {
    title: 'Comprehensive Audit Logging',
    description: (
      <>
        Track all security-relevant events across your system. Capture detailed audit logs
        for compliance requirements and security investigations.
      </>
    ),
  },
  {
    title: 'Enterprise Monitoring',
    description: (
      <>
        Monitor system health, performance, and security metrics in real-time. Set alerts
        for suspicious activities and maintain visibility across your deployment.
      </>
    ),
  },
  {
    title: 'High Availability & Scalability',
    description: (
      <>
        Deploy with confidence using containerized architecture designed for horizontal scaling.
        Implement high-availability patterns for mission-critical workloads.
      </>
    ),
  },
];

const BusinessValueList = [
  {
    title: 'For Security Teams',
    description: (
      <>
        Reduce breach risk with comprehensive protection against unauthorized access. 
        Gain complete visibility with security analytics and automate policy enforcement.
      </>
    ),
  },
  {
    title: 'For IT Operations',
    description: (
      <>
        Reduce helpdesk burden with self-service capabilities. Simplify administration with
        intuitive interfaces and optimize authentication flows for better performance.
      </>
    ),
  },
  {
    title: 'For Compliance Officers',
    description: (
      <>
        Streamline audits with ready-made reports and comprehensive logs. Demonstrate compliance
        with evidence of security controls and prevent violations with proactive enforcement.
      </>
    ),
  },
];

const MarketSolutionsList = [
  {
    title: 'Security-Compliance Balance',
    description: (
      <>
        Balance strong security without sacrificing usability. Granular controls with intuitive interfaces,
        automated compliance, and contextual security that adapts to threat levels.
      </>
    ),
  },
  {
    title: 'Multi-environment Identity',
    description: (
      <>
        Unified identity governance across cloud, on-premises, and hybrid environments.
        Consistent policy enforcement and centralized visibility regardless of resource location.
      </>
    ),
  },
  {
    title: 'Modern Threat Protection',
    description: (
      <>
        Defense against sophisticated attacks with behavioral analysis, continuous authentication,
        and proactive threat mitigation with security intelligence integration.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section>
      <div className={styles.features}>
        <div className="container">
          <h2 className="text--center">Key Features</h2>
          <div className="row">
            {FeatureList.map((props, idx) => (
              <Feature key={idx} {...props} />
            ))}
          </div>
        </div>
      </div>
      
      <div className={styles.section}>
        <div className="container">
          <h2 className="text--center margin-top--xl">Market Problems Solved</h2>
          <div className="row">
            {MarketSolutionsList.map((props, idx) => (
              <Feature key={idx} {...props} />
            ))}
          </div>
        </div>
      </div>
      
      <div className={styles.section}>
        <div className="container">
          <h2 className="text--center margin-top--xl">Business Value</h2>
          <div className="row">
            {BusinessValueList.map((props, idx) => (
              <Feature key={idx} {...props} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
} 