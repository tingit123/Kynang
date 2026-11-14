import React, { useEffect, useRef } from 'react';
import '../../recruitment-statuses.js';
import '../../skill-options.js';
import '../../employer-quick-hire.js';
import '../../employer-pipeline.js';
import '../../employer-evidence.js';

// Shared with the active nginx page; no duplicate matching or mock candidate data.
export default function EmployerCandidatesPage() {
  const container = useRef(null);
  useEffect(() => window.SkillGapEvidence.mount(container.current), []);
  return <div ref={container} />;
}
