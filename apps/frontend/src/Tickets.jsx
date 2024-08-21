import { List, Button, Flex, Typography } from "antd";

const { Title } = Typography;

export default function Tickets() {
    return (
        <>
            <Title level={3}>Ваши билеты</Title>
            <List
                itemLayout="horizontal"
                dataSource={[{}, {}]}
                renderItem={(item, index) => (
                <List.Item>
                    <List.Item.Meta
                        title="Ростов — Москва"
                        description={<Flex vertical>
                            <div>Поезд 012с Ростов Главный - Москва Каз отправление 11:20</div>
                            <Button style={{margin: "5px 0"}}>Скачать билеты</Button>
                        </Flex>}
                    />
                </List.Item>
                )}
            />
        </>
    );
}