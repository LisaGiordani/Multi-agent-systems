import random
import string
import time
from sys import argv
from typing import List, Dict

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import Behaviour
from pade.core.agent import Agent
from pade.misc.utility import start_loop, display_message

N_BIDDERS = 15
N_GOOD = 150
BUDGET = 10


def generate_good():
    return Good(random.random(), random.random(), random.random())


class Good:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return str(self.a) + ';' + str(self.b) + ';' + str(self.c)

    @classmethod
    def from_string(cls, message: string):
        a, b, c = [float(x) for x in message.split(';')]
        return cls(a, b, c)


class BidBehaviour(Behaviour):
    def bid(self, good):
        return min(utility(good, self.agent), self.agent.remaining_budget)

    def execute(self, message):
        # Receive the REQUEST message to send the utility and send INFORM with the overall_utility value
        if message.performative == ACLMessage.REQUEST:
            # display_message(self.agent.aid.name, "Request received")
            reply = ACLMessage(ACLMessage.INFORM)
            reply.add_receiver(message.sender)
            reply.set_content(self.agent.overall_utility)
            self.agent.send(reply)
            display_message(self.agent.aid.name, "Inform sent")

        # ------------- Question 6 ------------ #
        elif message.performative == ACLMessage.CFP:
            # Deserialize the content
            good = Good.from_string(message.content)

            # Create a proposal
            proposal = ACLMessage(ACLMessage.PROPOSE)
            proposal.add_receiver(message.sender)
            proposal.set_content(str(self.bid(good)))

            # Send the proposal
            self.agent.send(proposal)

        # If the performative is an ACCEPT_PROPOSAL
        elif message.performative == ACLMessage.ACCEPT_PROPOSAL:
            # Deserialize the content
            proposal_value, good = message.content.split(",")
            proposal_value = float(proposal_value)
            good = Good.from_string(good)

            # Compute the new budget of the agent
            self.agent.remaining_budget -= proposal_value

            # Compute new  utility of the agent
            self.agent.overall_utility += utility(good,
                                                  self.agent) - proposal_value

        # If the performative is a REJECT_PROPOSAL, do nothing


class RequestResults(Behaviour):
    """
    This behaviour is used to retrieve the utility of all the agent
    """

    def __init__(self, agent):
        super().__init__(agent)
        self.utilities = {}

    # First send a REQUEST message
    def on_start(self):
        message = ACLMessage(ACLMessage.REQUEST)
        for r in self.agent.receivers:
            message.add_receiver(r)
        self.agent.send(message)
        # display_message(self.agent.aid.name, "Request sent")

    # And receive the utility as INFORM
    def execute(self, message):
        if message.performative == ACLMessage.INFORM:
            # display_message(self.agent.aid.name, "Inform received")
            self.utilities[message.sender.name] = float(message.content)
            if len(self.utilities) == len(self.agent.receivers):
                display_message(self.agent.aid.name,
                                "Utilities:\n{}".format(self.utilities))
                self.agent.behaviours.remove(self)


class AuctioneerBehaviour(Behaviour):
    good: Good
    proposals: Dict[AID, float]

    # Define the price an agent will pay. This function must be overridden for the Vickrey version
    def price(self, sorted_proposals):
        return sorted_proposals[0][1]

    # To be executed when the behaviour is created;
    # creates a new good; sends a CFP to all the bidders
    def on_start(self):
        self.proposals = {}
        self.good = generate_good()
        message = ACLMessage(ACLMessage.CFP)
        for r in self.agent.receivers:
            message.add_receiver(r)
        message.set_content(str(self.good))
        self.agent.send(message)
        display_message(self.agent.aid.name,
                        'CFP sent to: {}'.format(self.agent.receivers))

    # Function that determines who will receive accept/reject and sends these messages
    def choose_accept_reject(self):
        sorted_proposals = [l for l in sorted(
            self.proposals.items(), key=lambda it: it[1], reverse=True)]
        accept = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
        accept.add_receiver(sorted_proposals[0][0])
        accept.set_content(
            str(self.price(sorted_proposals)) + ',' + str(self.good))
        reject = ACLMessage(ACLMessage.REJECT_PROPOSAL)
        # display_message(self.agent.aid.name, "Sent accept to: {} with value: {}".format(accept.receivers[0].name,
        #                                                                                 sorted_proposals[0][1]))
        for r in range(1, len(self.proposals)):
            reject.add_receiver(sorted_proposals[r][0])
            reject.set_content(sorted_proposals[r][1])
            # display_message(self.agent.aid.name, "Sent reject to: {}".format(sorted_proposals[r][0].name))
        self.agent.send(accept)
        self.agent.send(reject)

    # Main loop; executed when a message is received
    def execute(self, message):
        if message.performative == ACLMessage.PROPOSE:
            # display_message(self.agent.aid.name, "Received proposal from: {}".format(message.sender.name))
            self.proposals[message.sender] = float(message.content)
            if len(self.proposals) == len(self.agent.receivers):
                self.choose_accept_reject()
                self.agent.n_goods = self.agent.n_goods - 1
                if self.agent.n_goods != 0:
                    self.agent.initialize_send()
                else:
                    request_behaviour = RequestResults(self.agent)
                    self.agent.behaviours.append(request_behaviour)
                    request_behaviour.on_start()
                self.agent.behaviours.remove(self)


