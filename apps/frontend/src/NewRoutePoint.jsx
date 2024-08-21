import { Form as RouterForm, useActionData, useSubmit } from "react-router-dom";
import { Input, List, DatePicker, Flex, Button, Typography } from "antd";
import { useState } from "react";

const {RangePicker} = DatePicker;
const {Text} = Typography;

export default function NewRoutePoint() {
    const submit = useSubmit();
    const data = useActionData();
    
    const [dates, setDates] = useState();
    const [error, setError] = useState(false);

    function submitReady({id, lat, lon, name}) {
        return (evt) => {
            if (dates === undefined) setError(true);
            else submit({
                action: "submitCity",
                id,
                lat,
                lon,
                name,
                dates
            }, {
                method: "POST",
                encType: "application/json",
                action: ""
            })
        };
    }

    return (
        <RouterForm>
            <Flex vertical gap="middle">
                <Input.Search 
                    placeholder="Выберите название города" 
                    onSearch={(value) => submit({
                        action: "searchCity",
                        data: value
                    }, {
                        method: "POST",
                        encType: "application/json",
                        action: ""
                    })}
                    enterButton
                />    
                <RangePicker outlined onChange={(dates) => setDates(dates)} />
                {error && <Text type="danger">Укажите даты</Text>}
            </Flex>
            <List itemLayout="vertical">
                {(data?.resp || []).map(element => (
                    <List.Item extra={[<Button onClick={submitReady({
                        id: element.osm_type + String(element.osm_id),
                        lat: element.lat,
                        lon: element.lon,
                        name: element.name
                    })}>Выбрать</Button>]}>
                        {element.display_name}
                    </List.Item>
                ))}
            </List>
        </RouterForm>
    );
}