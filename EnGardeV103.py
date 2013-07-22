#  ===En Garde===
# (Basic Game)
# Version: 1.0.3
#
# Original game by Reiner Knizia: http://www.knizia.de
# Full rules available at:
# http://freespace.virgin.net/chris.lawson/rk/engarde/rules.htm
#
# Program designed & coded by Robert Boily
#
# One week from 'Hello world' to this!
# The code is presented unmodified from that version, other than bugfixes.
#
# There are ways I would change the code to make it more readable, more
# pythonic, but this gives you an understanding of how quickly I learn new
# programming concepts.

import collections
import random
import sys

def setupBoard(board, boardLength):
    # Places the pieces in starting positions
    # Keep in mind that space 1 when the board is drawn is index 0 in the board list
    board[0] = 'X'
    board[boardLength - 1] = 'O'


def drawBoard(board):
    # First row.
    for i in range(len(board)):
        print(' ', end='')
        print(i+1, end='') # i+1 because there is no space 0
        if i < 9: # Extra space for single-digit numbers
            print(' ', end='')
    print()
    
    # Second row.
    hline = '+'
    for i in range(len(board)):
        hline += '--+'
    print(hline)

    # Third row, calls data from board
    print('|', end='')
    for i in range(len(board)):
        print(' ' + board[i] + '|', end='')
    print()

    # Fourth row, same as second row.
    print(hline)

    # Fifth row, shows scores and deck.
    print('Your score: ' + str(xScore) + ' ' * 15, end='')
    print('Deck: ' + str(len(gameDeck)), end = '')
    print(' ' * 15 + "Opponent's score: " + str(oScore))
    

def setupDeck(deck, lowestCard, highestCard, cardCopies):
    # Returns a shuffled En Garde-style deck with the specified parameters.
    # deck should be an empty list when passed
    while cardCopies > 0:    
        for i in range(lowestCard, highestCard + 1):
            deck.append(i)
        cardCopies -= 1
    random.shuffle(deck)
    

def dealHands(deck, handSize, xHand, oHand):
    for i in range(handSize):
        dealCard(deck, xHand)
        dealCard(deck, oHand)


def dealCard(deck, hand):
    # Takes the top card of the deck and adds it to the hand, removing that card from the deck.
    # If the deck is empty, instead returns False
    if deck == []:
        return False
    hand.append(deck[0])
    hand.sort()
    del deck[0]


def getRandomPlayer():
    if random.randint(0, 1) == 0:
        return 'X'
    else:
        return 'O'

  
def getXMove(xHand, LOWEST_CARD, HIGHEST_CARD):
    # Asks the player for a move, checks that the input is a card in their hand and a direction left or right.
    # Returns [number on card, direction]
    while True:
        print('Your hand: ' + str(xHand)) 
        print("Which card will you play? (the card's value, %s - %s, or quit)" % (LOWEST_CARD, HIGHEST_CARD))
        moveNum = input()
        if moveNum.lower().startswith('q'):
            sys.exit()
        if not moveNum.isdigit() or not int(moveNum) in xHand:
            print("That is not a card in your hand. Please input a single digit that is listed among the cards in your hand.")
            continue
            
        # Here, we know that moveNum is a single, positive integer, that is in xHand.
        while True:
            moveNum = int(moveNum)
            print('Which direction will you move? (left, right, or cancel)')
            moveDir = input()
            if moveDir.lower().startswith('c'):
                break # Make sure there's nothing after this loop
            if moveDir.lower().startswith('l'):
                return moveNum, 'l'
            if not moveDir.lower().startswith('r'):
                print("Please choose a direction. Input 'left' or 'l' for left, 'right' or 'r' for right, 'cancel' or 'c' to choose a different card.")
                continue
            else:
                return moveNum, 'r'
            
            
def isHit(board, moveNum, moveDir, player):
    # Returns False for non-hits, returns True for hits.
    startPoint = getPlayerLocation(board, player)
    if player == 'X':
        otherPlayer = 'O'
    else:
        otherPlayer = 'X'
        
    if moveDir == 'l':
        moveNum *= -1
        if startPoint + moveNum < 0:
            return False
        
    if not startPoint + moveNum >= len(board) and board[startPoint + moveNum] == otherPlayer: ## Fixed bug
        return True
    else:
        return False


