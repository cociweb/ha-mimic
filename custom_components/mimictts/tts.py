"""Support for the MimicTTS service."""
from __future__ import annotations

import http.client as http
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
from homeassistant.const import CONF_EFFECT, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

CONF_VOICE = "voice"
CONF_CODEC = "codec"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 59125
DEFAULT_LANG = "en_US"
DEFAULT_VOICE = "cmu-slt-hsmm"
DEFAULT_CODEC = "WAVE_FILE"
DEFAULT_EFFECTS: dict[str, str] = {}
DEFAULT_INPUT_TYPE = "TEXT"
DEFAULT_OUTPUT_TYPE = "AUDIO"
DEFAULT_LOCALE = "en_US"


class MimicTTS(object):

    def __init__(self,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 codec=DEFAULT_CODEC,
                 locale=DEFAULT_LOCALE,
                 voice=DEFAULT_VOICE,
                 input_type=DEFAULT_INPUT_TYPE):

        self._host = host
        self._port = port
        self._codec = codec
        self._locale = locale
        self._voice = voice
        self._input_type = input_type

    def speak(self, message, effects=None):
        if effects is None:
            effects = {}

        raw_params = {
            "INPUT_TEXT": message.encode('UTF8'),
            "OUTPUT_TYPE": DEFAULT_OUTPUT_TYPE,
            "INPUT_TYPE": self._input_type,
            "LOCALE": self._locale,
            "AUDIO": self._codec,
            "VOICE": self._voice,
        }

        for effect, parameter in effects.items():
            raw_params["effect_%s_selected" % effect] = "on"
            raw_params["effect_%s_parameters" % effect] = parameter

        conn = http.HTTPConnection(self._host, self._port)

        conn.request("POST", "/process", urlencode(raw_params))
        response = conn.getresponse()

        if response.status != 200:
            raise Exception("{0} - {1}: '{2}''".format(response.status, response.reason, response.readline()))
        return response.read()

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def locale(self):
        return self._locale

    @property
    def voice(self):
        return self._voice

    @property
    def codec(self):
        return self._codec

    @staticmethod
    def supported_codecs():
        return ["WAVE_FILE", "AU_FILE", "AIFF_FILE"]

    @staticmethod
    def supported_effects():
        """Returns a dict of available effects and the default arguments"""
        return {
            "Volume": "amount:2.0;",
            "TractScaler": "amount:1.5;",
            "F0Scale": "f0Scale:2.0;",
            "F0Add": "f0Add:50.0;",
            "Rate": "durScale:1.5;",
            "Robot": "amount:100.0;",
            "Whisper": "amount:100.0;",
            "Stadium": "amount:100.0",
            "Chorus": "delay1:466;amp1:0.54;delay2:600;amp2:-0.10;delay3:250;amp3:0.30",
            "FIRFilter": "type:3;fc1:500.0;fc2:2000.0",
            "JetPilot": ""
        }

    @staticmethod
    def supported_locales():
        return ["af_ZA", "bn", "de_DE", "el_GR", "en_UK", "es_ES", "fa", "fi_FI", "fr_FR", "gu_IN", "ha_NE", "hu_HU", "it_IT", "jv_ID", "ko_KO", "ne_NP", "nl", "pl_PL", "ru_RU", "sw", "te_IN", "tn_ZA", "uk_UK", "vi_VN", "yo"]

SUPPORT_LANGUAGES = MimicTTS.supported_locales()
SUPPORT_CODEC = MimicTTS.supported_codecs()
SUPPORT_OPTIONS = [CONF_EFFECT]
SUPPORT_EFFECTS = MimicTTS.supported_effects().keys()


MAP_MimicTTS_CODEC = {"WAVE_FILE": "wav", "AIFF_FILE": "aiff", "AU_FILE": "au"}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): cv.string,
        vol.Optional(CONF_CODEC, default=DEFAULT_CODEC): vol.In(SUPPORT_CODEC),
        vol.Optional(CONF_EFFECT, default=DEFAULT_EFFECTS): {
            vol.All(cv.string, vol.In(SUPPORT_EFFECTS)): cv.string
        },
    }
)


def get_engine(hass, config, discovery_info=None):
    """Set up MimicTTS speech component."""
    return MimicTTSProvider(hass, config)


class MimicTTSProvider(Provider):
    """MimicTTS speech api provider."""

    def __init__(self, hass, conf):
        """Init MimicTTS TTS service."""
        self.hass = hass
        self._Mimic = MimicTTS(
            conf.get(CONF_HOST),
            conf.get(CONF_PORT),
            conf.get(CONF_CODEC),
            conf.get(CONF_LANG),
            conf.get(CONF_VOICE),
        )
        self._effects = conf.get(CONF_EFFECT)
        self.name = "MimicTTS"

    @property
    def default_language(self):
        """Return the default language."""
        return self._Mimic.locale

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def default_options(self):
        """Return dict include default options."""
        return {CONF_EFFECT: self._effects}

    @property
    def supported_options(self):
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    def get_tts_audio(self, message, language, options):
        """Load TTS from MimicTTS."""
        effects = options[CONF_EFFECT]

        data = self._Mimic.speak(message, effects)
        audiotype = MAP_MimicTTS_CODEC[self._Mimic.codec]

        return audiotype, data
