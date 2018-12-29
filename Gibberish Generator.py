import random
import re

# Use any file with one word/item per line
with open("English dictionary.txt", encoding="utf-8") as file:
    words = file.readlines()
    for i in range(len(words)):
        words[i] = words[i].replace('\n', '')

class node:
    """To generate realistic words, the program stores the frequency of
    every substring found in words of the source text in a tree. Each
    node (other than the root) represents one substring. Each node is
    assigned one character, and the path from the root to any node
    spells out the substring of that node. Each node stores a number
    representing how many times its substring appears in the source
    text. For example, the node Root→T→H→I stores a number representing
    how many times the substring “thi” appeared in the source. A node
    can also represent how often the end of a word occurs after a
    certain substring.

    self.text -- the substring represented by this node
    self.freq -- the number of times this substring appeared
    self.children -- children of this node, representing all substrings
    found in the source that are formed by adding one character to the
    end of this node's substring. A dictionary mapping characters to
    the children that represent those characters."""
    
    def __init__(self, text):
        self.text = text
        self.freq = 0
        self.children = {}

    def get_freq(self):
        """Return the number of times this substring appeared."""
        return self.freq

    def get_text(self):
        """Return the substring of this node."""
        return self.text

    def get_children(self):
        """Return the children of this node."""
        return self.children

    def set_freq(self, new_freq):
        """Change the frequency to new_freq."""
        self.freq = new_freq

    def set_text(self, new_text):
        """Change this node's substring to new_text."""
        self.text = new_text

    def set_children(self, new_children):
        """Replace the children diectionary."""
        self.children = new_children

    def add_one(self):
        """Record one more instance of this substring found."""
        self.freq += 1

    def add(self, word):
        """Used with the root node to record one instance of a substring
        in the tree.
        Each iteration adds one to the frequency of the node and then,
        if characters remain in the input, recursively calls add on the
        next character on the substring. If add is called on (e.g.) 'abc',
        it will add 1 to the frequencies of 'a', 'ab', and 'abc'.
        """
        self.freq += 1
        if len(word) != 0:
            # If this substring hasn’t been recorded yet, add it to the tree
            if word[0] not in self.children:
                self.children[word[0]] = node(word[0])
            # Then, recursively call add
            self.children[word[0]].add(word[1:])
        else:
            # If this is the end of the word, then add one to the frequency of the end-of-word node
            if 'end' not in self.children:  # but first, add that node if it isn't there
                self.children['end'] = node('end')
            self.children['end'].add_one()

    def element(self, word):
        """Used with the root node to return a node corresponding to a
        particular substring (word).
        If the input has characters, go to the child node for the first
        character and recursively call element on it with the rest of
        the characters as input. For example, if word is 'abcd', go to
        the 'a' node and call element on it with word = 'bcd'.
        If the input has no characters, then we've reached the end of
        the recursion; return the node."""
        if word == '':
            return self
        else:
            if word[0] in self.children:
                return self.children[word[0]].element(word[1:])
            else:
                return None

def random_choice(items, probs):
    """Weighted randomn choice: choose a random item from items,
    where item[n] has a weight of probs[n] to be chosen."""
    # Randomly generate a number from 0 to the sum of all weights
    r = random.uniform(0, sum(probs))
    # Then find which item r corresponds to 
    so_far = 0
    for i in range(len(items)):
        so_far += probs[i]
        if r <= so_far:
            return items[i]

def has_vowel(text):
    """Used when generating two-letter words to make sure they have a vowel"""
    return 'a' in text or 'e' in text or 'i' in text or 'o' in text or 'u' in text or 'y' in text