def isValidMove(board, moveNum, moveDir, player):
    # Returns False for invalid moves, True for valid ones. 
    startPoint = getPlayerLocation(board, player)
    if player == 'X':
        otherPlayer = 'O'
        
        if moveDir == 'l':
            if startPoint < moveNum:
                return False
            else:
                return True
        else:
            opponentPoint = getPlayerLocation(board, otherPlayer)
            if startPoint + moveNum > opponentPoint:
                return False
            else:
                return True

    if player == 'O':
        otherPlayer = 'X'

        if moveDir == 'r':
            if moveNum + startPoint > len(board) - 1:
                return False
            else:
                return True
                
        else:
            opponentPoint = getPlayerLocation(board, otherPlayer)
            if startPoint - moveNum < opponentPoint:
                return False
            else:
                return True     
    

def getPlayerLocation(board, player):
    # Returns the board index the player is on (1 lower than the label).
    for i in range(len(board)):
        if board[i] == player:
            return i


def makeMove(board, deck, discard, hand, moveNum, moveDir, player):
    # We know a valid, non-hit move has been passed, so move the pieces, play the card, add a new card.
    hand.remove(moveNum)
    dealCard(deck, hand)
    discard.append(moveNum)
    
    startPoint = getPlayerLocation(board, player)

    if moveDir == 'l':
        moveNum *= -1

    endPoint = startPoint + moveNum
    board[startPoint] = ' '
    board[endPoint] = player


def getOMove(LOWEST_CARD, HIGHEST_CARD, CARD_COPIES, board, oHand, discard):
    # The AI! Returns moveNum, moveDir
    xPoint = getPlayerLocation(board, 'X')
    oPoint = getPlayerLocation(board, 'O')
    distance = oPoint - xPoint
    if distance in oHand: # If I can score a hit, do so
        return distance, 'l'
    
    possibleMoves = getPossibleMoves(oHand)
    validMoves = []
    for i in possibleMoves:
        if isValidMove(board, i[0], i[1], 'O'):
            validMoves.append(i)

    # validMoves is now a list of valid, non-hit moves that can be played with a card in oHand [moveNum, moveDir]
    validMoves.sort(reverse=True) # Higher left moves are preferable.
    safeRanges = getSafeRanges(LOWEST_CARD, HIGHEST_CARD, CARD_COPIES, board, oHand, discard)
    for i in validMoves: # Make a high left move first
        if i[1] == 'l': # Could probably do this with some kind of advanced sorting method and remove earlier sort
            if distance - i[0] in safeRanges:
                return i
    validMoves.reverse() # Lower right moves are preferable.
    for i in validMoves:
        if i[1] == 'r':
            if distance + i[0] in safeRanges:
                return i
            
    # If we can score a hit or move to a safe space, we have returned that move. So, make a random move.
    return validMoves[random.randint(0, len(validMoves) - 1)]    
        

def getPossibleMoves(hand):
    # Returns a list of possible moves based on cards in hand, including invalid ones. Format [moveNum, moveDir]
    handDupe = []
    for i in hand:
        handDupe.append([i, 'l'])
        handDupe.append([i, 'r'])
    return handDupe

        
def getSafeRanges(LOWEST_CARD, HIGHEST_CARD, CARD_COPIES, board, oHand, discard):
    # Returns a list of safe ranges to be at
    safeRanges = []
    cardsSeen = collections.Counter(discard) + collections.Counter(oHand)
    for i in cardsSeen:
        if cardsSeen[i] == CARD_COPIES:
            safeRanges.append(i)

    if LOWEST_CARD - 1 > 0:
        safeRanges.append(LOWEST_CARD - 1)
        
    safeRanges.append(HIGHEST_CARD + 1)
    for i in range(HIGHEST_CARD + 1, len(board)):
        safeRanges.append(i)
            
    return safeRanges


