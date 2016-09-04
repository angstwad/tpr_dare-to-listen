(function () {
    var app = angular.module('dareToListen', ['dareToListen.config', 'ezfb', 'oitozero.ngSweetAlert']);

    app.config(function (ezfbProvider, dtlConfig) {
        ezfbProvider.setInitParams({
            appId: dtlConfig.facebookAppId
        })
    });

    function getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min)) + min;
    }

    app.directive('randomBackgroundImage', function () {
        return {
            restrict: 'A',
            link: function (scope, element) {
                var images = [
                    "url(../images/header/darian.jpg)",
                    "url(../images/header/glen.jpg)",
                    "url(../images/header/kim.jpg)",
                    "url(../images/header/pena.jpg)"
                ];
                element.css("background-image", images[getRandomInt(0, 4)]);
            }
        }
    });

    app.controller('counterCtrl', [
        '$http',
        '$scope',
        '$interval',
        'dtlConfig',
        function ($http, $scope, $interval, dtlConfig) {
            var self = this;
            this.count = 0;

            function get() {
                var url = dtlConfig.apiBackend + '/dare-count';
                $http.get(url).then(
                    function (response) {
                        self.count = response.data.count;
                    },
                    function (response) {
                        console.log('There was a problem getting dare count.')
                    }
                )
            }

            $scope.$on('updateCounter', get);

            get();
            $interval(get, 60000);
        }
    ]);

    app.controller('contactFormCtrl', [
        '$http',
        '$scope',
        'SweetAlert',
        'dtlConfig',
        function ($http, $scope, SweetAlert, dtlConfig) {
            var self = this;
            self.data = {};

            this.oneTouched = function () {
                var touched = false;
                try {
                    $scope.messageForm.$error.required.forEach(function (item) {
                        if (item.$touched)
                            touched = true;
                    });
                } catch (TypeError) {
                    return false;
                }
                return touched;
            };

            this.sendMessage = function () {
                console.log('Send message.');
                if ($scope.messageForm.$invalid) {
                    SweetAlert.swal({
                        type: 'error',
                        title: 'Oops!',
                        text: 'Please fill out the form correctly and completely and try again.'
                    });
                    return;
                }
                var url = dtlConfig.apiBackend + '/contact';
                $http.post(url, angular.copy(self.data)).then(
                    function (response) {
                        self.data = {};
                        SweetAlert.swal({
                            type: "success",
                            title: "Awesome!",
                            text: "Your message has been sent. Thanks for contacting us!"
                        });
                        $scope.messageForm.$setValidity();
                        $scope.messageForm.$setPristine();
                        $scope.messageForm.$setUntouched();
                    },
                    function (response) {
                        SweetAlert.swal({
                            type: "error",
                            title: "Oh no!",
                            text: "There was a problem sending your message. Please try again later!"
                        })
                    }
                )
            }
        }
    ]);

    app.controller('socialCtrl', [
        '$http',
        'dtlConfig',
        function ($http, dtlConfig) {
            var self = this;
            this.dares = [];

            (function () {
                var url = dtlConfig.apiBackend + '/dares';
                $http.get(url).then(
                    function (response) {
                        self.dares = response.data.dares || [];
                    }
                )
            })();
        }
    ]);

    app.controller('dareFormCtrl', [
        '$http',
        '$scope',
        '$window',
        '$rootScope',
        'ezfb',
        'SweetAlert',
        'dtlConfig',
        function ($http, $scope, $window, $rootScope, ezfb, SweetAlert, dtlConfig) {
            var self = this;
            this.data = {
                public: true,
                optIn: true
            };
            this.showDare = true;
            this.dares = [
                'question more and preach less',
                'risk understanding your beliefs',
                'open my mind and risk changing it',
                'listen even when it hurts',
                'listen closest to the most challenging ideas',
                'put aside pre-conceived notions',
                'not judge your opinions by your appearance',
                'get outside my comfort zone',
                'seek new perspectives',
                'not label differing opinions "stupid"',
                'be open to new ideas',
                'ask sincere questions',
                'listen to your response',
                'think before I respond',
                'try and find common ground',
                'reserve judgement',
                'respect your experience',
                'trust your motivation',
                "try to understand where you're coming from",
                'put myself in your shoes',
                'consider "different" is not threatening',
                'be open and truly hear you',
                'shut my mouth and open my ears',
                'listen to those whose voices are seldom heard'
            ];

            this.takeDare = function (action, data) {
                console.log('Dared ' + action + '.', data);
                if ($scope.dareForm.$invalid) {
                    SweetAlert.swal({
                        type: 'error',
                        title: 'Oops!',
                        text: 'Please fill out the form completely and correcly before submitting your dare.'
                    });
                    return;
                }
                switch (action) {
                    case "TPR":
                        this.data.method = 'tpr';
                        doTpr(angular.copy(this.data));
                        break;
                    case "Twitter":
                        this.data.method = 'twitter';
                        doTweet(angular.copy(this.data));
                        break;
                    case "Facebook":
                        this.data.method = 'facebook';
                        doFacebook(angular.copy(this.data));
                        break;
                }
            };

            this.allReqTouched = function () {
                var touched = [];
                try {
                    $scope.dareForm.$error.required.forEach(function (item) {
                        touched.push(item.$touched)
                    });
                } catch (TypeError) {
                    return false;
                }
                return touched.every(function (val, idx, arr) {
                    return val === true;
                });
            };

            function sendUserData(data, type) {
                console.log("Sending user data to backend.");
                var url = dtlConfig.apiBackend + '/dare';
                $http.post(url, data).then(
                    function (response) {
                        $rootScope.$broadcast('updateCounter', true);
                    },
                    function (response) {
                        console.log('Error sending data to backend.');
                        if (type === 'tpr') {
                            SweetAlert.swal(
                                "Oops!",
                                "Something went wrong sending your dare to TPR.  Please try again.",
                                "error"
                            );
                            self.showDare = true;
                        }
                    }
                );

            }

            function doTpr(data) {
                console.log('Doing TPR dare.');
                sendUserData(data, 'tpr');
                self.showDare = false;
            }

            function makeTwitterUrl() {
                var twitterUrl = "https://twitter.com/intent/tweet",
                    tweet = "I dare to " + self.data.dare + ".",
                    queryUrl = "http://idaretolisten.org/",
                    hashtags = "DareToListen,TPR",
                    via = "TPRCommunity",
                    queryArgs = "?text=" + encodeURI(tweet) + "&via=" + via + "&url=" +
                        encodeURI(queryUrl) + "&hashtags=" + encodeURI(hashtags);
                return twitterUrl + queryArgs;
            }

            function doTweet(data) {
                console.log('Doing a Tweet.');
                var windowOptions = 'scrollbars=yes,resizable=yes,toolbar=no,location=yes',
                    width = 550,
                    height = 420,
                    winHeight = screen.height,
                    winWidth = screen.width,
                    uri = makeTwitterUrl(),
                    left = Math.round((winWidth / 2) - (width / 2)),
                    top = 0;

                if (winHeight > height) {
                    top = Math.round((winHeight / 2) - (height / 2));
                }

                $window.open(uri, 'intent', windowOptions + ',width=' + width + ',height=' +
                    height + ',left=' + left + ',top=' + top);

                sendUserData(data);
            }

            function doFacebook(data) {
                console.log('Doing Facebook share.');
                ezfb.ui({
                    method: 'share',
                    href: 'http://idaretolisten.org',
                    hashtag: '#DareToListen',
                    quote: "I dare to " + self.data.dare + "."
                }).then(function (response) {
                    sendUserData(data);
                })
            }
        }
    ]);

})();