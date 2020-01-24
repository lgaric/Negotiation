#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template

import argparse
from ast import literal_eval
from time import sleep
import random

"""
    Strategija pregovaranja: Always Cooperate

    Pokretanje: python AlwaysCheat.py -o babajaga123@jix.im -jid lgaric@jix.im -pwd lgaric

"""

class Pregovaratelj(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, organizator, **kwargs):
        super().__init__(*args, **kwargs)
        self.organizator = organizator

    class Registracija(OneShotBehaviour):
        """Registriranje na pregovaranje kod organizatora."""

        async def run(self):
            msg = Message(
                to=self.agent.organizator,
                body="Registracija")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)

    class Pregovaranje(CyclicBehaviour):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            msg = Message()
            msg = await self.receive(timeout=10)
            if msg:
                if msg.body in ["Kraj"]:
                    self.agent.say("Stop!")
                    await self.agent.stop()
                else:
                    msg = Message(
                        to=self.agent.organizator,
                        body="1")
                    self.agent.say(f"Saljem poruku: {msg.body}")
                    await self.send(msg)

    def say(self, msg):
        print(f"[Always Cooperate] {self.name}: {msg}")

    async def setup(self):
        self.say("Starting!")
        self.vrijeme = 20
        self.sugovornikPrijeVarao = False
        self.proslaPonuda = {}
        self.varam = False # Nikada ne varam! :)

        ponasanjePregovaranje = self.Pregovaranje()
        self.add_behaviour(ponasanjePregovaranje)

        ponasanjeRegistracija = self.Registracija()
        self.add_behaviour(ponasanjeRegistracija)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--organizator", type=str, help="JID organizatora pregovaranja", default="babajaga123@jix.im")
    parser.add_argument("-jid", type=str, help="JID kupca")
    parser.add_argument("-pwd", type=str, help="Lozinka kupca")
    args = parser.parse_args()

    agent = Pregovaratelj(args.jid, args.pwd, organizator=args.organizator)
    agent.start()
