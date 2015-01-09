(function() {
    'use strict';
    describe('Logger', function() {
        it('expose window.log_event', function() {
            expect(window.log_event).toBe(Logger.log);
        });

        describe('log', function() {
            it('can send a request to log event', function() {
                spyOn(jQuery, 'ajaxWithPrefix');
                Logger.log('example', 'data');
                expect(jQuery.ajaxWithPrefix).toHaveBeenCalledWith({
                    url: '/event',
                    type: 'POST',
                    data: {
                        event_type: 'example',
                        event: '"data"',
                        page: window.location.href
                    },
                    async: true
                });
            });

            it('can send a request with custom options to log event', function() {
                spyOn(jQuery, 'ajaxWithPrefix');
                Logger.log('example', 'data', null, {type: 'GET', async: false});
                expect(jQuery.ajaxWithPrefix).toHaveBeenCalledWith({
                    url: '/event',
                    type: 'GET',
                    data: {
                        event_type: 'example',
                        event: '"data"',
                        page: window.location.href
                    },
                    async: false
                });
            });
        });

        describe('listen', function() {
            beforeEach(function () {
                spyOn(jQuery, 'ajaxWithPrefix');
                this.callbacks = _.map(_.range(4), function () {
                    return jasmine.createSpy();
                });
                Logger.listen('example', null, this.callbacks[0]);
                Logger.listen('example', null, this.callbacks[1]);
                Logger.listen('example', 'element', this.callbacks[2]);
                Logger.listen('new_event', null, this.callbacks[3]);
            });

            it('can listen events when the element name is unknown', function() {
                Logger.log('example', 'data');
                expect(this.callbacks[0]).toHaveBeenCalledWith('example', 'data', null);
                expect(this.callbacks[1]).toHaveBeenCalledWith('example', 'data', null);
                expect(this.callbacks[2]).not.toHaveBeenCalled();
                expect(this.callbacks[3]).not.toHaveBeenCalled();
            });

            it('can listen events when the element name is known', function() {
                Logger.log('example', 'data', 'element');
                expect(this.callbacks[0]).not.toHaveBeenCalled();
                expect(this.callbacks[1]).not.toHaveBeenCalled();
                expect(this.callbacks[2]).toHaveBeenCalledWith('example', 'data', 'element');
                expect(this.callbacks[3]).not.toHaveBeenCalled();
            });
        });

        describe('bind', function() {
            beforeEach(function() {
                this.initialPostWithPrefix = jQuery.postWithPrefix;
                this.initialGetWithPrefix = jQuery.getWithPrefix;
                this.initialAjaxWithPrefix = jQuery.ajaxWithPrefix;
                this.prefix = '/6002x';
                AjaxPrefix.addAjaxPrefix($, _.bind(function () {
                    return this.prefix;
                }, this));
                Logger.bind();
            });

            afterEach(function() {
                jQuery.postWithPrefix = this.initialPostWithPrefix;
                jQuery.getWithPrefix = this.initialGetWithPrefix;
                jQuery.ajaxWithPrefix = this.initialAjaxWithPrefix;
                window.onunload = null;
            });

            it('can bind the onunload event', function() {
                expect(window.onunload).toEqual(jasmine.any(Function));
            });

            it('can send a request to log event', function() {
                spyOn(jQuery, 'ajax');
                window.onunload();
                expect(jQuery.ajax).toHaveBeenCalledWith({
                    url: this.prefix + '/event',
                    type: 'GET',
                    data: {
                        event_type: 'page_close',
                        event: '',
                        page: window.location.href
                    },
                    async: false
                });
            });
        });
    });
}).call(this);