class VickreyBehaviour(AuctioneerBehaviour):
    # TODO: Implement the new price function for Vickrey auctions
    # ------------- Question 7 ------------ #
    def price(self, sorted_proposals):
        """Return second best proposal. """
        return sorted_proposals[1][1]
    # ------------- Fin Question 7 ------------ #



class AuctioneerAgent(Agent):
    """
    The class for the auctioneer
    """
    # ------------- Modifié pour Question 7 ------------ #
    def __init__(self, aid, vickrey:bool=False):
        super(AuctioneerAgent, self).__init__(aid=aid, debug=False)
        self.n_goods = N_GOOD
        self.vickrey = vickrey
        self.receivers = []
        self.call_later(8, self.initialize_send)

    def initialize_send(self):
        if not vickrey:
            auctioneer_behaviour = AuctioneerBehaviour(self)
        else:
            auctioneer_behaviour = VickreyBehaviour(self)
        self.behaviours.append(auctioneer_behaviour)
        auctioneer_behaviour.on_start()
    # ------------- Fin Question 7 ------------ #


class BidderAgent(Agent):
    """
    The class for the bidder
    """

    def __init__(self, aid, auctioneer_aid):
        super(BidderAgent, self).__init__(aid=aid, debug=False)
        self.overall_utility = 0
        self.a = random.random()
        self.b = random.random()
        self.c = random.random()
        self.auctioneer = auctioneer_aid
        self.remaining_budget = BUDGET
        self.behaviours.append(BidBehaviour(self))


def utility(good: Good, bidder: BidderAgent):
    return good.a * bidder.a + good.b * bidder.b + good.c * bidder.c



class TargetBidBehaviour(BidBehaviour):
    # TODO: Modify this function to bid unfaithfully
    # ------------- Question 6 ------------ #
    def bid(self, good):
        return (1-0.1)*min(utility(good, self.agent), self.agent.remaining_budget)


class TargetAgent(BidderAgent):

    def __init__(self, aid, auctioneer_aid):
        super(BidderAgent, self).__init__(aid=aid, debug=False)
        self.overall_utility = 0
        self.a = random.random()
        self.b = random.random()
        self.c = random.random()
        self.auctioneer = auctioneer_aid
        self.remaining_budget = BUDGET
        self.behaviours.append(TargetBidBehaviour(self))

    # ------------- Question 7 ------------ #
vickrey = True
    # ------------- Fin Question 7 ------------ #

if __name__ == '__main__':
    agents = []
    bidders = []

    port = int(argv[1])
    auctioneer_agent_name = 'auctioneer_{}@localhost:{}'.format(
        port - N_BIDDERS, port - N_BIDDERS)

    # ------------- Question 7 ------------ #
    auctioneer_agent = AuctioneerAgent(AID(name=auctioneer_agent_name), vickrey)
    # ------------- Fin Question 7 ------------ #

    for i in range(N_BIDDERS - 1):
        bidder_agent_name = 'bidder_agent_{}@localhost:{}'.format(
            port - i, port - i)
        bidder_agent = BidderAgent(
            AID(name=bidder_agent_name), auctioneer_agent_name)
        bidders.append(bidder_agent_name)
        agents.append(bidder_agent)

    bidder_agent_name = 'target_agent_{}@localhost:{}'.format(
        port - N_BIDDERS + 1, port - N_BIDDERS + 1)

    bidder_agent = TargetAgent(
        AID(name=bidder_agent_name), auctioneer_agent_name)

    bidders.append(bidder_agent_name)
    agents.append(bidder_agent)

    auctioneer_agent.receivers = bidders
    agents.append(auctioneer_agent)

    start_loop(agents)