def generate_word(tree, beginnings, words):
    """Builds the word one character at a time, adding to the end,
    making sure that short substrings of the word are realistic.

    tree -- the frequency of all substrings appearing anywhere
    beginnings -- the frequency of all substrings appearing at the
    beginning of a word
    words -- the list of all the real words used as the basis for
    generating gibberish words"""

    # When generating the next letter, look at the last few characters of
    # the word so far, and then for every character that could come next,
    # see how common it is in the source material for that character to
    # come after those last few characters. For example, if the word ends
    # in 'thi', then look in the tree for the frequency of 'thia', 'thib',
    # 'thic', etc. If you look only a few characters back, only smaller
    # patterns of the language show up in the generated words. If you look
    # farther back, longer patterns and roots show up. It is best when the
    # program looks both at short strings and long strings, because then
    # the words both have the longer roots and patterns and also have
    # parts that are totally unconnected from any roots.

    # min_ and max_reference_letters represent the range of substring
    # lengths from the end of the word the program should look at to
    # achieve that effect.
    
    min_reference_letters = 2
    max_reference_letters = 5
    word = ''  # The word to be built up
    # Determine whether to generate a word normally or to make a short
    # word (used when generating a vocabulary for generating gibberish
    # sentences, which needs one and two letter words).
    length_random = random.randint(0,100)  # Used for deciding whether to generate a short word
    length_choice = 0  # Represents how long the word should be (1 or 2 = 1 or 2 letter word; 0 = no limit)
    # 1% chance to generate 1-letter word
    if length_random == 0:
        length_choice = 1
    # 3% chance to generate 2-letter word
    elif length_random < 4:
        length_choice = 2
    # 96% chance to have length >2

    # If the word length is limited to have 1 or 2 letters:
    # Keep generating candidates until a suitable word is found.
    # Only set word to a value if it has a vowel, so if word = '', that
    # means it hasn't generated one with a vowel
    # And don't keep a candidate if it is already a real word (word in words)
    if length_choice > 0:
        while word == '' or word in words:
            # Set text to a randomly generated string of the right length
            text = ''
            # Save that string to the word only if it has a vowel
            word = ''
            current_node = beginnings
            # Randomly generate a 3-letter sequence, weighted according
            # to how often each sequence appears at the beginnings of words
            # Repeatedly add one letter based on weights, then go to
            # that letter's node and randomly generate the next letter
            for i in range(3):
                children = current_node.get_children()
                current_node = random_choice([children[child] for child in children], [children[child].get_freq() for child in children])
                text += current_node.get_text()
            # Cut this sequence to the desired length
            text = text[:length_choice]

            # If this word has a vowel, then save it as a candidate
            if has_vowel(text):
                word = text

    # If the word length is >2, keep generating candidate words
    # until you get one that is (1) not empty, (2) not a real word, and
    # (3) has a vowel.
    while word == '' or word in words or not has_vowel(word):
        word = ''
        stop = False
        # To start off the word:
        # Randomly generate a 3-letter sequence, weighted according
        # to how often each sequence appears at the beginnings of words
        # Repeatedly add one letter based on weights, then go to
        # that letter's node and randomly generate the next letter
        current_node = beginnings
        for i in range(3):
            children = current_node.get_children()
            current_node = random_choice([children[child] for child in children], [children[child].get_freq() for child in children])
            word += current_node.get_text()
        # Then, add more letters until the end-of-word node is chosen
        while not stop:
            letters = []  # All the letters that could come next
            probs = []  # The weights for each of those letters to be chosen
            # Look through every substring at the end of the word that
            # has a length between min_reference_letters and
            # max_reference_letters (or, if either of those is too long,
            # the whole word)
            for i in range(min(min_reference_letters, len(word)), min(max_reference_letters, len(word)) + 1):
                reference = word[-i:]  # The reference substring
                element = tree.element(reference)  # The node representing this substring
                if element != None:  # Only look at this substring if it actually appears somewhere in the source words
                    # Iterate through each of the letters that ever
                    # appears after this substring in the source
                    children = element.get_children()
                    for child in children:
                        # If this letter isn’t yet in the list of
                        # letters that could come next, add it (with a
                        # probability of 0)
                        if child not in letters:
                            letters.append(child)
                            probs.append(0)
                        # Then, add weight to the probability of this
                        # letter’s being added, based on how often it
                        # appears in the source

                        # Longer sequences will inherently be found less
                        # frequently (in an idealized model based on
                        # English letters, a sequence of length n will,
                        # on average, be 26 times less likely than a
                        # sequence of length n-1). So, correct for this
                        # by multiplying the frequency by 26^(length of
                        # reference substring).
                        if child == 'end':
                            # Add extra weight to the end-of-word option
                            # (I found that if I don’t, the words get
                            # too long).
                            probs[letters.index(child)] += children[child].get_freq() * (26 ** i) * 1.5 
                        else:
                            probs[letters.index(child)] += children[child].get_freq() * (26 ** i)
            # Now, letters contains every letter that comes after any of
            # the reference substrings looked at, and probs contains
            # their weights
            # Based on those weights, choose the next letter to add
            next_letter = random_choice(letters, probs) 
            if next_letter == 'end':
                # If the end-of-word is chosen, don't keep adding letters
                stop = True
            else:
                # If an actual letter is chosen, add that to the end
                word += next_letter
    return word

