import { List, Button } from "antd";
import { useLoaderData } from "react-router-dom";
import { useWebApp } from "@vkruglikov/react-telegram-web-app";


export default function Notes() {
    const data = useLoaderData();
    const webapp = useWebApp();
    
    return (
        <List
            itemLayout="vertical"
            dataSource={data}
            renderItem={(item) => (
                <List.Item 
                    key={item.id} 
                    extra={[<Button onClick={() => webapp.switchInlineQuery(item.title)}>Открыть</Button>]}
                >
                    <List.Item.Meta title={item.title} description={"от " + item.author_name} />
                </List.Item>
            )}
        />
    )
}