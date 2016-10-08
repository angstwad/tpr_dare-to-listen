(function () {
    var app = angular.module('dtlReports', ['dareToListen.config']);

    app.controller('reportsCtrl', [
        '$http',
        'dtlConfig',
        function ($http, dtlConfig) {
            var self = this;
            var url = dtlConfig.apiBackend + "/reports";
            this.reports = {};
            this.formData = {};
            this.requested = false;
            this.error = false;
            this.fatalError = false;

            function get_reports() {
                $http.get(url).then(
                    function (response) {
                        self.reports = response.data
                    },
                    function (response) {
                        console.log('There was a problem getting the reports.');
                    }
                );
            }

            this.request_report = function () {
                self.requested = true;
                $http.post(url, self.formData).then(
                    function (response) {
                        self.formData = {};
                        self.error = false;
                    },
                    function (response) {
                        self.error = true;
                    }
                );
            };

            get_reports();
        }
    ]);
})();