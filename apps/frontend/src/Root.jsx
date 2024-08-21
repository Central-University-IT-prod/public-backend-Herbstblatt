import { Typography, Flex } from "antd";
import NavItem from "./NavItem";
import { Outlet, useLoaderData } from "react-router-dom";

const { Title } = Typography;

export default function Root() {
    const {name} = useLoaderData();
    return (
        <>
            <Title level={2}>{name}</Title>
            <Flex gap="small" style={{"overflow-x": "scroll", "marginBottom": "10px"}}>
                <NavItem path="route" name="Маршрут" />
                <NavItem path="notes" name="Заметки" />
            </Flex>
            <Outlet />
        </>
    );
}