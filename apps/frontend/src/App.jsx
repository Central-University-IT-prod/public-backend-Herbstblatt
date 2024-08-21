import { createBrowserRouter, RouterProvider, Navigate, redirect } from 'react-router-dom';
import Root from './Root.jsx';
import TripRoute from './TripRoute.jsx';
import Tickets from './Tickets.jsx';
import Notes from './Notes.jsx';
import NewRoutePoint from './NewRoutePoint.jsx';
import { Typography } from 'antd';

const {Text} = Typography


export default function App({token}) {
    const router = createBrowserRouter([
        {
            path: "/forbidden",
            element: <Text>Вы не можете управлять этой поездкой.</Text>
        },
        {
            path: "/",
            loader: async ({request}) => {
                const url = new URL(request.url);
                const params = new URLSearchParams(url.search);
                const [sub, trip] = params.get("tgWebAppStartParam").split("_");
                return redirect(`/trip/${trip}/${sub}`);
            }
        },
        {
                path: "/trip/:tripId",
                element: <Root />,
                loader: async ({params}) => {
                    const data = await fetch("/api/trips/" + params.tripId, {
                        headers: {
                            "Authorization": "Bearer " + token
                        }
                    });
                    if (data.status !== 200) return redirect("/forbidden");
                    return await data.json();
                },
                children: [
                    {
                        path: "route",
                        element: <TripRoute />,
                        loader: async ({params}) => {
                            const {tripId} = params;
                            return fetch(`/api/trips/${tripId}/points`, {
                                headers: {
                                    "Authorization": "Bearer " + token
                                }
                            });
                        },
                        action: async ({params, request}) => {
                            const {tripId} = params;
                            const {id} = await request.json();
                            return fetch(`/api/trips/${tripId}/points/${id}`, {
                                method: "DELETE",
                                headers: {
                                    "Authorization": "Bearer " + token
                                }
                            });
                        }
                    },
                    {
                        path: "route/new",
                        element: <NewRoutePoint />,
                        action: async ({params, request}) => {
                            const {tripId} = params;
                            const query = await request.json();
                            if (query.action === "searchCity") {
                                const resp = await fetch("https://nominatim.openstreetmap.org/search?" + new URLSearchParams({
                                    q: query.data,
                                    format: "json"
                                }));
                                const data = await resp.json();
                                return {resp: data};
                            } else {
                                await fetch(`/api/trips/${tripId}/points`, {
                                    method: "POST",
                                    headers: {
                                        "Authorization": "Bearer " + token,
                                        'Content-Type': 'application/json;charset=utf-8'
                                    },
                                    body: JSON.stringify({
                                        name: query.name,
                                        date_from: query.dates[0],
                                        date_to: query.dates[1],
                                        location_id: query.id,
                                        location_lat: query.lat,
                                        location_long: query.lon
                                    })
                                });
                                return redirect(`/trip/${tripId}/route`);
                            }
                        }
                    },
                    {
                        path: "tickets",
                        element: <Tickets />
                    },
                    {
                        path: "notes",
                        loader: async({params}) => {
                            const {tripId} = params;
                            return fetch(`/api/trips/${tripId}/notes`, {
                                headers: {
                                    "Authorization": "Bearer " + token
                                }
                            })
                        },
                        element: <Notes />
                    },
                    {
                        path: "*",
                        element: <Navigate to="route" replace />
                    }
                ]
            }
        ]);
    return (
        <RouterProvider router={router} />
    );
}