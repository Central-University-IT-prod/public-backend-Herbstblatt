import { Steps, Flex, Button } from "antd";
import { CaretDownOutlined, CaretUpOutlined, DeleteOutlined } from "@ant-design/icons";
import { Link, useLoaderData, useSubmit } from "react-router-dom";


export default function Route() {
    const data = useLoaderData();
    const submit = useSubmit();
    const items = data.map((item, i, arr) => {
        const date = date => new Date(date).toLocaleDateString();
        const submitDelete = (id) => {
            return () => submit({id}, {
                method: "POST",
                encType: "application/json",
                action: ""
            });
        };
        const data = {
            title: item.name,
        }
        if (item.date_from) {
            data.subTitle = `${date(item.date_from)} — ${date(item.date_to)}`;
        }
        if ((i != 0) && (i != arr.length - 1)) {
            data.description = (
                <Flex>
                    <Button icon={<DeleteOutlined />} type="text" danger onClick={submitDelete(item.id)} />
                </Flex>
            );
        }
        return data;
    });

    return (
        <>
        <Steps
            progressDot
            current={items.length}
            direction="vertical"
            items={items}
        />
        <Flex justify="center">
            <Link to="new"><Button type="dashed">Добавить точку</Button></Link>
        </Flex>
        </>
    );
}