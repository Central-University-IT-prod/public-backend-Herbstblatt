import {
    useThemeParams,
    WebAppProvider,
    useInitData,
    useCloudStorage
} from '@vkruglikov/react-telegram-web-app';
import { ConfigProvider, theme, Spin } from 'antd';
import useFetch from 'react-fetch-hook';

import App from './App.jsx';
import { useEffect } from 'react';


export default function WebAppWrapper() {
    const [colorScheme, themeParams] = useThemeParams();
    const [initDataUnsafe, initData] = useInitData();
    
    const {isLoading, data, error} = useFetch("/api/auth/sign-in", {
        method: 'POST',
        body: initData,
        formatter: (resp) => {
            if (resp.status !== 200) throw new Error();
            return resp.json();
        }
    });
  
    return (
      <WebAppProvider>
        <ConfigProvider
          theme={
            themeParams.text_color
              ? {
                  algorithm:
                    colorScheme === 'dark'
                      ? theme.darkAlgorithm
                      : theme.defaultAlgorithm,
                  token: {
                    colorText: themeParams.text_color,
                    colorPrimary: themeParams.button_color,
                    colorBgBase: themeParams.bg_color,
                  },
                }
              : undefined
          }
        >
            <Spin spinning={isLoading} fullscreen></Spin>
            {!isLoading && !error && <App token={data?.token} />}
            {error && "We're not letting you in"}
        </ConfigProvider>
      </WebAppProvider>
    );
  };