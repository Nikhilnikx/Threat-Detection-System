console.log("Dashboard JS loaded");


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(
            /[&<>'"]/g,
            function(char) {

                const map = {
                    "&": "&amp;",
                    "<": "&lt;",
                    ">": "&gt;",
                    "'": "&#39;",
                    '"': "&quot;"
                };

                return map[char];

            }
        );
}



function renderRows(items, formatter) {

    if (!items || items.length === 0) {

        return "<p class='empty'>No records yet.</p>";

    }

    return items.map(formatter).join("");

}





async function loadDashboard() {

    console.log("Loading dashboard...");


    try {


        const response = await fetch(
            "/api/dashboard/summary", {
                credentials: "same-origin"
            }
        );


        console.log(
            "API status:",
            response.status
        );



        if (!response.ok) {

            window.location.href = "/login";
            return;

        }



        const data = await response.json();



        console.log(
            "Dashboard data:",
            data
        );




        document.getElementById(
                "total-events"
            ).textContent =
            data.total_events;



        document.getElementById(
                "open-alerts"
            ).textContent =
            data.open_alerts;




        document.getElementById(
                "critical-events"
            ).textContent =
            data.critical_events;






        document.getElementById(
                "risk-breakdown"
            ).innerHTML =


            Object.entries(
                data.risk_breakdown
            )

        .map(function(entry) {


            return `

                <span class="badge ${escapeHtml(entry[0])}">

                    ${escapeHtml(entry[0])}: ${entry[1]}

                </span>

                `;


        })

        .join("");









        document.getElementById(
                "recent-events"
            ).innerHTML =


            renderRows(

                data.recent_events,


                function(event) {


                    return `

                    <div class="row">


                        <div>


                            <strong>

                                <a 
                                class="event-link"
                                href="/events/${event.id}/detail"
                                >

                                ${escapeHtml(event.event_type)}

                                </a>

                            </strong>



                            <small>

                                ${escapeHtml(event.created_at)}

                            </small>


                        </div>





                        <span class="badge ${escapeHtml(event.severity)}">


                            ${event.risk_score}/100 ·

                            ${escapeHtml(event.severity)}


                        </span>



                    </div>

                    `;


                }

            );









        document.getElementById(
                "recent-alerts"
            ).innerHTML =



            renderRows(

                data.recent_open_alerts,


                function(alert) {


                    return `


                    <div class="row">


                        <div>


                            <strong>


                                <a

                                class="alert-link"

                                href="/alerts/${alert.id}"

                                >

                                    Alert #${alert.id}

                                </a>


                            </strong>




                            <small>

                                ${escapeHtml(
                                    alert.event_type || 
                                    "Security event"
                                )}

                            </small>



                        </div>





                        <span class="badge ${escapeHtml(alert.severity)}">


                            ${escapeHtml(alert.status)}


                        </span>



                    </div>


                    `;


                }

            );





    } catch (error) {


        console.error(
            "Dashboard loading failed:",
            error
        );


    }


}








document
    .getElementById("logout")
    .addEventListener(

        "click",

        async function() {



            const tokenResponse =

                await fetch(
                    "/api/csrf-token", {
                        credentials: "same-origin"
                    }
                );




            const tokenData =

                await tokenResponse.json();





            await fetch(

                "/auth/logout",

                {

                    method: "POST",


                    headers: {

                        "X-CSRFToken": tokenData.csrf_token

                    },


                    credentials: "same-origin"


                }

            );




            window.location.href = "/login";


        }

    );







loadDashboard();



setInterval(

    loadDashboard,

    30000

);