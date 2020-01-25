#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

import argparse
from ast import literal_eval
from time import sleep
import random

"""
    Strategija pregovaranja: Copy Cat

    Pokretanje: python CopyCat.py -m babajaga123@jix.im -id lgaric@jix.im -pwd lgaric

"""

class CopyCat(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, MiddleMan, **kwargs):
        super().__init__(*args, **kwargs)
        self.MiddleMan = MiddleMan

    class StatesBehaviour(FSMBehaviour):
        async def on_start(self):
            self.agent.say("Starting!")

        async def on_end(self):
            self.agent.say("End!")

    class Registration(State):
        """Registriranje na pregovaranje kod MiddleMana."""

        async def run(self):
            msg = Message(
                to=self.agent.MiddleMan,
                body="Registration")
            self.agent.say(f"Sending message: {msg.body}")
            await self.send(msg)
            
            self.set_next_state("AcceptMessage")

    class AcceptMessage(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.msg = await self.receive(timeout=10)
            if self.agent.msg:
                print("~~~~~~~~~~~~~~~~~~~~")
                if "Start" in self.agent.msg.body:
                    self.set_next_state("SendResponse")
                elif "Stanje" in self.agent.msg.body:
                    self.set_next_state("ProcessCurrentScore")
                elif "Kraj" in self.agent.msg.body:
                    self.set_next_state("ProcessResult")
                    
            

    class ProcessCurrentScore(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.lastScore = self.agent.score
            self.agent.score = str(self.agent.msg.body).split(":", 1)[1]
            if int(self.agent.lastScore) >= int(self.agent.score): # Handle errors
                self.agent.opponentCheated = True
            else: 
                self.agent.opponentCheated = False
            self.agent.say(f"Current score: {self.agent.score}")
            
            self.set_next_state("NegotiateResponse")



    class NegotiateResponse(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            if self.agent.opponentCheated:
                self.agent.cheat = True
            else:
                self.agent.cheat = False

            self.set_next_state("SendResponse")



    class ProcessResult(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.say("Stop!")
            self.agent.say(f"My result: {self.agent.score}")
            await self.agent.stop()


    class SendResponse(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            if(self.agent.cheat):
                bodyMessage = "0"
                self.agent.say(f"Cheating!")
            else:
                bodyMessage = "1"
                self.agent.say(f"Cooperating!")

            msg = Message(
                        to=self.agent.MiddleMan,
                        body=bodyMessage)
            await self.send(msg)
                    
            self.set_next_state("AcceptMessage")

    def say(self, msg):
        print(f"[Copy Cat] {self.name}: {msg}")

    async def setup(self):
        fsm = self.StatesBehaviour()
        self.say("Starting!")
        self.score = 0
        self.lastScore = 0
        self.opponentCheated = False
        self.cheat = False # I cooperate at first!

        fsm.add_state(name="Registration", state=self.Registration(), initial=True)
        fsm.add_state(name="AcceptMessage", state=self.AcceptMessage())
        fsm.add_state(name="ProcessCurrentScore", state=self.ProcessCurrentScore())
        fsm.add_state(name="ProcessResult", state=self.ProcessResult())
        fsm.add_state(name="NegotiateResponse", state=self.NegotiateResponse())
        fsm.add_state(name="SendResponse", state=self.SendResponse())

        fsm.add_transition(source="Registration", dest="AcceptMessage")
        fsm.add_transition(source="AcceptMessage", dest="SendResponse")
        fsm.add_transition(source="AcceptMessage", dest="ProcessCurrentScore")
        fsm.add_transition(source="AcceptMessage", dest="ProcessResult")
        fsm.add_transition(source="ProcessCurrentScore", dest="NegotiateResponse")
        fsm.add_transition(source="NegotiateResponse", dest="SendResponse")
        fsm.add_transition(source="SendResponse", dest="AcceptMessage")

        self.add_behaviour(fsm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--MiddleMan", type=str, help="ID MiddleMana pregovaranja", default="babajaga123@jix.im")
    parser.add_argument("-id", type=str, help="Agent ID")
    parser.add_argument("-pwd", type=str, help="Agent password")
    args = parser.parse_args()

    agent = CopyCat(args.id, args.pwd, MiddleMan=args.MiddleMan)
    agent.start()
