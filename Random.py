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
    Strategija pregovaranja: Random

    Pokretanje: python Random.py -v p -s lgaric@jix.im -mp "{'kava': 25, 'čaj': 20}" -jid babajaga123@jix.im -pwd lozinka

"""

class Pregovaratelj(Agent):

    """Sudionik u pregovaranju."""

    def __init__(self, *args, vrsta, sugovornik, mojaPonuda, **kwargs):
        super().__init__(*args, **kwargs)
        self.sugovornik = sugovornik
        self.mojaPonuda = literal_eval(mojaPonuda)
        self.vrsta = vrsta

    class InicijalnaPonuda(OneShotBehaviour):
        """Slanje inicijalne ponude."""

        async def run(self):
            msg = Message(
                to=self.agent.sugovornik,
                metadata={"ontology": "pregovaranje"},
                body=f"{self.agent.mojaPonuda}")
            self.agent.say(f"Saljem poruku: {msg.body}")
            await self.send(msg)

    class Pregovaranje(CyclicBehaviour):
        """Ponasanje koje vodi proces pregovaranja i obraduje poruke iz procesa pregovaranja."""

        async def run(self):
            msg = Message()
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.say(f"Dobio sam ponudu: {msg.body}")
                if msg.body in ["odbij", "prihvati"]:
                    await self.agent.stop()
                else:
                    ponuda = literal_eval(msg.body)
                    interpretacija = self.interpretiraj(ponuda)

                    msg = msg.make_reply()

                    if interpretacija in ["odbij", "prihvati"]:
                        msg.body = interpretacija
                        await self.send(msg)
                        await self.agent.stop()
                    else:
                        msg.body = f"{interpretacija}"
                        sleep(1)
                        await self.send(msg)

        def interpretiraj(self, ponuda):
            print("~~~~~~~~~~~~~~~~~~~~")
            if self.agent.vrsta in ["prodavac", "p"]:
                print(f"# {self.agent.vrijeme}")
            self.agent.vrijeme -= 1
            if self.agent.vrijeme == 0:
                self.agent.say(f"Odbijam ponudu zbog isteka vremena: {ponuda}")
                return "odbij"
            else:
                self.agent.mojaPonuda = self.generirajPonudu(ponuda)
                if self.agent.vrsta in ["kupac", "k"]:
                    if self.evaluiraj(self.agent.mojaPonuda) + 1 >= self.evaluiraj(ponuda):
                        self.agent.say(f"Prihvacam ponudu: {ponuda}")
                        return "prihvati"
                    else:
                        self.agent.say(f"Dajem protuponudu: {self.agent.mojaPonuda}")
                        return self.agent.mojaPonuda
                else:
                    if self.evaluiraj(self.agent.mojaPonuda) - 1 <= self.evaluiraj(ponuda):
                        self.agent.say(f"Prihvacam ponudu: {ponuda}")
                        return "prihvati"
                    else:
                        self.agent.say(f"Dajem protuponudu: {self.agent.mojaPonuda}")
                        return self.agent.mojaPonuda

        def evaluiraj(self, ponuda):
            return sum([i for i in ponuda.values()])

        def generirajPonudu(self, ponuda):
            protuponuda = {}
            # CopyKitten - Varam ako me sugovornik dva puta zaredom prevario
            if self.sugovornikVarao(ponuda):
                if self.agent.sugovornikPrijeVarao:
                    self.agent.varam = True
                    self.agent.say(f"Varao me 2 puta: Varam: {self.agent.varam}")
                else:
                    self.agent.sugovornikPrijeVarao = True
                    self.agent.varam = self.varam()
                    self.agent.say(f"Varao me 1 puta: Varam: {self.agent.varam}")
            else:
                self.agent.varam = self.varam()
                self.agent.sugovornikPrijeVarao = False
                self.agent.say(f"Nije me varao: Varam: {self.agent.varam}")

            if self.agent.vrsta in ["kupac", "k"]:
                for proizvod, cijena in self.agent.mojaPonuda.items():
                    if self.agent.varam:
                        novaCijena = cijena - (ponuda[proizvod] - cijena) / 10.0
                        protuponuda[proizvod] = round(novaCijena, 2)
                    else:
                        if self.agent.vrijeme > 15:
                            novaCijena = cijena + (ponuda[proizvod] - cijena) / self.agent.vrijeme
                            protuponuda[proizvod] = round(novaCijena, 2)
                        elif self.agent.vrijeme > 10:
                            novaCijena = cijena + (ponuda[proizvod] - cijena) / (self.agent.vrijeme / 2)
                            protuponuda[proizvod] = round(novaCijena, 2)
                        elif self.agent.vrijeme > 5:
                            novaCijena = cijena + (ponuda[proizvod] - cijena) / (self.agent.vrijeme / 3)
                            protuponuda[proizvod] = round(novaCijena, 2)
            else:
                for proizvod, cijena in self.agent.mojaPonuda.items():
                    if self.agent.varam:
                        novaCijena = cijena + (cijena - ponuda[proizvod]) / 60.0
                        protuponuda[proizvod] = round(novaCijena, 2)
                    else:
                        if self.agent.vrijeme > 15:
                            novaCijena = cijena - (cijena - ponuda[proizvod]) / (self.agent.vrijeme * 6)
                            protuponuda[proizvod] = round(novaCijena, 2)
                        elif self.agent.vrijeme > 10:
                            novaCijena = cijena - (cijena - ponuda[proizvod]) / (self.agent.vrijeme * 2)
                            protuponuda[proizvod] = round(novaCijena, 2)
                        elif self.agent.vrijeme > 5:
                            novaCijena = cijena - (cijena - ponuda[proizvod]) / (self.agent.vrijeme / 2)
                            protuponuda[proizvod] = round(novaCijena, 2)
            self.agent.proslaPonuda = ponuda
            return protuponuda

        def varam(self):
            broj = random.randint(0,100)
            if broj <= 25: # 25% sanse da sugovornik vara
                return True
            else:
                return False


        def sugovornikVarao(self, ponuda):
            if len(self.agent.proslaPonuda) is 0: # Prva ponuda
                self.agent.proslaPonuda = ponuda
                return False
            for proizvod, cijena in self.agent.proslaPonuda.items():
                if self.agent.vrsta in ["kupac", "k"]:
                    if cijena < ponuda[proizvod]: # Ponudac ponudio vecu ponudu (varao)
                        return True
                else:
                    if cijena > ponuda[proizvod]: # Kupac ponudio manju ponudu (varao)
                        return True
            return False 


    def say(self, msg):
        print(f"[Random] {self.name}: {msg}")

    async def setup(self):
        self.say("Starting!")
        self.vrijeme = 20
        self.sugovornikPrijeVarao = False
        self.proslaPonuda = {}
        self.varam = False

        ponasanjePregovaranje = self.Pregovaranje()
        predlozakPregovaranje = Template(metadata={"ontology": "pregovaranje"})
        self.add_behaviour(ponasanjePregovaranje, predlozakPregovaranje)

        if self.vrsta in ["kupac", "k"]:
            ponasanjeInicijalnaPonuda = self.InicijalnaPonuda()
            self.add_behaviour(ponasanjeInicijalnaPonuda)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vrsta", type=str, help="Vrsta agenta (k ili p ili kupac ili prodavac)")
    parser.add_argument("-s", "--sugovornik", type=str, help="JID prodavaca", default="babajaga123@jix.im")
    parser.add_argument("-mp", "--mojaPonuda", help="Inicijalna ponuda agenta, u obliku {'stvar1':cijena1, 'stvar2':cijena2}")
    parser.add_argument("-jid", type=str, help="JID kupca")
    parser.add_argument("-pwd", type=str, help="Lozinka kupca", default="tajna")
    args = parser.parse_args()

    agent = Pregovaratelj(args.jid, args.pwd, vrsta=args.vrsta, sugovornik=args.sugovornik, mojaPonuda=args.mojaPonuda)
    agent.start()
