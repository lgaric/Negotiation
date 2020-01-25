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
    Strategija pregovaranja: Copy Kitten

    Pokretanje: python CopyKitten.py -m babajaga123@jix.im -id lgaaric@jix.im -pwd lgaric

"""

class CopyKitten(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, MiddleMan, **kwargs):
        super().__init__(*args, **kwargs)
        self.MiddleMan = MiddleMan

    class FSMBehaviour(FSMBehaviour):
        async def on_start(self):
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            self.agent.sayBold(f"Starting {self.agent.name}! ")

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
            self.agent.msg = await self.receive(timeout=100)
            if self.agent.msg:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                if "Start" in self.agent.msg.body:
                    self.agent.sayBold("Start score: 0")
                    self.set_next_state("SendResponse")
                elif "Stanje" in self.agent.msg.body:
                    self.set_next_state("ProcessCurrentScore")
                elif "End" in self.agent.msg.body:
                    self.agent.score = str(self.agent.msg.body).split(":", 2)[1]
                    self.agent.opponentsScore = str(self.agent.msg.body).split(":", 2)[2]
                    self.set_next_state("ProcessResult")
                    
            

    class ProcessCurrentScore(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.lastScore = self.agent.score
            self.agent.score = str(self.agent.msg.body).split(":", 1)[1]

            # Opponent cheated
            if int(self.agent.lastScore) >= int(self.agent.score): # Handle errors
                if self.agent.opponentCheatedOnce:
                    self.agent.opponentCheatedTwice = True
                else:
                    self.agent.opponentCheatedOnce = True
                    self.agent.opponentCheatedTwice = False
            # Opponent cooperated
            else: 
                self.agent.opponentCheatedOnce = False
                self.agent.opponentCheatedTwice = False
            self.agent.sayBold(f"Current score: {self.agent.score}")
            
            self.set_next_state("NegotiateResponse")



    class NegotiateResponse(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            if self.agent.opponentCheatedTwice:
                self.agent.cheat = True
            else:
                self.agent.cheat = False
            self.set_next_state("SendResponse")



    class ProcessResult(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.say("End of negotiation!")
            print()
            self.agent.sayBold("Results:")
            self.agent.say(f"Me: {self.agent.score}")
            self.agent.say(f"Opponent: {self.agent.opponentsScore}")
            if int(self.agent.score) > int(self.agent.opponentsScore):
                self.agent.sayBold("I gained more in this negotiations! :)")
            elif int(self.agent.score) == int(self.agent.opponentsScore):
                self.agent.sayBold("Perfect agreement for both sides!")
            else:
                self.agent.sayBold("I lost more in this negotiations! :(")
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
        print(f"[Copy Kitten] {msg}")

    def sayBold(self, msg):
        print('\033[1m' + f"[Copy Kitten] {msg}" + '\033[0m')

    async def setup(self):
        fsm = self.FSMBehaviour()
        self.msg = Message()
        self.score = 0
        self.lastScore = 0
        self.opponentsScore = 0
        self.opponentCheatedOnce = False
        self.opponentCheatedTwice = False

        self.cheat = True # I always cheat!

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

    agent = CopyKitten(args.id, args.pwd, MiddleMan=args.MiddleMan)
    agent.start()
