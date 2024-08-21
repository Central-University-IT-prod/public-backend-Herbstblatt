import { NavLink } from "react-router-dom";
import { Button } from "antd";

export default function NavItem({path, name}) {
    return (
        <NavLink to={path}>
            {({isActive}) => (
                <Button type={isActive ? "primary" : "default"}>
                    {name}
                </Button>
            )}
        </NavLink>
    )
}