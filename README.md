# **MimicTTS**
This repository is a custom integration to Home-Assistant via HACS for MycroftAi-Mimic3 TTS.

Further integration steps and descriptions goes here later...

Code for integration in configuration.yaml:

    tts:
      - platform: mimictts
        host: "172.30.32.100"
        port: 59125
        voice: "hu_HU/diana-majlinger_low"
        language: "hu_HU"


Links: 
 - https://mycroft-ai.gitbook.io/docs/mycroft-technologies/mimic-tts/mimic-3
 -    https://github.com/Poeschl/speak2mary
 -    https://github.com/home-assistant/core/tree/dev/homeassistant/components/marytts
 -    https://www.home-assistant.io/integrations/marytts