def canPlayerMove(board, hand, player):
    possibleMoves = getPossibleMoves(hand)
    for i in possibleMoves:
        if isValidMove(board, i[0], i[1], player):
            return True
    return False     


# Establish deck parameters. AI can adapt to changes made here.
LOWEST_CARD = 1
HIGHEST_CARD = 5
CARD_COPIES = 5

# Establish game parameters
HAND_SIZE = 5 # Unintended consequences will result if there are more cards in the starting hands than there are in the deck.
BOARD_LENGTH = 23 # Formatting problems begin around 26. AI can adapt to changes.
MAX_SCORE = 5

# Set starting scores; adjust to start with a handicap.
xScore = 0
oScore = 0

turn = ' '
pointWinner = ' '


# Variable definitions done
print('===En Garde===')
print('(Basic Game)')
print()
print('Original game by Reiner Knizia: http://www.knizia.de/')
print()
print('Designed and coded by Robert Boily')
print()
print('View instructions? (y/n)')
if str(input()).lower().startswith('y'):
    # For displaying an example board with starting positions along with the instructions.
    board = [' '] * BOARD_LENGTH
    gameDeck = []
    gameDiscard = []
    xHand = []
    oHand = []

    setupDeck(gameDeck, LOWEST_CARD, HIGHEST_CARD, CARD_COPIES)
    dealHands(gameDeck, HAND_SIZE, xHand, oHand)
    setupBoard(board, BOARD_LENGTH)
    drawBoard(board)
    print()
    print('The game is played in matches, composed of several points. The first player to')
    print('win %s points wins the match.' % (MAX_SCORE))
    print()
    print('In each point, two fencers face each other across a piste, %s spaces long.' % (BOARD_LENGTH))
    print('Your fencer is represented by the X. Your opponent, by the O.')
    print()
    print('Players alternate turns. For the first point, the starting player is determined')
    print('randomly. The players alternate going first in subsequent points.')
    print()
    print('Each player is dealt %s cards from the deck. Each card has a number on it, from' % (HAND_SIZE))
    print('%s to %s. (For reference, the deck contains %s cards of each number.)' % (LOWEST_CARD, HIGHEST_CARD, CARD_COPIES))
    print()
    print('Press Enter to continue.')
    input()

    print("On each player's turn, they play a card from their hand, then move that many")
    print("spaces, either left or right. After moving, the player draws another card from")
    print("the deck. A player cannot move past their opponent or off the edge of the board.")
    print()
    print("If a player moves exactly onto their opponent, they have made a hit. They score")
    print('a point, and the fencers are returned to their starting positions. The deck is')
    print("reshuffled, including cards played and both players' hands. New hands are dealt,", end='')
    print("and another point is played.")
    print()
    print('Press Enter to continue.')
    input()

    print('If a player cannot make a valid move on their turn, they lose the point as if')
    print('their opponent had scored a hit.')
    print()
    print('When a player takes the last card from the deck, the fencers can no longer be')
    print('moved. The other player then has one last chance to score a hit and win the')
    print('point. If they cannot, the point is won by the player who is furthest from their', end='')
    print('own side of the board. In case of a tie, the point is a draw.')
    print()
    print('Press Enter to continue.')
    input()    
    
          
