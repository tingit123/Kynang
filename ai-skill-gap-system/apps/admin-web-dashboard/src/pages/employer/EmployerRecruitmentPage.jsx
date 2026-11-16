import React, {useEffect,useRef} from 'react';
import '../../recruitment-statuses.js';
import '../../skill-options.js';
import '../../employer-quick-hire.js';
import '../../employer-pipeline.js';
import '../../employer-evidence.js';
export default function EmployerRecruitmentPage(){const root=useRef(null);useEffect(()=>window.SkillGapEvidence.mount(root.current,null,'quick'),[]);return <div ref={root}/>;}
