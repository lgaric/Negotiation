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

    Command line start: python MiddleMan.py -id babajaga123@jix.im -pwd lozinka

"""

class MiddleMan(Agent):

    """Middle Man between two negotiation sides."""

    def __init__(self, *args, rounds, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounds = rounds

    class FSMBehaviour(FSMBehaviour):
        async def on_start(self):
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            self.agent.sayBold(f"Starting Middle Man! ")

        async def on_end(self):
            self.agent.say("End!")

    class AgentsRegistration(State):
        
        """State responsible for registering 2 agents (negotiation sides)."""

        async def run(self):
            self.agent.say("Waiting agent registrations!")

            # First agent registration
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                if msg.body in ["Registration"]:
                    self.agent.firstAgentName = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"1. Agent {self.agent.firstAgentName} has registered!")

            # Second agent registration
            msg = Message()
            msg = await self.receive(timeout=100)
            if msg:
                if msg.body in ["Registration"]:
                    self.agent.drugiPregovarac = str(msg.sender).split("/", 1)[0]
                    self.agent.say(f"2. Agent {self.agent.drugiPregovarac} has registered!")
            
            self.agent.sayBold("Negotiation begins!")
            self.set_next_state("SendStartNegotiations")


    class SendStartNegotiations(State):

        """State for sending start messages with end scores to both agents."""

        async def run(self):
            # Poruka prvog agenta
            self.agent.say(f"Sending start messages!")
            msg = Message()
            msg = Message(
                to=self.agent.firstAgentName,
                body="Start")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body="Start")
            await self.send(msg)
            self.set_next_state("Negotiations")


    class Negotiations(State):

        """State responsible for processing messages and leading negotiation process."""

        async def run(self):
            # First agent message
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"# {self.agent.rounds}")
            agent1GoodMessage = False
            agent2GoodMessage = False
            msg1 = Message()
            msg1 = await self.receive(timeout=100)
            if msg1:
                sender = str(msg1.sender).split("@", 1)[0]
                if msg1.body in ["1", "0"]:
                    agent1GoodMessage = True
                    if int(msg1.body) == 0:
                        self.agent.say(f"Agent {sender} is cheating!")
                    else:
                        self.agent.say(f"Agent {sender} is cooperating!")

            # Second agent message
            msg2 = Message()
            msg2 = await self.receive(timeout=100)
            if msg2:
                sender = str(msg2.sender).split("@", 1)[0]
                if msg2.body in ["1", "0"]:
                    agent2GoodMessage = True
                    if int(msg2.body) == 0:
                        self.agent.say(f"Agent {sender} is cheating!")
                    else:
                        self.agent.say(f"Agent {sender} is cooperating!")

            if agent1GoodMessage and agent2GoodMessage:
                self.interpret(msg1, msg2)
            



        def interpret(self, msg1, msg2):
            self.agent.rounds = int(self.agent.rounds) - 1
            if int(self.agent.rounds) == 0:
                self.agent.sayBold("Negotiation ends!")
                self.set_next_state("SendEndMessage")
            else:
                self.set_next_state("SendNegotiationScores")

            if str(msg1.sender).split("/", 1)[0] == self.agent.firstAgentName:
                self.saveScore(msg1, msg2)
            else:
                self.saveScore(msg2, msg1)

        def saveScore(self, agent1, agent2):
            
            if agent1.body in ["1"] and agent2.body in ["1"]:
                self.agent.agent1Score += 2
                self.agent.agent2Score += 2
                self.agent.currentNegotiationState = 11 # Both agents are cooperating
            elif agent1.body in ["1"] and agent2.body in ["0"]:
                self.agent.agent1Score -= 1
                self.agent.agent2Score += 3
                self.agent.currentNegotiationState = 10 # Only first agent is cooperating
            elif agent1.body in ["0"] and agent2.body in ["1"]:
                self.agent.agent1Score += 3
                self.agent.agent2Score -= 1
                self.agent.currentNegotiationState = 1 # Only second agent is coooperating
            else:
                self.agent.currentNegotiationState = 0 # No one is cooperating

    class SendNegotiationScores(State):

        """State which sends current scores to agents"""

        async def run(self):
            # Message from first agent
            msg = Message()
            msg = Message(
                to=self.agent.firstAgentName,
                body=f"Stanje:{self.agent.agent1Score}")
            await self.send(msg)

            # Message from second agent
            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body=f"Stanje:{self.agent.agent2Score}")
            print()
            self.agent.sayBold("Current score:")
            sender1 = str(self.agent.firstAgentName).split("@", 1)[0]
            sender2 = str(self.agent.drugiPregovarac).split("@", 1)[0]
            self.agent.say(f"Agent {sender1}: {self.agent.agent1Score}")
            self.agent.say(f"Agent {sender2}: {self.agent.agent2Score}")
            await self.send(msg)
            sleep(1)
            self.set_next_state("Negotiations")


    class SendEndMessage(State):
        
        """State for sending end messages with end scores to both agents"""

        async def run(self):
            # End message -> End:MyScore:OpponentsScore
            self.agent.say(f"Sending end messages!")
            msg = Message()
            msg = Message(
                to=self.agent.firstAgentName,
                body=f"End:{self.agent.agent1Score}:{self.agent.agent2Score}")
            await self.send(msg)

            msg = Message()
            msg = Message(
                to=self.agent.drugiPregovarac,
                body=f"End:{self.agent.agent2Score}:{self.agent.agent1Score}")
            
            self.printFinalResults()
            await self.send(msg)
            sleep(1)
            await self.agent.stop()

        def printFinalResults(self):
            print()
            self.agent.sayBold("Final score:")
            sender1 = str(self.agent.firstAgentName).split("@", 1)[0]
            sender2 = str(self.agent.drugiPregovarac).split("@", 1)[0]
            self.agent.say(f"Agent {sender1}: {self.agent.agent1Score}")
            self.agent.say(f"Agent {sender2}: {self.agent.agent2Score}")

            print()
            if int(self.agent.agent1Score) > int(self.agent.agent2Score):
                self.agent.sayBold(f"Agent {sender1} has gained more from this negotiations!")
            elif int(self.agent.agent2Score) > int(self.agent.agent1Score):
                self.agent.sayBold(f"Agent {sender2} has gained more from this negotiations!")
            else:
                self.agent.sayBold("Both agents gained the same from this negotiations! Perfect match!:)")


    def say(self, msg):
        print(f"[MiddleMan] {msg}")

    def sayBold(self, msg):
        print('\033[1m' + f"[MiddleMan] {msg}" + '\033[0m')

    async def setup(self):
        fsm = self.FSMBehaviour()
        self.vrijeme = 20
        self.agent1Score = 0
        self.agent2Score = 0
        self.currentNegotiationState = 0

        fsm.add_state(name="AgentsRegistration", state=self.AgentsRegistration(), initial=True)
        fsm.add_state(name="SendStartNegotiations", state=self.SendStartNegotiations())
        fsm.add_state(name="SendNegotiationScores", state=self.SendNegotiationScores())
        fsm.add_state(name="SendEndMessage", state=self.SendEndMessage())
        fsm.add_state(name="Negotiations", state=self.Negotiations())

        fsm.add_transition(source="AgentsRegistration", dest="SendStartNegotiations")
        fsm.add_transition(source="SendStartNegotiations", dest="Negotiations")
        fsm.add_transition(source="Negotiations", dest="SendEndMessage")
        fsm.add_transition(source="Negotiations", dest="SendNegotiationScores")
        fsm.add_transition(source="SendNegotiationScores", dest="Negotiations")

        self.add_behaviour(fsm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", type=str, help="MiddleMan ID", default="babajaga123@jix.im")
    parser.add_argument("-pwd", type=str, help="MiddleMan Password", default="lozinka")
    parser.add_argument("-r", "--rounds", type=str, help="Number of negotiation rounds", default=20)
    args = parser.parse_args()

    agent = MiddleMan(args.id, args.pwd, rounds=args.rounds)
    agent.start()
