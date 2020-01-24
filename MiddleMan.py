#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, State, FSMBehaviour
from spade.message import Message
from spade.template import Template

import argparse
from time import sleep
import random

"""
    Organizator!

    Pokretanje: python Organizator.py -jid babajaga123@jix.im -pwd lozinka

"""

class Organizator(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class PonasanjeKA(FSMBehaviour):
        async def on_start(self):
            self.agent.say("Starting!")

        async def on_end(self):
            self.agent.say("End!")

    class RegistracijaAgenata(State):
        """Registracija agenata za pregovaranje."""

        async def run(self):
            # Cekam registraciju prvog agenta
            self.agent.say("Cekam registraciju agenata!")
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                self.agent.say("Usao")
                if msg.body in ["Registracija"]:
                    self.agent.prviPregovarac = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"1. Agent se registrirao: {self.agent.prviPregovarac}")

            # Cekam registraciju drugog agenta
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                if msg.body in ["Registracija"]:
                    self.agent.drugiPregovarac = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"2. Agent se registrirao: {self.agent.drugiPregovarac}")
            
            self.agent.say("Pregovaranje pocinje!")
            self.set_next_state("PosaljiStartPregovaranja")


    class PosaljiStartPregovaranja(State):
        """Stanje koje javlja pregovaracima da proces pregovaranja pocinje."""

        async def run(self):
            # Poruka prvog agenta
            msg = Message()
            msg = Message(
                to=self.agent.prviPregovarac,
                body="Start")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body="Start")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)
            self.set_next_state("Pregovaranje")


    class Pregovaranje(State):
        """Stanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            # Poruka prvog agenta
            print("~~~~~~~~~~~~~~~~~~~~")
            print(f"# {self.agent.vrijeme}")
            agent1DobraPoruka = False
            agent2DobraPoruka = False
            msg1 = Message()
            msg1 = await self.receive(timeout=20)
            if msg1:
                sender = str(msg1.sender).split("/", 1)[0]
                self.agent.say(f"Agent {sender} poslao poruku: {msg1.body}")
                if msg1.body in ["1", "0"]:
                    agent1DobraPoruka = True

            # Poruka drugog agenta
            msg2 = Message()
            msg2 = await self.receive(timeout=20)
            if msg2:
                sender = str(msg1.sender).split("/", 1)[0]
                self.agent.say(f"Agent {sender} poslao poruku: {msg2.body}")
                if msg1.body in ["1", "0"]:
                    agent2DobraPoruka = True

            if agent1DobraPoruka and agent2DobraPoruka:
                self.interpretiraj(msg1, msg2)


        def interpretiraj(self, msg1, msg2):
            self.agent.vrijeme -= 1
            if self.agent.vrijeme == 0:
                self.agent.say(f"Pregovaranje zavrseno!")
                self.set_next_state("PosaljiKrajPregovaranja")
            else:
                self.set_next_state("PosaljiStanjePregovaranja")
                self.agent.say("Koordiniraj poruke")
                if str(msg1.sender).split("/", 1)[0] == self.agent.prviPregovarac:
                    self.zabiljeziRezultat(msg1, msg2)
                else:
                    self.zabiljeziRezultat(msg2, msg1)

        def zabiljeziRezultat(self, pregovarac1, pregovarac2):
            sleep(1)
            if pregovarac1.body in ["1"] and pregovarac2.body in ["1"]:
                self.agent.pregovarac1Rezultat += 2
                self.agent.pregovarac2Rezultat += 2
                self.agent.stanjePregovaraca = 11
            elif pregovarac1.body in ["1"] and pregovarac2.body in ["0"]:
                self.agent.pregovarac1Rezultat -= 1
                self.agent.pregovarac2Rezultat += 3
                self.agent.stanjePregovaraca = 10
            elif pregovarac1.body in ["0"] and pregovarac2.body in ["1"]:
                self.agent.pregovarac1Rezultat += 3
                self.agent.pregovarac2Rezultat -= 1
                self.agent.stanjePregovaraca = 1
            else:
                self.agent.stanjePregovaraca = 0

    class PosaljiStanjePregovaranja(State):
        """Stanje koje javlja pregovaracima stanje pregovaranja (jesu li prevareni ili nisu)"""

        async def run(self):
            # Poruka prvog agenta
            msg = Message()
            msg = Message(
                to=self.agent.prviPregovarac,
                body=f"Stanje:{self.agent.pregovarac1Rezultat}")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body=f"Stanje:{self.agent.pregovarac2Rezultat}")
            self.agent.say("Rezultat:")
            self.agent.say(f"{self.agent.prviPregovarac}: {self.agent.pregovarac1Rezultat}")
            self.agent.say(f"{self.agent.drugiPregovarac}: {self.agent.pregovarac2Rezultat}")
            await self.send(msg)
            self.set_next_state("Pregovaranje")


    class PosaljiKrajPregovaranja(State):
        """Stanje koje javlja pregovaracima stanje pregovaranja (jesu li prevareni ili nisu)"""

        async def run(self):
            # Poruka prvog agenta
            msg = Message()
            msg = Message(
                to=self.agent.prviPregovarac,
                body="Kraj")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body="Kraj")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)
            sleep(1)
            await self.agent.stop()


    def say(self, msg):
        print(f"[Organizator] {self.name}: {msg}")
        #self.agent.say(f"[Organizator] {self.name}: {msg}")

    async def setup(self):
        fsm = self.PonasanjeKA()
        self.vrijeme = 20
        self.pregovarac1Rezultat = 0
        self.pregovarac2Rezultat = 0
        self.stanjePregovaraca = 0

        fsm.add_state(name="RegistracijaAgenata", state=self.RegistracijaAgenata(), initial=True)
        fsm.add_state(name="PosaljiStartPregovaranja", state=self.PosaljiStartPregovaranja())
        fsm.add_state(name="PosaljiStanjePregovaranja", state=self.PosaljiStanjePregovaranja())
        fsm.add_state(name="PosaljiKrajPregovaranja", state=self.PosaljiKrajPregovaranja())
        fsm.add_state(name="Pregovaranje", state=self.Pregovaranje())

        fsm.add_transition(source="RegistracijaAgenata", dest="PosaljiStartPregovaranja")
        fsm.add_transition(source="PosaljiStartPregovaranja", dest="Pregovaranje")
        fsm.add_transition(source="Pregovaranje", dest="PosaljiKrajPregovaranja")
        fsm.add_transition(source="Pregovaranje", dest="PosaljiStanjePregovaranja")
        fsm.add_transition(source="PosaljiStanjePregovaranja", dest="Pregovaranje")

        self.add_behaviour(fsm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-jid", type=str, help="JID kupca", default="babajaga123@jix.im")
    parser.add_argument("-pwd", type=str, help="Lozinka kupca", default="lozinka")
    args = parser.parse_args()

    agent = Organizator(args.jid, args.pwd)
    agent.start()
