(function () {
    var graphs_updatable = false;

    document.addEventListener('DOMContentLoaded', function() {
        setUpGraphs();
        graphs_updatable = true;

        function prepCameraFeed(feedId) {
            var feed = document.getElementById(feedId);
            
            var feedUrl = "http://" + location.host + feed.alt
            feed.src = feedUrl;
            feed.alt = feedUrl;
        }

        prepCameraFeed("camera-feed-1");
        prepCameraFeed("camera-feed-2");
        prepCameraFeed("thermal-feed");
    });

    var temp_graph_ctx;
    var temp_graph_cpu_data      = [];
    var temp_graph_gpu_data      = [];
    var temp_graph_inertial_data = [];

    function setUpGraphs() {
        temp_graph_ctx = document.getElementById("temp-graph").getContext("2d");
    }

    function updateGraphs(data) {
        if (!graphs_updatable) return;

        temp_graph_cpu_data.push(data["rpi_temps"]["cpu"]);
        temp_graph_gpu_data.push(data["rpi_temps"]["gpu"]);
        temp_graph_inertial_data.push(data["inertial"]["temp"]);

        new Chart(temp_graph_ctx, {
            type: "line",
            data: {
                labels: [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ],
                datasets: [
                {
                    label: "CPU Temp",
                    backgroundColor: "rgba(255, 0, 0, 0.55)",
                    data: temp_graph_cpu_data.slice(Math.max(temp_graph_cpu_data.length - 10, 0))
                },
                {
                    label: "GPU Temp",
                    backgroundColor: "rgba(0, 255, 0, 0.55)",
                    data: temp_graph_gpu_data.slice(Math.max(temp_graph_gpu_data.length - 10, 0))
                },
                {
                    label: "Inertial Temp",
                    backgroundColor: "rgba(0, 0, 255, 0.55)",
                    data: temp_graph_inertial_data.slice(Math.max(temp_graph_inertial_data.length - 10, 0))
                }
                ],
            },
            options: {
                animation: {
                    duration: 0,
                },
                hover: {
                    animationDuration: 0,
                },
                responsiveAnimationDuration: 0,
                scales: {
                    yAxes: [{
                        display: true,
                        ticks: {
                            suggestedMin: 42,
                            suggestedMax: 52
                        }
                    }]
                }
            }
        });
    }

    function retrieveData(num = 0) {
        $.ajax({
            url: "data_acquisition.php",
            data: {
                start_index_for_inemo: num
            }
        }).done(function(data) {
            var ind = num;
            var parsed_data = JSON.parse(data);

            updateGraphs(parsed_data);

            setTimeout(function() { retrieveData(ind); }, 500);
        });
    }

    retrieveData();
})();
