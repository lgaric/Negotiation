#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

import argparse
from time import sleep
import random

"""
    MiddleMan!

    Pokretanje: python MiddleMan.py -id babajaga123@jix.im -pwd lozinka

"""

class MiddleMan(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class PonasanjeKA(FSMBehaviour):
        async def on_start(self):
            self.agent.sayBold(f"Starting Middle Man! ")

        async def on_end(self):
            self.agent.say("End!")

    class RegistracijaAgenata(State):
        
        """Registracija agenata za pregovaranje."""

        async def run(self):
            # Cekam registraciju prvog agenta
            self.agent.say("Waiting agent registrations!")
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                if msg.body in ["Registration"]:
                    self.agent.prviPregovarac = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"1. Agent {self.agent.prviPregovarac} has registered!")

            # Cekam registraciju drugog agenta
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                if msg.body in ["Registration"]:
                    self.agent.drugiPregovarac = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"2. Agent {self.agent.drugiPregovarac} has registered!")
            
            self.agent.sayBold("Negotiation begins!")
            self.set_next_state("PosaljiStartPregovaranja")


    class PosaljiStartPregovaranja(State):
        """Stanje koje javlja pregovaracima da proces pregovaranja pocinje."""

        async def run(self):
            # Poruka prvog agenta
            self.agent.say(f"Sending start messages!")
            msg = Message()
            msg = Message(
                to=self.agent.prviPregovarac,
                body="Start")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body="Start")
            await self.send(msg)
            self.set_next_state("Pregovaranje")


    class Pregovaranje(State):
        """Stanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            # Poruka prvog agenta
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"# {self.agent.vrijeme}")
            agent1GoodMessage = False
            agent2GoodMessage = False
            msg1 = Message()
            msg1 = await self.receive(timeout=100)
            if msg1:
                sender = str(msg1.sender).split("@", 1)[0]
                if msg1.body in ["1", "0"]:
                    agent1GoodMessage = True
                    if int(msg1.body) == 1:
                        self.agent.say(f"Agent {sender} is cheating!")
                    else:
                        self.agent.say(f"Agent {sender} is cooperating!")

            # Poruka drugog agenta
            msg2 = Message()
            msg2 = await self.receive(timeout=100)
            if msg2:
                sender = str(msg2.sender).split("@", 1)[0]
                if msg2.body in ["1", "0"]:
                    agent2GoodMessage = True
                    if int(msg2.body) == 1:
                        self.agent.say(f"Agent {sender} is cheating!")
                    else:
                        self.agent.say(f"Agent {sender} is cooperating!")

            if agent1GoodMessage and agent2GoodMessage:
                self.interpretiraj(msg1, msg2)
            



        def interpretiraj(self, msg1, msg2):
            self.agent.vrijeme -= 1
            if self.agent.vrijeme == 0:
                self.agent.say(f"Pregovaranje zavrseno!")
                self.set_next_state("PosaljiKrajPregovaranja")
            else:
                self.set_next_state("PosaljiStanjePregovaranja")
                if str(msg1.sender).split("/", 1)[0] == self.agent.prviPregovarac:
                    self.zabiljeziRezultat(msg1, msg2)
                else:
                    self.zabiljeziRezultat(msg2, msg1)

        def zabiljeziRezultat(self, pregovarac1, pregovarac2):
            
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
            print()
            self.agent.sayBold("Current score:")
            sender1 = str(self.agent.prviPregovarac).split("@", 1)[0]
            sender2 = str(self.agent.drugiPregovarac).split("@", 1)[0]
            self.agent.say(f"Agent {sender1}: {self.agent.pregovarac1Rezultat}")
            self.agent.say(f"Agent {sender2}: {self.agent.pregovarac2Rezultat}")
            await self.send(msg)
            sleep(1)
            self.set_next_state("Pregovaranje")


    class PosaljiKrajPregovaranja(State):
        """Stanje koje javlja pregovaracima stanje pregovaranja (jesu li prevareni ili nisu)"""

        async def run(self):
            # Poruka prvog agenta
            self.agent.say(f"Sending end messages!")
            msg = Message()
            msg = Message(
                to=self.agent.prviPregovarac,
                body="Kraj")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body="Kraj")
            await self.send(msg)
            sleep(1)
            await self.agent.stop()


    def say(self, msg):
        print(f"[MiddleMan] {msg}")

    def sayBold(self, msg):
        print('\033[1m' + f"[MiddleMan] {msg}" + '\033[0m')

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
    parser.add_argument("-id", type=str, help="MiddleMan ID", default="babajaga123@jix.im")
    parser.add_argument("-pwd", type=str, help="MiddleMan Password", default="lozinka")
    args = parser.parse_args()

    agent = MiddleMan(args.id, args.pwd)
    agent.start()
