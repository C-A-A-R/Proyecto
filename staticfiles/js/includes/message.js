setTimeout(function() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        var alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
        alertInstance.close();
    });
}, 5000);  // 5000ms = 5 seconds