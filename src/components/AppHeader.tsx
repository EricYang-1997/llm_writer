// src/components/AppHeader.tsx

import React, { useState, useEffect, useRef } from "react";
import { Input, Menu, message, ConfigProvider } from "antd";
import { AppstoreOutlined } from "@ant-design/icons";
import styles from "./AppHeader.module.css";

const { Search } = Input;
interface AppHeaderProps {
  onLogoClick?: () => void;
}
const AppHeader: React.FC<AppHeaderProps> = ({ onLogoClick }) => {
  const [searchValue, setSearchValue] = useState("");
  const [current, setCurrent] = useState(["mail"]);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const items = [
    {
      key: "mail",
      label: "图谱",
    },
    {
      key: "app",
      label: "Navigation Two",
    },
    {
      key: "sub1",
      label: "Navigation Three - Submenu",
      children: [
        {
          type: "group",
          label: "Item 1",
          children: [
            { label: "Option 1", key: "setting:1" },
            { label: "Option 2", key: "setting:2" },
          ],
        },
        {
          type: "group",
          label: "Item 2",
          children: [
            { label: "Option 3", key: "setting:3" },
            { label: "Option 4", key: "setting:4" },
          ],
        },
      ],
    },
    {
      key: "alipay",
      label: (
        <a href="https://ant.design" target="_blank" rel="noopener noreferrer">
          Navigation Four - Link
        </a>
      ),
    },
  ];

  const onSearch = (value: string) => {
    console.log("搜索:", value);
    message.info(`搜索: ${value}`);
  };

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === "logout") {
      message.success("已退出登录");
    }
  };

  // Ctrl+K / Cmd+K 快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <header className={styles.appLayoutHeader}>
      <div className={styles.headerContainer}>
        {/* 左侧 */}
        <div className={styles.headerLeft}>
          <img
            src="public/1.png"
            alt="logo"
            className={styles.logoIcon}
            onClick={onLogoClick}
            style={{ width: "64px", height: "64px" }} // 可选：设置图标大小
          />{" "}
          <span className={styles.appName}>EricYang</span>
          <Search
            placeholder="搜索...（Ctrl+K）"
            onSearch={onSearch}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className={styles.searchInput}
            ref={searchInputRef}
          />
        </div>

        {/* 右侧 */}
        <div className={styles.headerBottom}>
          <ConfigProvider
            theme={{
              components: {
                Menu: {
                  // 所有背景设为透明
                  itemBg: "transparent",
                  itemHoverBg: "transparent",
                  horizontalItemHoverBg: "transparent",
                  horizontalItemHoverColor: "transparent",
                  itemActiveBg: "transparent",
                  horizontalItemSelectedBg: "transparent",
                  subMenuItemBg: "transparent",

                  // 可选：微调文字颜色（保持默认也可以）
                  itemColor: "#777",
                  itemHoverColor: "#777",
                },
              },
            }}
          >
            <Menu
              mode="horizontal"
              selectedKeys={current}
              onSelect={({ selectedKeys }) =>
                setCurrent(selectedKeys as string[])
              }
              onClick={handleMenuClick}
              items={items}
            />
          </ConfigProvider>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
