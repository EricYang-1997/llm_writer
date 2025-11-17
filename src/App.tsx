// src/App.tsx
import React, { useState } from "react";
import "./App.css";
import AppHeader from "./components/AppHeader.tsx";
import SideMenu from "./components/SideMenu";
import CenterGraph from "./components/CenterGraph"; // 👈 新增导入
import { Splitter } from "antd";
import BottomTabs from "./components/BottomTabs"; // 👈 新增导入

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(true); // 👈 新增状态
  const [showIconMode] = useState<'auto' | boolean>(true);

  const toggleSidebar = () => {
    setCollapsed((prev) => {
      const next = !prev;
      return next;
    });
  };

  return (
    <div className="app">
      {/* Header */}
      <AppHeader onLogoClick={toggleSidebar} />

      {/* Content: Left + (Center + Bottom) */}
      <main className="app-content">
        <SideMenu collapsed={collapsed} mode="vertical" onLogoClick={toggleSidebar} />

        {/* Center + Bottom → Splitter */}
        <div className="splitter-container">
          <Splitter layout="vertical" style={{ height: "100%",width:"100%"}}>
            <Splitter.Panel defaultSize="100%" min="20%">
              {/* ✅ 放置 G6 中心图组件 */}
              <div
                style={{ height: "100%", width: "100%", overflow: "hidden" }}
              >
                <CenterGraph />
              </div>
            </Splitter.Panel>
            <Splitter.Panel defaultSize="0%" min="60%" collapsible={{ start: true, end: true, showCollapsibleIcon: showIconMode }}>
              <div
                style={{ height: "100%", width: "100%", overflow: "hidden"}}
              >
                <BottomTabs />
              </div>
            </Splitter.Panel>
          </Splitter>
        </div>
      </main>
    </div>
  );
};

export default App;