def generate_vocabulary(num_words, tree, beginnings, words):
    """Used when generating sentences and paragraphs so that there are
    some common words that are repeated multiple times.

    num_words -- how many words this vocabulary should have
    tree -- the frequency of all substrings appearing anywhere
    beginnings -- the frequency of all substrings appearing at the
    beginning of a word
    words -- the list of all the real words used as the basis for
    generating gibberish words"""

    # Shorter words should generally be more common, so when generating
    # words, sort them by length
    words_by_length = {}  # Holds all the words, with words of the same length grouped together in lists
    lengths = []  # All the word lengths represented in words_by_length
    i = 0
    # Generate num_words words, and put them in words_by_length
    while i < num_words:
        word = generate_word(tree, beginnings, words)
        length = len(word)
        # If no word of this length has been added, add a new empty list
        # to words_by_legnth corresponding to this length of word, and
        # record in lengths that this is one of the word lengths
        # represented
        if length not in words_by_length:
            words_by_length[length] = []
            lengths.append(length)
        # Only add the word and increment i if the word hasn't already
        # been generated
        if word not in words_by_length[length]:
            words_by_length[length].append(word)
            i += 1
    # Put all the words generated in the list words, in increasing order
    # of length
    lengths.sort()
    words = []
    for length in lengths:
        words += words_by_length[length]
    # Mix up words a bit, so that shorter words aren’t always more
    # frequent than longer words
    # Do this by repeatedly swapping pairs of words whose indices are
    # within section of each other
    section = len(words) // 7
    for i in range(len(words) - section):
        for j in range(section):
            random_1 = random.randint(i, i + section)
            random_2 = random.randint(i, i + section)
            random_word_1 = words[random_1]
            words[random_1] = words[random_2]
            words[random_2] = random_word_1
    # Give each word a probability inversely proportional to its index
    probs = [i ** (-1) for i in range(1, len(words) + 1)]
    return [words, probs]

def generate_sentence(vocabulary):
    """Generates a sentence using a given vocabulary. The input
    vocabulary is in the same format as the output of
    generate_vocabulary: a list whose first item is a list of words and
    whose second item is the frequencies of those words."""
    
    vocab_words = vocabulary[0]
    vocab_probs = vocabulary[1]
    sentence_list = []  # The list of words in the sentence
    length = random.randint(3, 20) # The number of words to put in the sentence
    while len(sentence_list) < length:
        # Generate a word
        word = random_choice(vocab_words, vocab_probs)
        # Add it to the sentence, but only if it's not already the last
        # word in the sentence (to avoid repeats)
        if len(sentence_list) == 0 or (len(sentence_list) > 0 and sentence_list[-1] != word):
            # Occasionally add a punctuation mark after a word, but only
            # if it's not the last word in the sentence
            if len(sentence_list) < length - 1:
                word += random_choice(['', ',' ';'], [85, 10, 5])
                # (85% chance of not adding anything after the word)
            sentence_list.append(word)
    # Join all the words together and capitalize the first word
    sentence = ' '.join(sentence_list)
    sentence = sentence[0].capitalize() + sentence[1:]
    # Add a punctuation mark to the end
    sentence += random_choice(['.', '?', '!'], [90, 6, 4])
    return sentence

# Form the trees that will be used to generate words           
tree = node('')
beginnings = node('')

num_words = len(words)
print('Loading ' + str(num_words) + ' words…')
for i in range(num_words):
    if i != 0 and i % (num_words // 10) == 0:
        print(str(int(10 * i / (num_words // 10))) + '%')  # status updates
    word = words[i]
    # node.add only adds the substrings that start from the beginning —
    # so, for example, node.add('abcd') only adds 'a', 'ab', 'abc', and
    # 'abcd.' To add the rest of the substrings, need to also call it on
    # 'bcd', 'cd', and 'd'.
    for j in range(len(word)):
        tree.add(word[j:])
    # because beginnings will always be used to generate 3-letter
    # sequences, don't add words to it that are less than 3 letters
    if len(word) >= 3:
        beginnings.add(word)

vocabulary = None  # Will be used if the user wants to generate a sentence/paragraph

print('Done loading.\n\nPress enter to generate a new word.\nType p and press enter to generate a paragraph.')

# This part lets the user generate words/sentences/paragraphs
while(True):
    s = input()
    if s == '':
        print(generate_word(tree, beginnings, words))
    elif s == 'p' or s == 'P':  # Generate a paragraph
        if vocabulary == None:  # Generate a vocabulary (of 1000 words) if that hasn't been done yet
            print('Generating vocabulary…')
            vocabulary = generate_vocabulary(1000, tree, beginnings, words)
            print('Done.\n')
        # Generate sentences and join them together
        sentences = []
        for i in range(random.randint(2, 15)):
            sentences.append(generate_sentence(vocabulary))
        print(' '.join(sentences))
    elif s == 'v' or s == 'V':  # Re-generate a new vocabulary
        print('Generating vocabulary…')
        print('Done.\n')
    elif s == 's' or s == 'S':  # Generate a sentence
        if vocabulary == None:
            print('Generating vocabulary…')
            vocabulary = generate_vocabulary(1000, tree, beginnings, words)
            print('Done.\n')
        print(generate_sentence(vocabulary))
    elif re.match('^[0-9]+$', s) != None:  # If the user enters a number, generate that many gibberish words
        p = ''
        for i in range(int(s)):
            p += generate_word(tree, beginnings, words) + ' '
        p = p[:-1]
        print(p)
