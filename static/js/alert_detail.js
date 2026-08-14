console.log("Alert detail JS loaded");


const alertId =
    window.location.pathname.split("/").pop();


console.log(
    "Alert ID:",
    alertId
);



const resolveButton =
    document.getElementById(
        "resolve-alert"
    );



if (resolveButton) {


    resolveButton.addEventListener(
        "click",
        async() => {


            console.log(
                "Resolve clicked"
            );



            try {


                const tokenResponse =
                    await fetch(
                        "/api/csrf-token", {
                            credentials: "same-origin"
                        }
                    );



                const tokenData =
                    await tokenResponse.json();



                const response =
                    await fetch(
                        `/alerts/api/${alertId}`, {

                            method: "PATCH",

                            headers: {

                                "Content-Type": "application/json",

                                "X-CSRFToken": tokenData.csrf_token
                            },


                            credentials: "same-origin",


                            body: JSON.stringify({

                                status: "resolved"

                            })

                        }
                    );



                console.log(
                    "PATCH status:",
                    response.status
                );



                const result =
                    await response.json();



                console.log(
                    "Response:",
                    result
                );



                if (response.ok) {


                    resolveButton.textContent =
                        "Resolved";


                    resolveButton.disabled =
                        true;



                    setTimeout(() => {

                        window.location.href =
                            "/dashboard";

                    }, 1000);



                } else {


                    console.error(
                        "Update failed:",
                        result
                    );

                }



            } catch (error) {


                console.error(
                    "Resolve error:",
                    error
                );

            }


        }
    );


} else {


    console.error(
        "Resolve button not found"
    );

}