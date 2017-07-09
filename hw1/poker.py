#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета. Черный джокер '?B' может быть
# использован в качестве треф или пик любого ранга, красный
# джокер '?R' - в качестве черв и бубен люього ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------

from itertools import combinations, product
from pandas import Series
import numpy as np

def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов, отсортированный от большего к меньшему"""
    ranks = ['--23456789TJQKA'.index(r) for r, s in hand]
    ranks.sort(reverse = True)
    
    # Учитывать wheel (straight с туза - A2345)
    wheel = range(5, 0, -1)
    return wheel if ranks == [14, 5, 4, 3, 2] else ranks


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits = [s for r, s in hand]
    return len(set(suits)) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    for r in ranks:
        if ranks.count(r) == n:
            return r
    return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    pair = kind(2, ranks)
    lowpair = kind(2, list(reversed(ranks)))
    
    if pair and lowpair != pair:
        return (pair, lowpair)
    else:
        return None

# def all_max(iterable, key = None):
#    """Возвращает список всех элементов с максимальным значением"""
#    result = []
#    max_value = None
#    key = key or (lambda x: x)
#    
#    for x in iterable:
#        x_value = key(x)
#        if not result or x_value > max_value:
#            result = [x]
#            max_value = x_value
#        elif x_value == max_value:
#            result.append(x)
#    
#    return result
        
    
def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    cards_count = 5
    hands = combinations(hand, cards_count)
    
    # Возвращаем первую руку с максимальным рангом
    return max(hands, key = hand_rank)


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    
    hand_series = Series(hand)
    jokers = hand_series[hand_series.str.startswith('?')].index
    if np.any(jokers):       
        cards = '23456789TJQKA'
        red_cards = map(lambda x: ''.join(x), product(cards, 'DH'))
        black_cards = map(lambda x: ''.join(x), product(cards, 'CS'))
        
        used_cards = hand_series[~hand_series.str.startswith('?')]
        free_red_cards = list(set(red_cards) - set(used_cards))
        free_black_cards = list(set(black_cards) - set(used_cards))
        
        for joker in jokers:
            if hand[joker].endswith('R'):
                hand[joker] = free_red_cards
            else:
                hand[joker] = free_black_cards
            
        cards_list = map(lambda x: [x] if not isinstance(x, list) else x, hand)
        hands = list(product(*cards_list))
        
        cards_count = 5    
        max_ranks_list = []
        
        for curr_hand in hands:
            max_rank = max(combinations(curr_hand, cards_count), key = hand_rank)
            max_ranks_list.append(max_rank)
    else:
        return (best_hand(hand))
    
    return max(max_ranks_list, key = hand_rank)


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    return 'test_best_hand passes'
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
#    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
#            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
#    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
#            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'

if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
