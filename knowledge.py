import logging
import re
from typing import Tuple, List, Union, Optional, Pattern


async def Handler(message: str, **params: str) -> Optional[Union[str, bytes]]:
    """
    Example of handler type
    :param message: message text without trigger word
    :param params: named groups for regexp-based matching
    :return: None if nothing matched, string or bytes
    """
    pass  # typedef


class Knowledge:
    """
    Base async router for incoming messages.
    Routes messages if message starts from one of trigger word.
    Router's can be nested as usual triggers.
    Handlers may throw an exception that will be printed and suppressed (except KeyboardException).
    If no triggers specified - any message will be accepted

    @:param triggers: case-insensitive words that will be used as a trigger
    """

    def __init__(self, *triggers: str):
        self.__handlers = []  # type: List[Tuple[Pattern,Handler],...]
        self.__default = None  # type: Optional[Handler]
        self.__triggers = tuple(x.lower() for x in triggers)
        self.__log = logging.getLogger('knowledge')

    async def __call__(self, message_text: str, **params) -> Optional[Union[str, bytes]]:
        """
        Check that message contains trigger word in beginning (case-insensitive) and tries to check all handlers one-by-one.
        If handler's pattern matched and callback returns not None, result is returned as is.
        If no successful handler found, default handler used (if defined)
        If no triggers specified - any message will be accepted
        :param message_text: any text message
        :return: None - if nothing matched or if default handler returned not, otherwise expects string or bytes
        """
        self.__log.info("triggered text %s with %i params", message_text, len(params))
        triggered = len(self.__triggers) == 0
        for trigger in self.__triggers:
            if message_text.lower().startswith(trigger):
                message_text = message_text[len(trigger):]
                self.__log.info("triggered text %s by %s", message_text, trigger)
                triggered = True
                break
        if not triggered:
            self.__log.info("triggered text %s is not suitable for the router", message_text)
            return None
        for (pattern, handler) in self.__handlers:
            match = pattern.match(message_text)
            if match:
                self.__log.info("triggered text %s match handler by %s via %r", message_text, pattern.pattern, handler)
                reply = None
                try:
                    reply = await handler(message_text, **match.groupdict(), **params)
                except KeyboardInterrupt:
                    # it's a program termination
                    return None
                except Exception as ex:
                    self.__log.info("triggered text %s match handler by %s failed %r", message_text,
                                    pattern.pattern,
                                    ex)
                    print("error on processing", message_text, ":", ex)
                if reply is not None:
                    self.__log.info("triggered text %s match handler by %s replied %r", message_text,
                                    pattern.pattern,
                                    reply)
                    return reply
        if self.__default is not None:
            return await self.__default(message_text, **params)

    def simple(self, keyword: str, handler: Handler = None):
        """
        Add simple non-regexp handler that matched if text exact as in message
        :param keyword: trigger text
        :param handler: standard handler or none for annotation wrapper
        """
        pattern = re.compile(re.escape(keyword))
        if handler is None:
            return self.__register(pattern)
        self.__handlers.append((pattern, handler))

    def prefix(self, prefix: str, handler: Handler = None):
        """
        Add prefix-based handler that matched if text has specified prefix. Handler got message without prefix
        :param prefix: trigger prefix
        :param handler: standard handler or none for annotation wrapper that should expect message without prefix
        """
        pattern = re.compile(f'^{re.escape(prefix)}.*?')
        if handler is None:
            def wrapper(f):
                async def without_prefix(message: str):
                    return await f(message[len(prefix):])

                self.__handlers.append((pattern, without_prefix))
                return f

            return wrapper

        async def without_prefix(message: str):
            return await handler(message[len(prefix):])

        self.__handlers.append((pattern, without_prefix))

    def regexp(self, pattern_text: str, handler: Handler = None):
        """
        Add regexp handler that matched if pattern matched message.
        Named groups will be used as named arguments in handler
        :param pattern_text: any valid regexp
        :param handler: standard handler or none for annotation wrapper. should expects named arguments if pattern contains named groups
        """
        pattern = re.compile(pattern_text)
        if handler is None:
            return self.__register(pattern)
        self.__handlers.append((pattern, handler))

    def default(self, handler: Handler = None):
        """
        Set default handler for non-matched messages
        :param handler: standard handler or none for annotation wrapper
        """
        if handler is None:
            def wrapper(f):
                self.__default = f
                return f

            return wrapper
        self.__default = handler

    def __register(self, pattern: Pattern):
        def wrapper(f):
            self.__handlers.append((pattern, f))
            return f

        return wrapper
