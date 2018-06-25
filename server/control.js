function allStop() {
    $.ajax({
        url: "all_stop.php"
    });
}

function allResume() {
    $.ajax({
        url: "all_resume.php"
    });
}

function retrieveData() {
    $.ajax({
        url: "action_acquisition.php"
    }).done(function(data) {
        var parsed_data = JSON.parse(data);
        
        var commandsHTML = [];

        parsed_data.forEach(function(command) {
            var sectionName = "";
            var commandName = "";
            var commandArgs = [];
            
            // Get data for motor commands.
            function handleMotors() {
                switch (command.id) {
                    case 1:
                        commandName = "Forward";
                        commandArgs.push([ "velocity", command.args[0] ]);
                        commandArgs.push([ "duration", command.args[1] ]);
                        break;
                    case 2:
                        commandName = "Reverse";
                        commandArgs.push([ "velocity", command.args[0] ]);
                        commandArgs.push([ "duration", command.args[1] ]);
                        break;
                    case 3:
                        commandName = "Left";
                        commandArgs.push([ "angle", command.args[0] ]);
                        break;
                    case 4:
                        commandName = "Right";
                        commandArgs.push([ "angle", command.args[0] ]);
                        break;
                }
            }

            // Get data for arm commands.
            function handleArm() {
                switch (command.id) {
                    case 1:
                        commandName = "Stow";
                        break;
                    case 2:
                        commandName = "Extend";
                        break;
                    case 3:
                        commandName = "Go To Ice Box";
                        break;
                    case 4:
                        commandName = "Grip";
                        break;
                    case 5:
                        commandName = "Release";
                        break;
                    case 6:
                        commandName = "Arm Go To";
                        commandArgs.push([ "position", command.args[0] ]);
                        if (command.args.length == 2) {
                            commandArgs.push([ "orientation", command.args[1] ]);
                        }
                        break;
                    case 7:
                        commandName = "Gripper Orient";
                        commandArgs.push([ "orientation", command.args[0] ]);
                        break;
                }
            }

            // Get data for camera commands.
            function handleCamera() {
                switch (command.id) {
                    case 1:
                        commandName = "Pan";
                        break;
                    case 2:
                        commandName = "Go To";
                        commandArgs.push([ "angle", command.args[0] ]);
                        break;
                }
            }

            // Determine which section this command belongs to.
            switch (command.section) {
                case -1:
                    sectionName = "All Resume";
                    break;
                case 0:
                    sectionName = "All Stop";
                    break;
                case 1:
                    sectionName = "Motors";
                    handleMotors();
                    break;
                case 2:
                    sectionName = "Arm";
                    handleArm();
                    break;
                case 4:
                    sectionName = "Rear Camera";
                    handleCamera();
                    break;
            }

            // Convert command to HTML.
            var commandHTML = "";
            commandHTML += "<span class=\"section\">" + sectionName + "</span> ";
            commandHTML += "<span class=\"name\">" + commandName + "</span> ";
            commandArgs.forEach(function(argument) {
                commandHTML += "<i>" + argument[0] + "</i> " + "<b>" + argument[1] + "</b> ";
            });
            commandsHTML.push(commandHTML);
        });

        var queueHTML = "<ul id=\"queue\">";
        commandsHTML.forEach(function(commandHTML) {
            queueHTML += "<li>" + commandHTML + "</li>";
        });
        queueHTML += "</ul>";

        document.getElementById("live-queue-holder").innerHTML = queueHTML; 

        setTimeout(function() { retrieveData(); }, 500);
    });
}

retrieveData();

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
} 

function submitForward() {
    var data = {
        section: 1,
        id: 1,
        args: []
    };
    var velocity = parseInt($("#forward .vel").text());
    var duration = parseInt($("#forward .dur").text());
    data["args"].push(velocity);
    data["args"].push(duration);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitReverse() {
    var data = {
        section: 1,
        id: 2,
        args: []
    };
    var velocity = parseInt($("#reverse .vel").text());
    var duration = parseInt($("#reverse .dur").text());
    data["args"].push(velocity);
    data["args"].push(duration);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitLeft() {
    var data = {
        section: 1,
        id: 3,
        args: []
    };
    var angle = parseInt($("#left .ang").text());
    data["args"].push(angle);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitRight() {
    var data = {
        section: 1,
        id: 4,
        args: []
    };
    var angle = parseInt($("#right .ang").text());
    data["args"].push(angle);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitStow() {
    var data = {
        section: 2,
        id: 1,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitExtend() {
    var data = {
        section: 2,
        id: 2,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitIceBox() {
    var data = {
        section: 2,
        id: 3,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitGrip() {
    var data = {
        section: 2,
        id: 4,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitRelease() {
    var data = {
        section: 2,
        id: 5,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitArmGoTo() {
    var data = {
        section: 2,
        id: 6,
        args: []
    };
    var x = $("#arm-go-to .x").text();
    var y = $("#arm-go-to .y").text();
    var z = $("#arm-go-to .z").text();
    data["args"].push(x + " " + y + " " + z);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitOrient() {
    var data = {
        section: 2,
        id: 7,
        args: []
    };
    var x = $("#orient .x").text();
    var y = $("#orient .y").text();
    var z = $("#orient .z").text();
    data["args"].push(x + " " + y + " " + z);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitPan() {
    var data = {
        section: 3,
        id: 1,
        args: []
    };

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}

function submitCameraGoTo() {
    var data = {
        section: 3,
        id: 3,
        args: []
    };
    var angle = parseInt($("#camera-go-to .ang").text());
    data["args"].push(angle);

    $.ajax({
        url: "action_handler.php",
        data: {
            command_data: JSON.stringify(data)
        }
    });

    return false;
}