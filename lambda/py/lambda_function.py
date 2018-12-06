# -*- coding: utf-8 -*-

import logging
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, viewport
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode)

from typing import Dict, Any

SKILL_NAME = "Pager Karaoke"
HELP_MESSAGE = ("You can say, show me pager, show me karaoke, "
                "or show me device information!")
HELP_REPROMPT = ("You can say, show me pager, show me karaoke, "
                 "or show me device information!")
STOP_MESSAGE = "Goodbye!"

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

# Built-in Intent Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequest")

        speech = ('Welcome to the Pager Karaoke Device skill! '
                  'You can say, show me pager, show me karaoke, or '
                  'show me device information!')

        handler_input.response_builder.speak(speech).ask(speech).set_card(
            SimpleCard(SKILL_NAME, speech))
        return handler_input.response_builder.response


# Built-in Intent Handlers
class PagerIntentHandler(AbstractRequestHandler):
    """Handler for Pager Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("PagerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PagerIntent")

        speech = 'This is the pager template!'

        handler_input.response_builder.speak(speech).add_directive(
            RenderDocumentDirective(
                token="pagerToken",
                document=_load_apl_document("pager.json"),
                datasources={
                    'pagerTemplateData': {
                        'type': 'object',
                        'properties': {
                            'hintString': 'try the blue cheese!'
                        },
                        'transformers': [
                            {
                                'inputPath': 'hintString',
                                'transformer': 'textToHint'
                            }
                        ]
                    }
                }
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="pagerToken",
                commands=[
                    AutoPageCommand(
                        component_id="pagerComponentId",
                        duration=5000)
                ]
            )
        )

        return handler_input.response_builder.response


class KaraokeIntentHandler(AbstractRequestHandler):
    """Handler for Karaoke Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("KaraokeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In Karaoke Intent")

        speech = 'This is the karaoke template!'

        handler_input.response_builder.speak(speech).add_directive(
            RenderDocumentDirective(
                token="karaokeToken",
                document=_load_apl_document("karaoke.json"),
                datasources={
                    'karaokeTemplateData': {
                        'type': 'object',
                        'objectId': 'karaokeSample',
                        'properties': {
                            'karaokeSsml': '<speak>We’re excited to announce a new video training series from A Cloud Guru on Alexa skill development. The free training series called Alexa Devs walks new developers and non-developers through how to build Alexa skills from start to finish. You’ll also learn how to enhance your skill using persistence, Speechcons, and SSML to create more engaging voice experiences for customers. Check out the first episode on how to build your first Alexa skill here.</speak>',
                            'hintString': 'try the blue cheese!'
                        },
                        'transformers': [
                            {
                                'inputPath': 'karaokeSsml',
                                'outputName': 'karaokeSpeech',
                                'transformer': 'ssmlToSpeech'
                            },
                            {
                                'inputPath': 'karaokeSsml',
                                'outputName': 'karaokeText',
                                'transformer': 'ssmlToText'
                            },
                            {
                                'inputPath': 'hintString',
                                'transformer': 'textToHint'
                            }
                        ]
                    }
                }
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="karaokeToken",
                commands=[
                    SpeakItemCommand(
                        component_id="karaokespeechtext",
                        highlight_mode=HighlightMode.LINE)
                ]
            )
        )

        return handler_input.response_builder.response


class DeviceIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DeviceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In Device Intent")

        speech = 'This device is a '

        if viewport.get_viewport_profile == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE:
            speech += 'hub landscape large'
        elif viewport.get_viewport_profile == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM:
            speech += 'hub landscape medium'
        elif viewport.get_viewport_profile == viewport.ViewportProfile.HUB_ROUND_SMALL:
            speech += 'hub round small'
        elif viewport.get_viewport_profile == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE:
            speech += 'tv landscape extra large'
        elif viewport.get_viewport_profile == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            speech += 'mobile landscape small'
        else: 
            speech += 'echo device!'

        handler_input.response_builder.speak(speech).add_directive(
            RenderDocumentDirective(
                document=_load_apl_document("devices.json"),
                datasources={
                    'deviceTemplateData': {
                        'type': 'object',
                        'objectId': 'deviceSample',
                        'properties': {
                            'deviceName': viewport.get_viewport_profile(
                                handler_input.request_envelope),
                            'hintString': 'try and buy more devices!'
                        },
                        'transformers': [
                            {
                                'inputPath': 'hintString',
                                'transformer': 'textToHint'
                            }
                        ]
                    }
                }
            )
        )

        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak('EXCEPTION_MESSAGE').ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PagerIntentHandler())
sb.add_request_handler(KaraokeIntentHandler())
sb.add_request_handler(DeviceIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
