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
    Strategija pregovaranja: Opponent

    Pokretanje: python Opponent.py -m babajaga123@jix.im -id lgaaric@jix.im -pwd lgaric

"""

class Opponent(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, MiddleMan, **kwargs):
        super().__init__(*args, **kwargs)
        self.MiddleMan = MiddleMan

    class FSMBehaviour(FSMBehaviour):
        async def on_start(self):
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
                elif "Kraj" in self.agent.msg.body:
                    self.set_next_state("ProcessResult")
                    
            

    class ProcessCurrentScore(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            self.agent.testPhase += 1
            self.agent.lastScore = self.agent.score
            self.agent.score = str(self.agent.msg.body).split(":", 1)[1]

            if int(self.agent.lastScore) >= int(self.agent.score): # Handle errors
                if self.agent.testPhase <= 4:
                    self.agent.opponentCheatedInTestPhase = True # Detective

                if self.agent.opponentCheatedOnce:
                    self.agent.opponentCheatedTwice = True
                else:
                    self.agent.opponentCheatedOnce = True
                    self.agent.opponentCheatedTwice = False
            elif "Grudger" not in self.agent.myStrategy: # Grudger never forgets!
                self.agent.opponentCheatedOnce = False
                self.agent.opponentCheatedTwice = False

            self.agent.sayBold(f"Current score: {self.agent.score}")
            self.set_next_state("NegotiateResponse")



    class NegotiateResponse(State):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self): 
            if "AlwaysCheat" in self.agent.myStrategy: # TODO Simplify
                self.AlwaysCheat()
            elif "AlwaysCooperate" in self.agent.myStrategy:
                self.AlwaysCooperate()
            elif "CopyCat" in self.agent.myStrategy:
                self.CopyCat()
            elif "CopyKitten" in self.agent.myStrategy:
                self.CopyKitten()
            elif "Detective" in self.agent.myStrategy:
                self.Detective()
            elif "Grudger" in self.agent.myStrategy:
                self.Grudger()
            elif "Radnom" in self.agent.myStrategy:
                self.Radnom()
            elif "Simpleton" in self.agent.myStrategy:
                self.Simpleton()
            elif "AlwaysCheat" in self.agent.myStrategy:
                self.AlwaysCheat()
    
            self.set_next_state("SendResponse")


        def AlwaysCheat(self):
            self.agent.cheat = True

        def AlwaysCooperate(self):
            self.agent.cheat = False

        def CopyCat(self):
            if self.agent.opponentCheatedOnce:
                self.agent.cheat = True
            else:
                self.agent.cheat = False

        def CopyKitten(self):
            if self.agent.opponentCheatedTwice:
                self.agent.cheat = True
            else:
                self.agent.cheat = False

        def Detective(self):
            if self.agent.testPhase in [1, 3, 4]:
                self.agent.cheat = False
            elif self.agent.testPhase == 2:
                self.agent.cheat = True
            elif self.agent.opponentCheatedInTestPhase: # If opponent cheated act lice Copy Cat
                if self.agent.opponentCheatedOnce:
                    self.agent.cheat = True
                else:
                    self.agent.cheat = False
            else:                                       # Else act like Always Cheat
                self.agent.cheat = True

        def Grudger(self):
            if self.agent.opponentCheatedOnce: # TODO If cheated once, always cheat!!
                self.agent.cheat = True 
            else:
                self.agent.cheat = False 

        def Random(self):
            broj = random.randint(0,100)
            if broj <= 50: # 50% - 50% Cheating - Cooperating
                self.agent.cheat = True
            else:
                self.agent.cheat = False

        def Simpleton(self):
            if self.agent.opponentCheatedOnce:
                self.agent.cheat = not self.agent.cheatedPreviousMove
            else:
                self.agent.cheat = self.agent.cheatedPreviousMove

            self.agent.cheatedPreviousMove = self.agent.cheat



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
        print(f"[Opponent] {msg}")

    def sayBold(self, msg):
        print('\033[1m' + f"[Opponent] {msg}" + '\033[0m')

    async def setup(self):
        fsm = self.FSMBehaviour()
        self.msg = Message()
        self.score = 0
        self.lastScore = 0
        self.opponentCheatedOnce = False
        self.opponentCheatedTwive = False
        self.opponentCheatedInTestPhase = False
        self.cheatedPreviousMove = False
        self.cheat = False # Starting with cooperate, cheat, cooperate, cooperate!
        self.testPhase = 1
        strategies = ["AlwaysCheat", "AlwaysCooperate", "CopyCat", "CopyKitten", "Detective", "Grudger", "Random", "Simpleton"]
        self.myStrategy = random.choice(strategies)
        self.say(f"Selected strategy: {self.myStrategy}")

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

    agent = Opponent(args.id, args.pwd, MiddleMan=args.MiddleMan)
    agent.start()