# Sets up new game.
# Build board data framework, create empty lists for passing.
while True:
    board = [' '] * BOARD_LENGTH
    gameDeck = []
    gameDiscard = []
    xHand = []
    oHand = []

    setupBoard(board, BOARD_LENGTH)
    setupDeck(gameDeck, LOWEST_CARD, HIGHEST_CARD, CARD_COPIES)
    dealHands(gameDeck, HAND_SIZE, xHand, oHand)
    
    gameIsPlaying = True
    lastTurn = False
    
    if turn == ' ':
        turn = getRandomPlayer()
    else:
        if turn == 'X':
            turn = 'O'
        else:
            turn = 'X'
                
    if pointWinner == 'X': # Assigns score from the last game, reports match win if appropriate.
        xScore += 1
        if xScore == MAX_SCORE:
            print('You have won the match, %s to %s! Congratulations!' % (xScore, oScore))
    if pointWinner == 'O':
        oScore += 1
        if oScore == MAX_SCORE:
            print('You have lost the match, %s to %s!' % (oScore, xScore))

    if xScore == MAX_SCORE or oScore == MAX_SCORE:
        print('Would you like to play another match? (y/n)')
        playAgain = input()
        if playAgain.lower().startswith('y'):
            xScore = 0
            oScore = 0
            pointWinner = ' '
            continue
        else:
            print('Goodbye!')
            sys.exit
            

    # Start playing a game.
    print()
    print('===NEW POINT===')
    drawBoard(board)
    print('Your hand: ' + str(xHand))
    print()
    print(turn + ' will play first.')
    print('Press Enter to continue.')
    input()
    
    while gameIsPlaying:
        # Check that the active player can make a move. If not, set pointWinner and gameIsPlaying,
        # and break out of the loop.
        if turn == 'X':
            if not canPlayerMove(board, xHand, turn):
                print('Your hand: ' + str(xHand))
                print('You have no valid moves available. Your opponent wins the point!')
                pointWinner = 'O'
                gameIsPlaying = False
                break
            
        else:
            if not canPlayerMove(board, oHand, turn):
                print("Opponent's hand: " +str(oHand))
                print('Your opponent has no valid moves available. You win the point!')
                pointWinner = 'X'
                gameIsPlaying = False
                break
            
        if gameDeck == []:
            print('The deck is empty! The fencers can no longer be moved!')
            print(turn + ' has one last chance to score a hit.')
            print('If ' + turn + ' cannot score a hit, the point will go to the player furthest from')
            print('their end of the board, with a tie resulting in a draw.')
            print('Press Enter to continue.')
            input()
            lastTurn = True           

                
        if turn == 'X': # Player turn
            drawBoard(board)
            moveNum, moveDir = getXMove(xHand, LOWEST_CARD, HIGHEST_CARD)
            if isHit(board, moveNum, moveDir, turn):
                print('You have scored a hit!')
                gameIsPlaying = False
                pointWinner = 'X'
                break
                
            if isValidMove(board, moveNum, moveDir, 'X') == False:
                print('That is not a valid move. You cannot move off the edge of the board or past your opponent.')
                print()
                continue
            
            # We now have a valid, non-hit move stored in moveNum and moveDir.
            if lastTurn:
                print('You have not scored a hit...')
            else:
                makeMove(board, gameDeck, gameDiscard, xHand, moveNum, moveDir, turn)
                turn = 'O'            
            
            # Show the player their move.
            print()        
            drawBoard(board)
            print('Press Enter to continue.')
            input()
            

        if turn == 'O': # Computer turn
            moveNum, moveDir = getOMove(LOWEST_CARD, HIGHEST_CARD, CARD_COPIES, board, oHand, gameDiscard)
            
            if isHit(board, moveNum, moveDir, turn):
                print('Your opponent has played a %s and scored a hit!' % (moveNum))
                pointWinner = 'O'
                gameIsPlaying = False
                break

            if lastTurn:
                print('Your opponent cannot score a hit...')                

            else:
                makeMove(board, gameDeck, gameDiscard, oHand, moveNum, moveDir, turn)
                turn = 'X'
                if moveDir == 'l':
                    moveDir = 'left'
                else:
                    moveDir = 'right'                                
                print('Your opponent played a %s and moved %s.' % (moveNum, moveDir))                             
                print()
                print('Press Enter to continue.')
                input()
                if lastTurn:
                    drawBoard(board)
                
        if lastTurn: # Handles empty deck after the last-chance-for-hit 
            if getPlayerLocation(board, 'X') > BOARD_LENGTH - 1 -getPlayerLocation(board, 'O'):
                pointWinner = 'X'
                gameIsPlaying = False
                print('You win the point!')
                break
            if getPlayerLocation(board, 'X') < BOARD_LENGTH - 1 -getPlayerLocation(board, 'O'):
                pointWinner = 'O'
                gameIsPlaying = False
                print('Your opponent wins the point!')
                break
            else:
                pointWinner = 'Draw'
                gameIsPlaying = False
                print('The point ends in a draw!')
                break
