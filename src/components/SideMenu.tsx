// src/components/SideMenu.tsx
import React from "react";
import {
  AppstoreOutlined,
  CalendarOutlined,
  MailOutlined,
  SettingOutlined,
  MenuFoldOutlined, // 折叠图标
  MenuUnfoldOutlined, // 展开图标
} from "@ant-design/icons";
import type { MenuProps } from "antd";
import { Menu } from "antd";

type MenuItem = Required<MenuProps>["items"][number];

// 将 items 定义为函数，接受 toggleSidebar 回调和当前折叠状态
const getItems = (toggleSidebar: () => void, collapsed: boolean): MenuItem[] => [
  {
    key: "1",
    icon: <MailOutlined />,
    label: "Navigation One",
  },
  {
    key: "2",
    icon: <CalendarOutlined />,
    label: "Navigation Two",
  },
  {
    key: "sub1",
    label: "Navigation Two",
    icon: <AppstoreOutlined />,
    children: [
      { key: "3", label: "Option 3" },
      { key: "4", label: "Option 4" },
      {
        key: "sub1-2",
        label: "Submenu",
        children: [
          { key: "5", label: "Option 5" },
          { key: "6", label: "Option 6" },
        ],
      },
    ],
  },
  {
    key: "sub2",
    label: "Navigation Three",
    icon: <SettingOutlined />,
    children: [
      { key: "7", label: "Option 7" },
      { key: "8", label: "Option 8" },
      { key: "9", label: "Option 9" },
      { key: "10", label: "Option 10" },
    ],
  },
  {
    key: "link",
    icon: collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />, // 根据状态显示不同图标
    label: collapsed ? "展开" : "折叠", // 根据折叠状态显示不同文字
    onClick: () => {
      toggleSidebar(); // 直接调用传入的回调函数
    },
  },
];

export interface SideMenuProps extends Omit<MenuProps, "items"> {
  collapsed?: boolean;
  onLogoClick: () => void; // 从 App.tsx 传入的回调函数
}

const SideMenu: React.FC<SideMenuProps> = ({
  collapsed = true,
  onLogoClick, // 接收回调函数
  defaultSelectedKeys = ["1"],
  defaultOpenKeys = [""],
  style,
  className,
  ...restProps
}) => {
  const items = getItems(onLogoClick, collapsed); // 将回调函数和折叠状态传递给 items

  return (
    <Menu
      className={className}
      style={{ width: collapsed ? 80 : 256, ...style }}
      defaultSelectedKeys={defaultSelectedKeys}
      defaultOpenKeys={defaultOpenKeys}
      theme="light"
      items={items}
      {...restProps}
      mode="inline"
      inlineCollapsed={collapsed}
    />
  );
};

export default SideMenu;