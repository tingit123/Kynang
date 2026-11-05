import React, {useEffect, useRef} from 'react';
import '../../recruitment-statuses.js';
import '../../worker-notifications.js';
export default function NotificationsPage(){
  const root=useRef(null);
  useEffect(()=>window.SkillGapWorkerNotifications.mount(root.current),[]);
  return <div ref={root} />;
}
