import '@ant-design/v5-patch-for-react-19';
import { createRoot } from "react-dom/client";
import { App as AntdApp, ConfigProvider } from "antd";
import "antd/dist/reset.css";
import "./index.css";
import App from "./App.tsx";

const rootElement = document.getElementById("root")!;
const root = createRoot(rootElement);

root.render(
  <ConfigProvider
    theme={{
      token: {
        borderRadiusLG: 0,
        borderRadius: 0,
        borderRadiusOuter: 0,
        colorPrimary: "#000000",
        colorBgContainer: '#ffffff',
        controlItemBgActive: "#f0f0f0",
        fontFamily: `"LXGW WenKai", system-ui, sans-serif`,
        motionUnit: 0.03,
      },
    }}
  >
    <AntdApp>
      <App />
    </AntdApp>
  </ConfigProvider>
);