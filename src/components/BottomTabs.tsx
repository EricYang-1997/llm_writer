// src/components/BottomTabs.tsx
import React, { useState } from 'react';
import { Tabs } from "antd";
import type { TabsProps } from "antd";
import Markdown from './markdown/Markdown'; 
import NodeCreator from './nodecreator/NodeCreator'
const BottomTabs: React.FC = () => {

  const items: TabsProps["items"] = [
    {
      key: "1",
      label: "编辑节点",
      children: (
        <div style={{ padding: "16px", maxHeight: '600px', overflowY: 'auto' }}>
          <NodeCreator />
        </div>
      ),
    },
    {
      key: "2",
      label: "内容预览",
      children: (
        <div style={{ padding: "16px", maxHeight: '600px', overflowY: 'auto' }}>
          <Markdown />
        </div>
      ),
    },
    {
      key: "3",
      label: "控制台",
      children: (
        <div style={{ padding: "16px" }}>
          <h3>Event Logs</h3>
          <p>Recent activity logs...</p>
        </div>
      ),
    },
  ];

 return (
    <Tabs
    defaultActiveKey="1"
    items={items}
    tabBarStyle={{margin:0}}
    type="card"
  />
  );
};

export default BottomTabs;
