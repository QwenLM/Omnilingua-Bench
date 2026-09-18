import re
import json

class Instruction:
    def __init__(self, language='zh'):
        self.language = language

    def build_description(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")

    def check_following(self, response):
        """
        Evaluate the response and return a score between 0 and 1.
        """
        raise NotImplementedError("Subclasses must implement this method")


class KeywordFrequency(Instruction):
    relation_mapping = {
        'zh': {"at_least": "最少", "exactly": "正好", "at_most": "最多"},
        'en': {"at_least": "at least", "exactly": "exactly", "at_most": "at most"},
        'ja': {"at_least": "最低", "exactly": "ちょうど", "at_most": "最大"},
        'fr': {"at_least": "au moins", "exactly": "exactement", "at_most": "au plus"},
        'ms': {"at_least": "sekurang-kurangnya", "exactly": "tepat", "at_most": "paling banyak"},
        'tgl': {"at_least": "hindi bababa sa", "exactly": "eksaktong", "at_most": "hindi hihigit sa"},
        'it': {"at_least": "almeno", "exactly": "esattamente", "at_most": "al massimo"},
        'bn': {"at_least": "কমপক্ষে", "exactly": "ঠিক", "at_most": "সর্বাধিক"},
        'id': {"at_least": "setidaknya", "exactly": "tepat", "at_most": "paling banyak"},
        'qu': {"at_least": "aswan", "exactly": "hunt'asqa", "at_most": "asllapas"},
        'zu': {"at_least": "okungenani", "exactly": "ncamashi", "at_most": "kungazidluli"},
        'mg': {"at_least": "farafahakeliny", "exactly": "marina", "at_most": "farafahabetsaka"},
        'sv': {"at_least": "minst", "exactly": "exakt", "at_most": "högst"},
        'ro': {"at_least": "cel puțin", "exactly": "exact", "at_most": "cel mult"},
        'tr': {"at_least": "en az", "exactly": "tam olarak", "at_most": "en fazla"},
        'ta': {"at_least": "குறைந்தது", "exactly": "சரியாக", "at_most": "அதிகபட்சம்"},
        'hy': {"at_least": "առնվազն", "exactly": "ճիշտ", "at_most": "առավելագույնը"},
        'ko': {"at_least": "최소", "exactly": "정확히", "at_most": "최대"},
        'te': {"at_least": "కనీసం", "exactly": "ఖచ్చితంగా", "at_most": "గరిష్టంగా"},
        'ka': {"at_least": "მინიმუმ", "exactly": "ზუსტად", "at_most": "მაქსიმუმ"},
        'ky': {"at_least": "кеминде", "exactly": "так", "at_most": "көбүнчө"},
        'pt': {"at_least": "pelo menos", "exactly": "exatamente", "at_most": "no máximo"},
        'hi': {"at_least": "कम से कम", "exactly": "ठीक", "at_most": "अधिक से अधिक"}
    }

    def build_description(self, relation, word_num, word):
        natural_relation = self.relation_mapping[self.language].get(relation, relation)
        self.word_num = word_num
        self.word = word
        self.relation = relation

        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回复中，词语\"{word}\"应{natural_relation}出现{word_num}次。"
        elif self.language == 'en':
            return f"In the response, the word or phrase \"{word}\" should appear {natural_relation} {word_num} times."
        elif self.language == 'ja':
            return f"回答の中で、言葉または語句\"{word}\"は{natural_relation}{word_num}回出現する必要があります。"
        elif self.language == 'fr':
            return f"Dans la réponse, le mot ou l'expression \"{word}\" doit apparaître {natural_relation} {word_num} fois."
        elif self.language == 'ms':
            return f"Dalam jawapan, perkataan atau frasa \"{word}\" hendaklah muncul {natural_relation} {word_num} kali."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, ang salitang \"{word}\" ay dapat {natural_relation} lumabas ng {word_num} beses."
        elif self.language == 'it':
            return f"Nella risposta, la parola o la frase \"{word}\" dovrebbe apparire {natural_relation} {word_num} volte."
        elif self.language == 'bn':
            return f"প্রতিক্রিয়ায়, \"{word}\" শব্দ {natural_relation} {word_num} বার দেখা উচিত।"
        elif self.language == 'id':
            return f"Dalam tanggapan Anda, kata atau frasa \"{word}\" harus muncul {natural_relation} {word_num} kali."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, \"{word}\" nisqa simita {natural_relation} {word_num} kuti rikurinan."
        elif self.language == 'zu':
            return f"Empendulweni yakho, igama \"{word}\" kufanele livele {natural_relation} {word_num}."
        elif self.language == 'mg':
            return f"Amin'ny valinteninao, ny teny \"{word}\" dia tokony hiseho {natural_relation} {word_num}."
        elif self.language == 'sv':
            return f"I svaret ska ordet eller frasen \"{word}\" förekomma {natural_relation} {word_num} gånger."
        elif self.language == 'ro':
            return f"În răspuns, cuvântul sau expresia \"{word}\" trebuie să apară {natural_relation} de {word_num} ori."
        elif self.language == 'tr':
            return f"Yanıtınızda, \"{word}\" kelimesi veya ifadesi {natural_relation} {word_num} kez görünmelidir."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில், \"{word}\" என்ற சொல் {natural_relation} {word_num} முறை தோன்ற வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում \"{word}\" բառը պետք է հայտնվի {natural_relation} {word_num} անգամ։"
        elif self.language == 'ko':
            return f"답변에서 \"{word}\" 단어가 {natural_relation} {word_num}번 나타나야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో \"{word}\" అనే పదం {natural_relation} {word_num} సార్లు కనిపించాలి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში სიტყვა \"{word}\" უნდა გამოჩნდეს {natural_relation} {word_num}-ჯერ."
        elif self.language == 'ky':
            return f"Жообуңузда \"{word}\" деген сөз {natural_relation} {word_num} жолу пайда болушу керек."
        elif self.language == 'pt':
            return f"Na resposta, a palavra ou frase \"{word}\" deve aparecer {natural_relation} {word_num} vezes."
        elif self.language == 'hi':
            return f"आपके उत्तर में, शब्द \"{word}\" {natural_relation} {word_num} बार आना चाहिए।"

    def check_following(self, response):
        # Languages that use the Latin alphabet and require consideration of plural forms
        if self.language in ['en', 'fr', 'it', 'sv', 'ro', 'tr', 'pt']:
            plural_forms = [
                self.word + 's',
                self.word + 'es' if self.word.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')) else None,
                self.word[:-1] + 'ies' if self.word.endswith('y') else None,
                self.word[:-1] + 'i' if self.word.endswith('o') else None,
                self.word[:-1] + 'e' if self.word.endswith('a') else None,
                self.word[:-1] + 'i' if self.word.endswith('e') else None,
                self.word[:-2] + 'chi' if self.word.endswith('co') else None,
                self.word[:-2] + 'ghi' if self.word.endswith('go') else None
            ]
            plural_forms = [f for f in plural_forms if f]
            pattern = r'\b(' + '|'.join([re.escape(self.word)] + [re.escape(p) for p in plural_forms]) + r')\b'

        # Languages that use simple repetitive forms
        elif self.language in ['ms', 'tgl', 'id', 'qu', 'zu', 'mg']:
            word_forms = [
                re.escape(self.word),
                re.escape(self.word) + '-' + re.escape(self.word),
                r'mga\s+' + re.escape(self.word) if self.language == 'tgl' else None,
                r'para\s+' + re.escape(self.word) if self.language == 'id' else None,
                r'para-para\s+' + re.escape(self.word) if self.language == 'id' else None
            ]
            word_forms = [f for f in word_forms if f]
            pattern = r'\b(' + '|'.join(word_forms) + r')\b'

        # Languages that use suffix changes
        elif self.language in ['bn', 'hi']:
            word_forms = [
                re.escape(self.word),
                re.escape(self.word) + r'गुलि|গুলি',
                re.escape(self.word) + r'गुलो|গুলো',
                re.escape(self.word) + r'रा|রা',
                re.escape(self.word) + r'ेरा|েরা',
                re.escape(self.word) + r'दের|দের'
            ]
            pattern = r'\b(' + '|'.join(word_forms) + r')\b'

        # Other languages use simple matching.
        else:  # zh, jp, ko, ta, te, ka, hy, ky
            pattern = re.escape(self.word)

        count = len(re.findall(pattern, response, flags=re.IGNORECASE))

        def calculate_score(diff):
            return max(0, 1 - 0.1 * (diff ** 2))

        if self.relation == "exactly":
            if count == self.word_num:
                return 1.0
            return calculate_score(abs(count - self.word_num))
        elif self.relation == "at_least":
            if count >= self.word_num:
                return 1.0
            return calculate_score(self.word_num - count)
        elif self.relation == "at_most":
            if count <= self.word_num:
                return 1.0
            return calculate_score(count - self.word_num)

        return 0.0


class KeywordsTogether(Instruction):
    def build_description(self, relation, word_num, word1, word2):
        self.word_num = word_num
        self.word1 = word1
        self.word2 = word2
        self.relation = relation

        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回复中，单词\"{word1}\"和单词\"{word2}\"应同时出现且不少于{word_num}次，且单词\"{word1}\"出现的次数要大于单词\"{word2}\"出现的次数。"
        elif self.language == 'en':
            return f"Your response must contain both \"{word1}\" and \"{word2}\" a minimum of {word_num} times each, with the frequency of \"{word1}\" exceeding that of \"{word2}\"."
        elif self.language == 'ja':
            return f"回答の中で、言葉\"{word1}\"と言葉\"{word2}\"は同時に{word_num}回以上出現する必要があり、かつ言葉\"{word1}\"の出現回数は言葉\"{word2}\"の出現回数より多くなければなりません。"
        elif self.language == 'fr':
            return f"Votre réponse doit contenir à la fois \"{word1}\" et \"{word2}\" au minimum {word_num} fois chacun, avec une fréquence de \"{word1}\" dépassant celle de \"{word2}\"."
        elif self.language == 'ms':
            return f"Dalam jawapan anda, perkataan atau frasa \"{word1}\" dan \"{word2}\" mesti muncul sekurang-kurangnya {word_num} kali setiap, dengan frekuensi \"{word1}\" melebihi \"{word2}\"。"
        elif self.language == 'tgl':
            return f"Sa iyong sagot, ang salitang \"{word1}\" at ang salitang \"{word2}\" ay dapat parehong lumabas ng hindi bababa sa {word_num} beses, at ang bilang ng paglabas ng salitang \"{word1}\" ay dapat mas mataas kaysa sa bilang ng paglitaw ng salitang \"{word2}\"."
        elif self.language == 'it':
            return f"La tua risposta deve contenere sia \"{word1}\" che \"{word2}\" un minimo di {word_num} volte ciascuna, con la frequenza di \"{word1}\" che supera quella di \"{word2}\"."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া, \"{word1}\" শব্দটি এবং \"{word2}\" শব্দটি একসাথে উপস্থিত হওয়া উচিত এবং {word_num} বারের কম নয়, এবং \"{word1}\" শব্দটি অবশ্যই এর চেয়ে বেশি বার প্রদর্শিত হবে শব্দটি \"{word2}\" এর উপস্থিতির সংখ্যা।"
        elif self.language == 'id':
            return f"Tanggapan Anda harus mengandung kedua kata \"{word1}\" dan \"{word2}\", masing-masing kata minimal {word_num} kali, dengan frekuensi \"{word1}\" melebihi \"{word2}\"."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, \"{word1}\" nisqa simi wan \"{word2}\" nisqa simi {word_num} kuti minchhayninwan rikurinan, \"{word1}\" nisqa simi aswan achka kutita rikurinan \"{word2}\" nisqa simiman."
        elif self.language == 'zu':
            return f"Empendulweni yakho, amagama \"{word1}\" no-\"{word2}\" kufanele avele okungenani {word_num} ngamunye, lapho \"{word1}\" kufanele livele kaningana kuno-\"{word2}\"."
        elif self.language == 'mg':
            return f"Amin'ny valinteninao, ny teny \"{word1}\" sy \"{word2}\" dia tokony hiseho farafahakeliny {word_num} isaky ny iray, ary ny teny \"{word1}\" tokony hihoatra ny \"{word2}\"."
        elif self.language == 'sv':
            return f"I ditt svar måste både \"{word1}\" och \"{word2}\" förekomma minst {word_num} gånger var, där frekvensen av \"{word1}\" överstiger den av \"{word2}\"."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să conțină atât \"{word1}\" cât și \"{word2}\" minimum de {word_num} ori fiecare, cu frecvența lui \"{word1}\" depășind-o pe cea a lui \"{word2}\"."
        elif self.language == 'tr':
            return f"Yanıtınızda, \"{word1}\" ve \"{word2}\" kelimelerinin her biri en az {word_num} kez geçmeli ve \"{word1}\" kelimesi \"{word2}\" kelimesinden daha sık kullanılmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில், \"{word1}\" மற்றும் \"{word2}\" ஆகிய இரண்டும் குறைந்தது {word_num} முறை தோன்ற வேண்டும், மேலும் \"{word1}\" என்பது \"{word2}\" ஐ விட அதிகமாக தோன்ற வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում \"{word1}\"-ը և \"{word2}\"-ը պետք է հայտնվեն նվազագույնը {word_num} անգամ, ընդ որում \"{word1}\"-ի հաճախականությունը պետք է գերազանցի \"{word2}\"-ի հաճախականությունը։"
        elif self.language == 'ko':
            return f"답변에서 \"{word1}\"와 \"{word2}\" 단어가 각각 최소 {word_num}번 이상 나타나야 하며, \"{word1}\"의 출현 빈도가 \"{word2}\"보다 더 많아야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో \"{word1}\" మరియు \"{word2}\" రెండూ కనీసం {word_num} సార్లు కనిపించాలి, అయితే \"{word1}\" యొక్క పునరావృతం \"{word2}\" కంటే ఎక్కువగా ఉండాలి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში \"{word1}\" და \"{word2}\" უნდა გამოჩნდეს მინიმუმ {word_num}-ჯერ თითოეული, სადაც \"{word1}\"-ის სიხშირე აღემატება \"{word2}\"-ის სიხშირეს."
        elif self.language == 'ky':
            return f"Жообуңузда \"{word1}\" жана \"{word2}\" сөздөрү ар бири кеминде {word_num} жолу пайда болушу керек, мында \"{word1}\" сөзү \"{word2}\" сөзүнөн көбүрөөк жолу кездешиши керек."
        elif self.language == 'pt':
            return f"Sua resposta deve conter tanto \"{word1}\" quanto \"{word2}\" no mínimo {word_num} vezes cada, com a frequência de \"{word1}\" excedendo a de \"{word2}\"."
        elif self.language == 'hi':
            return f"आपके उत्तर में, \"{word1}\" और \"{word2}\" दोनों शब्द कम से कम {word_num} बार आने चाहिए, जहां \"{word1}\" की आवृत्ति \"{word2}\" से अधिक होनी चाहिए।"

    def get_word_patterns(self, word):
        """Generate matching patterns for words in different languages."""
        # Languages that use the Latin alphabet and require consideration of plural forms
        if self.language in ['en', 'fr', 'sv', 'ro', 'tr', 'pt']:
            plural_forms = [
                word + 's',
                word + 'es' if word.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')) else None,
                word[:-1] + 'ies' if word.endswith('y') else None
            ]
            patterns = [word] + [p for p in plural_forms if p]
            return '(' + '|'.join(map(re.escape, patterns)) + ')'

        # Special handling for Italian
        elif self.language == 'it':
            plural_forms = [
                word,
                word[:-1] + 'i' if word.endswith('o') else None,
                word[:-1] + 'e' if word.endswith('a') else None,
                word[:-1] + 'i' if word.endswith('e') else None,
                word[:-2] + 'chi' if word.endswith('co') else None,
                word[:-2] + 'ghi' if word.endswith('go') else None
            ]
            patterns = [p for p in plural_forms if p]
            return '(' + '|'.join(map(re.escape, patterns)) + ')'

        # Languages that use suffix changes
        elif self.language in ['bn', 'hi']:
            suffix_forms = [
                word,
                word + r'গুলি|गुलि',
                word + r'গুলো|गुलो',
                word + r'রা|रा',
                word + r'েরা|ेरा',
                word + r'দের|दের'
            ]
            return '(' + '|'.join(map(re.escape, suffix_forms)) + ')'

        # Languages that use simple repetitive forms
        elif self.language in ['ms', 'tgl', 'id', 'qu', 'zu', 'mg']:
            forms = [
                re.escape(word),
                re.escape(word) + '-' + re.escape(word)
            ]
            if self.language == 'tgl':
                forms.append(r'mga\s+' + re.escape(word))
            elif self.language == 'id':
                forms.extend([
                    r'para\s+' + re.escape(word),
                    r'para-para\s+' + re.escape(word)
                ])
            return '(' + '|'.join(forms) + ')'

        # Other languages use simple matching.
        else:  # zh, jp, ko, ta, te, ka, hy, ky
            return re.escape(word)

    # cThe `check_following` method remains unchanged as its logic is universal.
    def check_following(self, response):
        pattern1 = self.get_word_patterns(self.word1)
        pattern2 = self.get_word_patterns(self.word2)

        together_pattern = f'{pattern1}.*?{pattern2}|{pattern2}.*?{pattern1}'
        together_count = len(re.findall(together_pattern, response, flags=re.IGNORECASE))

        count1 = len(re.findall(pattern1, response, flags=re.IGNORECASE))
        count2 = len(re.findall(pattern2, response, flags=re.IGNORECASE))

        score = 0.0

        if together_count > 0:
            score += 0.3

        if count1 >= self.word_num:
            score += 0.15

        if count2 >= self.word_num:
            score += 0.15

        if count1 >= self.word_num and count2 >= self.word_num:
            if count1 > count2:
                score += 0.4

        return score

class BannedKeywords(Instruction):
    def build_description(self, forbidden_words):
        self.forbidden_words = forbidden_words
        if self.language == 'zh':
            return f"不要在你的回复中包含 {', '.join(forbidden_words)} 等关键词。"
        elif self.language == 'en':
            return f"Your response must NOT contain: {', '.join(forbidden_words)}."
        elif self.language == 'ja':
            return f"回答の中に {', '.join(forbidden_words)} などのキーワードを含めないでください。"
        elif self.language == 'fr':
            return f"Votre réponse ne doit pas contenir : {', '.join(forbidden_words)}."
        elif self.language == 'ms':
            return f"Jawapan anda tidak boleh mengandungi: {', '.join(forbidden_words)}."
        elif self.language == 'tgl':
            return f"HUWAG isama ang mga keyword na {', '.join(forbidden_words)} sa iyong sagot."
        elif self.language == 'it':
            return f"La tua risposta NON deve contenere: {', '.join(forbidden_words)}."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া অবশ্যই থাকবে না: {', '.join(forbidden_words)}।"
        elif self.language == 'id':
            return f"Tanggapan Anda TIDAK BOLEH mengandung {', '.join(forbidden_words)}"
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi kay simikuna ama kachunchu: {', '.join(forbidden_words)}."
        elif self.language == 'zu':
            return f"Impendulo yakho AKUFANELE iqukathe: {', '.join(forbidden_words)}."
        elif self.language == 'mg':
            return f"Tsy tokony ahitana: {', '.join(forbidden_words)} ny valinteninao."
        elif self.language == 'sv':
            return f"Ditt svar får INTE innehålla: {', '.join(forbidden_words)}."
        elif self.language == 'ro':
            return f"Răspunsul tău NU trebuie să conțină: {', '.join(forbidden_words)}."
        elif self.language == 'tr':
            return f"Yanıtınız şunları İÇERMEMELİDİR: {', '.join(forbidden_words)}."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் பின்வரும் சொற்கள் இருக்கக்கூடாது: {', '.join(forbidden_words)}."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը ՉՊԵՏք է պարունակի: {', '.join(forbidden_words)}."
        elif self.language == 'ko':
            return f"답변에 다음 단어를 포함하지 마십시오: {', '.join(forbidden_words)}."
        elif self.language == 'te':
            return f"మీ సమాధానంలో ఈ పదాలు ఉండకూడదు: {', '.join(forbidden_words)}."
        elif self.language == 'ka':
            return f"თქვენი პასუხი არ უნდა შეიცავდეს: {', '.join(forbidden_words)}."
        elif self.language == 'ky':
            return f"Сиздин жообуңузда төмөнкү сөздөр болбошу керек: {', '.join(forbidden_words)}."
        elif self.language == 'pt':
            return f"Sua resposta NÃO deve conter: {', '.join(forbidden_words)}."
        elif self.language == 'hi':
            return f"आपके उत्तर में ये शब्द नहीं होने चाहिए: {', '.join(forbidden_words)}।"

    def get_word_patterns(self, word, language):
        """Generate word matching patterns based on different languages"""
        # Languages that use the Latin alphabet and need to consider plural forms
        if language in ['en', 'fr', 'sv', 'ro', 'tr', 'pt']:
            plural_forms = [
                word + 's',
                word + 'es' if word.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')) else None,
                word[:-1] + 'ies' if word.endswith('y') else None
            ]
            return [word] + [p for p in plural_forms if p]

        # Special handling of Italian
        elif language == 'it':
            plural_forms = [
                word,
                word[:-1] + 'i' if word.endswith('o') else None,
                word[:-1] + 'e' if word.endswith('a') else None,
                word[:-1] + 'i' if word.endswith('e') else None,
                word[:-2] + 'chi' if word.endswith('co') else None,
                word[:-2] + 'ghi' if word.endswith('go') else None
            ]
            return [p for p in plural_forms if p]

        # Languages that use suffix changes
        elif language in ['bn', 'hi']:
            suffix_forms = [
                word,
                word + ('গুলি' if language == 'bn' else 'गुलि'),
                word + ('গুলো' if language == 'bn' else 'गुलो'),
                word + ('রা' if language == 'bn' else 'रा'),
                word + ('েরা' if language == 'bn' else 'ेरा'),
                word + ('দের' if language == 'bn' else 'दের')
            ]
            return suffix_forms

        # Languages that use simple repetitive forms
        elif language in ['ms', 'tgl', 'id', 'qu', 'zu', 'mg']:
            forms = [
                word,
                word + '-' + word
            ]
            if language == 'tgl':
                forms.append('mga ' + word)
            elif language == 'id':
                forms.extend(['para-' + word, 'para ' + word])
            return forms

        # Other languages use simple matching.
        else:  # zh, jp, ko, ta, te, ka, hy, ky
            return [word]

    def check_following(self, response):
        forbidden_count = 0

        # Indo-European languages that use the Latin alphabet
        if self.language in ['en', 'fr', 'it', 'sv', 'ro', 'tr', 'pt']:
            for word in self.forbidden_words:
                word_forms = self.get_word_patterns(word, self.language)
                patterns = [r'\b' + re.escape(form) + r'\b' for form in word_forms]
                if any(re.search(pattern, response, flags=re.IGNORECASE) for pattern in patterns):
                    forbidden_count += 1

        # Languages that use suffix changes
        elif self.language in ['bn', 'hi']:
            for word in self.forbidden_words:
                word_forms = self.get_word_patterns(word, self.language)
                patterns = [re.escape(form) for form in word_forms]
                if any(re.search(pattern, response) for pattern in patterns):
                    forbidden_count += 1

        # Languages that use simple repetitive forms
        elif self.language in ['ms', 'tgl', 'id', 'qu', 'zu', 'mg']:
            for word in self.forbidden_words:
                word_forms = self.get_word_patterns(word, self.language)
                patterns = [r'\b' + re.escape(form) + r'\b' for form in word_forms]
                if any(re.search(pattern, response, flags=re.IGNORECASE) for pattern in patterns):
                    forbidden_count += 1

        # Other languages use simple matching.
        else:  # zh, jp, ko, ta, te, ka, hy, ky
            for word in self.forbidden_words:
                if re.search(r'\b' + re.escape(word) + r'\b', response, flags=re.IGNORECASE):
                    forbidden_count += 1

        # Calculate the score based on the number of forbidden words that appear.
        if forbidden_count == 0:
            return 1.0
        elif forbidden_count == 1:
            return 0.7
        elif forbidden_count == 2:
            return 0.1
        else:
            return 0.0


class ParagraphEnd(Instruction):
    def build_description(self, n, word):
        self.n = n
        self.word = word
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中，必须至少分{n}段，且词语\"{word}\"必须出现在所有段落的最后一句。"
        elif self.language == 'en':
            return f"Your response must contain at least {n} paragraphs, and \"{word}\" must appear in the last sentence of each paragraph."
        elif self.language == 'ja':
            return f"回答は最低{n}段落で構成され、言葉\"{word}\"は各段落の最後の文に必ず出現しなければなりません。"
        elif self.language == 'fr':
            return f"Votre réponse doit contenir au moins {n} paragraphes, et \"{word}\" doit apparaître dans la dernière phrase de chaque paragraphe."
        elif self.language == 'ms':
            return f"Jawapan anda mesti mengandungi sekurang-kurangnya {n} perenggan, dan \"{word}\" mesti muncul dalam ayat terakhir setiap perenggan."
        elif self.language == 'tgl':
            return f"Ang iyong sagot ay dapat magalman ng hind bababa sa {n} talata, at ang salitang \"{word}\" ay dapat lumabas sa huling pangungusap ng bawat talata."
        elif self.language == 'it':
            return f"La tua risposta deve contenere almeno {n} paragrafi, e \"{word}\" deve apparire nell'ultima frase di ogni paragrafo."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়াতে কমপক্ষে {n}টি অনুচ্ছেদ থাকতে হবে এবং প্রতিটি অনুচ্ছেদের শেষ বাক্যে \"{word}\" অবশ্যই উপস্থিত হবে।"
        elif self.language == 'id':
            return f"Tanggapan Anda harus mengandung setidaknya {n} paragraf, dan kata \"{word}\" harus muncul di kalimat terakhir setiap paragraf."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi {n} rakirisqa kanan tiyan, chaypi \"{word}\" simi tukuy rakirisqap qhipa rimaynimpi rikurinan."
        elif self.language == 'zu':
            return f"Impendulo yakho kufanele ibe nezigaba okungenani ezingu-{n}, futhi igama elithi \"{word}\" kufanele livele emshweni wokugcina wesigaba ngasinye."
        elif self.language == 'mg':
            return f"Ny valinteninao dia tsy maintsy ahitana paragrafy {n} farafahakeliny, ary ny teny hoe \"{word}\" dia tsy maintsy hita ao amin'ny fehezan-teny farany amin'ny paragrafy tsirairay."
        elif self.language == 'sv':
            return f"Ditt svar måste innehålla minst {n} stycken, och \"{word}\" måste finnas i den sista meningen i varje stycke."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să conțină cel puțin {n} paragrafe, iar \"{word}\" trebuie să apară în ultima propoziție a fiecărui paragraf."
        elif self.language == 'tr':
            return f"Yanıtınız en az {n} paragraf içermeli ve \"{word}\" kelimesi her paragrafın son cümlesinde bulunmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் குறைந்தது {n} பத்திகள் இருக்க வேண்டும், மேலும் \"{word}\" ஒவ்வொரு பத்தியின் கடைசி வாக்கியத்திலும் தோன்ற வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը պետք է պարունակի առնվազն {n} պարբերություն, և \"{word}\"-ը պետք է հայտնվի յուրաքանչյուր պարբերության վերջին նախադասության մեջ։"
        elif self.language == 'ko':
            return f"답변은 최소 {n}개의 문단으로 구성되어야 하며, \"{word}\"가 각 문단의 마지막 문장에 반드시 나타나야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో కనీసం {n} పేరాలు ఉండాలి, మరియు \"{word}\" ప్రతి పేరా చివరి వాక్యంలో కనిపించాలి."
        elif self.language == 'ka':
            return f"თქვენი პასუხი უნდა შეიცავდეს მინიმუმ {n} აბზაცს და \"{word}\" უნდა გამოჩნდეს თითოეული აბზაცის ბოლო წინადადებაში."
        elif self.language == 'ky':
            return f"Сиздин жообуңузда кеминде {n} абзац болушу керек, жана \"{word}\" ар бир абзацтын акыркы сүйлөмүндө көрүнүшү керек."
        elif self.language == 'pt':
            return f"Sua resposta deve conter pelo menos {n} parágrafos, e \"{word}\" deve aparecer na última frase de cada parágrafo."
        elif self.language == 'hi':
            return f"आपके उत्तर में कम से कम {n} अनुच्छेद होने चाहिए, और \"{word}\" प्रत्येक अनुच्छेद के अंतिम वाक्य में आना चाहिए।"

    def is_reference_section(self, paragraph):
        """Check if the paragraph is the reference section."""
        ref_starts = {
            'en': ['references', 'bibliography', 'works cited', 'citations'],
            'it': ['riferimenti', 'bibliografia', 'citazioni'],
            'zh': ['参考文献', '引用文献'],
            'ja': ['参考文献', '引用文献'],
            'fr': ['références', 'bibliographie'],
            'id': ['referensi', 'daftar pustaka'],
            'ms': ['rujukan', 'bibliografi'],
            'tgl': ['mga sanggunian', 'bibliograpiya'],
            'bn': ['তথ্যসূত্র', 'গ্রন্থপঞ্জি'],
            'qu': ['qilqasqakuna', 'bibliografía'],
            'zu': ['imithombo', 'izincwadi ezisetshenzisiwe'],
            'mg': ['boky nampiasaina', 'bibliographie'],
            'sv': ['referenser', 'källförteckning', 'litteratur'],
            'ro': ['referințe', 'bibliografie'],
            'tr': ['kaynakça', 'kaynaklar'],
            'ta': ['மேற்கோள்கள்', 'நூல் பட்டியல்'],
            'hy': ['գրականություն', 'հղումներ'],
            'ko': ['참고문헌', '인용문헌'],
            'te': ['సూచనలు', 'గ్రంథసూచి'],
            'ka': ['ლიტერატურა', 'წყაროები'],
            'ky': ['адабияттар', 'булактар'],
            'pt': ['referências', 'bibliografia'],
            'hi': ['संदर्भ', 'ग्रंथ सूची']
        }

        paragraph_lower = paragraph.lower().strip()
        return any(paragraph_lower.startswith(ref)
                   for ref in ref_starts.get(self.language, ref_starts['en']))

    def get_word_patterns(self, word):
        """Generate word matching patterns based on language"""
        # Languages that use the Latin alphabet and need to consider plural forms
        if self.language in ['en', 'fr', 'sv', 'ro', 'tr', 'pt']:
            plural_forms = [
                word + 's',
                word + 'es' if word.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')) else None,
                word[:-1] + 'ies' if word.endswith('y') else None
            ]
            patterns = [word] + [p for p in plural_forms if p]
            return '(' + '|'.join(map(re.escape, patterns)) + ')'

        # Special handling of Italian
        elif self.language == 'it':
            plural_forms = [
                word,
                word[:-1] + 'i' if word.endswith('o') else None,
                word[:-1] + 'e' if word.endswith('a') else None,
                word[:-1] + 'i' if word.endswith('e') else None,
                word[:-2] + 'chi' if word.endswith('co') else None,
                word[:-2] + 'ghi' if word.endswith('go') else None
            ]
            patterns = [p for p in plural_forms if p]
            return '(' + '|'.join(map(re.escape, patterns)) + ')'

        # Languages that use suffix changes
        elif self.language in ['bn', 'hi']:
            suffix_forms = [
                word,
                word + ('গুলি' if self.language == 'bn' else 'गुलि'),
                word + ('গুলো' if self.language == 'bn' else 'गुलो'),
                word + ('রা' if self.language == 'bn' else 'रा'),
                word + ('েরা' if self.language == 'bn' else 'ेरा'),
                word + ('দের' if self.language == 'bn' else 'दের')
            ]
            return '(' + '|'.join(map(re.escape, suffix_forms)) + ')'

        # Other languages use simple matching.
        else:
            return re.escape(word)

    def check_following(self, response):
        paragraphs = [para for para in response.strip().split('\n') if para.strip()]

        if len(paragraphs) < self.n:
            return 0.0

        # Define sentence termination symbols in different languages
        sentence_end_patterns = {
            'zh': r'[。！？]',
            'ja': r'[。！？]',
            'bn': r'[।!?]',
            'ta': r'[.|。|।|!|?|？|முற்று|.]',  # Tamil
            'te': r'[.|。|।|!|?|？|.]',  # Telugu
            'ka': r'[.|!|?|։|。|।]',  # Georgian
            'hy': r'[:|։|.|!|?|՝|।]',  # Armenian
            'ko': r'[다|까|요|.|!|?|。]',  # Korean
            'ky': r'[.|!|?|។|။|。|।]',  # Kyrgyz
            'hi': r'[.|।|?|!]'  # Hindi
        }

        # Get the sentence termination symbol pattern of the current language; if there is no specific pattern, use the default one.
        sentence_end_regex = sentence_end_patterns.get(self.language, r'[.!?]')

        incorrect_count = 0
        valid_paragraph_count = 0

        for paragraph in paragraphs[-self.n:]:
            if self.is_reference_section(paragraph):
                continue

            valid_paragraph_count += 1
            sentences = re.split(sentence_end_regex, paragraph.strip())
            sentences = [s for s in sentences if s.strip()]

            if not sentences:
                incorrect_count += 1
                continue

            last_sentence = sentences[-1].strip()

            pattern = self.get_word_patterns(self.word)
            if not re.search(r'\b' + pattern + r'\b', last_sentence, flags=re.IGNORECASE):
                incorrect_count += 1

        if valid_paragraph_count < self.n:
            return 0.0

        return max(0, 1 - 0.2 * (incorrect_count ** 2))

class FirstWord(Instruction):
    def build_description(self, word):
        self.word = word.lower()  # Convert the target word to lowercase.
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复的第一个词语必须是\"{word}\"。"
        elif self.language == 'en':
            return f"The first word of your response must be \"{word}\"."
        elif self.language == 'ja':
            return f"回答の最初の言葉は「{word}」でなければなりません。"
        elif self.language == 'fr':
            return f"Le premier mot de votre réponse doit être \"{word}\"."
        elif self.language == 'ms':
            return f"Perkataan pertama jawapan anda mesti \"{word}\"."
        elif self.language == 'tgl':
            return f"Ang unang salita ng iyong sagot ay dapat \"{word}\"."
        elif self.language == 'it':
            return f"La prima parola della tua risposta deve essere \"{word}\"."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া প্রথম শব্দ \"{word}\" হতে হবে।"
        elif self.language == 'id':
            return f"Kata pertama dalam tanggapan Anda haruslah \"{word}\"."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykip ñawpaq simin \"{word}\" kanan."
        elif self.language == 'zu':
            return f"Igama lokuqala empendulweni yakho kufanele libe \"{word}\"."
        elif self.language == 'mg':
            return f"Ny teny voalohany amin'ny valinteninao dia tsy maintsy \"{word}\"."
        elif self.language == 'sv':
            return f"Det första ordet i ditt svar måste vara \"{word}\"."
        elif self.language == 'ro':
            return f"Primul cuvânt al răspunsului tău trebuie să fie \"{word}\"."
        elif self.language == 'tr':
            return f"Yanıtınızın ilk kelimesi \"{word}\" olmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலின் முதல் வார்த்தை \"{word}\" ஆக இருக்க வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանի առաջին բառը պետք է լինի \"{word}\"։"
        elif self.language == 'ko':
            return f"답변의 첫 번째 단어는 \"{word}\"이어야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో మొదటి పదం \"{word}\" అయి ఉండాలి."
        elif self.language == 'ka':
            return f"თქვენი პასუხის პირველი სიტყვა უნდა იყოს \"{word}\"."
        elif self.language == 'ky':
            return f"Жообуңуздун биринчи сөзү \"{word}\" болушу керек."
        elif self.language == 'pt':
            return f"A primeira palavra da sua resposta deve ser \"{word}\"."
        elif self.language == 'hi':
            return f"आपके उत्तर का पहला शब्द \"{word}\" होना चाहिए।"

    def check_following(self, response):
        # Remove all symbols and spaces to get the cleaned text.
        def remove_special_chars(text):
            return re.sub(r'[^\w\s]', '', text).strip()  # Keep letters, numbers, and spaces, and remove other symbols.

        # Paragraphs (using \n or \n\n as paragraph separators)
        sections = re.split(r'\n\n|\n', response.strip())
        first_section = sections[0] if sections else ''
        second_section = sections[1] if len(sections) > 1 else ''

        # Clean up the content of the first and second paragraphs.
        cleaned_first_section = remove_special_chars(first_section).lower()  # Convert to lowercase
        cleaned_second_section = remove_special_chars(second_section).lower()  # Convert to lowercase

        # Get the first valid word
        def check_first_word(text):
            words = text.split()
            return words[0] if words else ''  # Return the first word; if it is empty, return an empty string.

        # Check the first words of the first and second paragraphs.
        first_word_in_first_section = check_first_word(cleaned_first_section)
        first_word_in_second_section = check_first_word(cleaned_second_section)

        # Translate the following text into English.
        # If the first paragraph contains `#`, check both the first and second paragraphs. Return 1 point as long as one of them is correct.
        if '#' in first_section:
            return 1.0 if (first_word_in_first_section == self.word or
                           first_word_in_second_section == self.word) else 0.0
        else:
            # Otherwise, only check the first paragraph.
            return 1.0 if first_word_in_first_section == self.word else 0.0


class MaxWords(Instruction):
    def build_description(self, max_words):
        self.max_words = max_words
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复不能超过{max_words}个字。"
        elif self.language == 'en':
            return f"Your response word count must not exceed {max_words}."
        elif self.language == 'ja':
            return f"回答は{max_words}文字を超えてはいけません。"
        elif self.language == 'fr':
            return f"Le nombre de mots de votre réponse ne doit pas dépasser {max_words}."
        elif self.language == 'ms':
            return f"Jumlah perkataan dalam jawapan anda tidak boleh melebihi {max_words}."
        elif self.language == 'tgl':
            return f"Ang iyong sagot ay hindi dapat lumagpas sa {max_words} na salita."
        elif self.language == 'it':
            return f"Il conteggio delle parole della tua risposta non deve superare {max_words}."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া শব্দ সংখ্যা {max_words} অতিক্রম করা উচিত নয়।"
        elif self.language == 'id':
            return f"Jumlah kata dalam tanggapan Anda tidak boleh melebihi {max_words} kata."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi simikunaqa ama {max_words} simita yallinmanchu."
        elif self.language == 'zu':
            return f"Amagama empendulo yakho akufanele adlule ku-{max_words}."
        elif self.language == 'mg':
            return f"Ny isan'ny teny amin'ny valinteninao dia tsy tokony hihoatra ny {max_words}."
        elif self.language == 'sv':
            return f"Antalet ord i ditt svar får inte överstiga {max_words}."
        elif self.language == 'ro':
            return f"Numărul de cuvinte din răspunsul tău nu trebuie să depășească {max_words}."
        elif self.language == 'tr':
            return f"Yanıtınızdaki kelime sayısı {max_words}'i geçmemelidir."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் சொற்களின் எண்ணிக்கை {max_words} ஐ மீறக்கூடாது."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում բառերի քանակը չպետք է գերազանցի {max_words}-ը։"
        elif self.language == 'ko':
            return f"답변의 글자 수가 {max_words}자를 초과하지 않아야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో పదాల సంఖ్య {max_words} మించకూడదు."
        elif self.language == 'ka':
            return f"თქვენს პასუხში სიტყვების რაოდენობა არ უნდა აღემატებოდეს {max_words}-ს."
        elif self.language == 'ky':
            return f"Жообуңуздагы сөздөрдүн саны {max_words} ашпашы керек."
        elif self.language == 'pt':
            return f"A contagem de palavras da sua resposta não deve exceder {max_words}."
        elif self.language == 'hi':
            return f"आपके उत्तर में शब्दों की संख्या {max_words} से अधिक नहीं होनी चाहिए।"

    def check_following(self, response):
        # Divide languages into three groups for processing.
        # Group 1: Languages that use spaces to separate words
        if self.language in ['en', 'fr', 'ms', 'tgl', 'it', 'bn', 'id', 'qu', 'zu', 'mg', 'sv', 'ro', 'tr', 'hy', 'ka', 'ky', 'pt']:
            words = response.split()
        # Group 2: Languages that use character counting (East Asian language group)
        elif self.language in ['zh', 'ja', 'ko']:
            if self.language == 'zh': 
                words = list(re.findall(r'[\u4e00-\u9fff]', response))
            elif self.language == 'ja':  
                words = list(re.findall(r'[ぁ-んァ-ン一-龥]', response))
            else:  #
                words = list(re.findall(r'[가-힣]', response))
        # Group 3: Languages that use unique character systems
        elif self.language in ['ta', 'te', 'hi']:  # Tamil, Telugu, Hindi
            # These languages use specific Unicode ranges.
            if self.language == 'ta':  # Tamil
                words = list(re.findall(r'[\u0B80-\u0BFF]+', response))
            elif self.language == 'te':  # Telugu
                words = list(re.findall(r'[\u0C00-\u0C7F]+', response))
            else:  # Hindi
                words = list(re.findall(r'[\u0900-\u097F]+', response))

        word_count = len(words)

        # If the word count does not exceed the limit, directly return 1 point.
        if word_count <= self.max_words:
            return 1.0

        # Calculate the deviation ratio
        deviation_ratio = abs(word_count - self.max_words) / self.max_words

        # Calculate the score using the formula.
        score = max(0, 1 - 20 * (deviation_ratio ** 2))

        return score


class RangeWords(Instruction):
    def build_description(self, min_words, max_words):
        self.min_words = min_words
        self.max_words = max_words
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复的字数应该在{min_words}到{max_words}之间。"
        elif self.language == 'en':
            return f"Your response word count must be between {min_words} and {max_words}."
        elif self.language == 'ja':
            return f"回答の文字数は{min_words}字から{max_words}字の間でなければなりません。"
        elif self.language == 'fr':
            return f"Le nombre de mots de votre réponse doit être compris entre {min_words} et {max_words}."
        elif self.language == 'ms':
            return f"Jumlah perkataan jawapan anda mesti berada antara {min_words} dan {max_words}."
        elif self.language == 'tgl':
            return f"Ang bilang ng mga salita sa iyong sagot ay dapat nasa pagitan ng {min_words} hanggang {max_words}."
        elif self.language == 'it':
            return f"Il conteggio delle parole della tua risposta deve essere tra {min_words} e {max_words}."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া শব্দ সংখ্যা অবশ্যই {min_words} এবং {max_words} এর মধ্যে হতে হবে।"
        elif self.language == 'id':
            return f"Jumlah kata dalam tanggapan Anda harus antara {min_words} dan {max_words} kata."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi simikunaqa {min_words}manta {max_words}kama kanan."
        elif self.language == 'zu':
            return f"Amagama empendulo yakho kufanele abe phakathi kuka-{min_words} no-{max_words}."
        elif self.language == 'mg':
            return f"Ny isan'ny teny amin'ny valinteninao dia tokony ho eo anelanelan'ny {min_words} sy {max_words}."
        elif self.language == 'sv':
            return f"Antalet ord i ditt svar måste vara mellan {min_words} och {max_words}."
        elif self.language == 'ro':
            return f"Numărul de cuvinte din răspunsul tău trebuie să fie între {min_words} și {max_words}."
        elif self.language == 'tr':
            return f"Yanıtınızdaki kelime sayısı {min_words} ile {max_words} arasında olmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் சொற்களின் எண்ணிக்கை {min_words} முதல் {max_words} வரை இருக்க வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում բառերի քանակը պետք է լինի {min_words}-ից {max_words}-ի միջև։"
        elif self.language == 'ko':
            return f"답변의 글자 수는 {min_words}자에서 {max_words}자 사이여야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో పదాల సంఖ్య {min_words} నుండి {max_words} మధ్య ఉండాలి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში სიტყვების რაოდენობა უნდა იყოს {min_words}-დან {max_words}-მდე."
        elif self.language == 'ky':
            return f"Жообуңуздагы сөздөрдүн саны {min_words} менен {max_words} арасында болушу керек."
        elif self.language == 'pt':
            return f"A contagem de palavras da sua resposta deve estar entre {min_words} e {max_words}."
        elif self.language == 'hi':
            return f"आपके उत्तर में शब्दों की संख्या {min_words} से {max_words} के बीच होनी चाहिए।"

    def check_following(self, response):
        # Divide languages into three groups for processing.
        # Group 1: Languages that use spaces to separate words
        if self.language in ['en', 'fr', 'ms', 'tgl', 'it', 'bn', 'id', 'qu', 'zu', 'mg', 'sv', 'ro', 'tr', 'hy', 'ka', 'ky', 'pt']:
            words = response.split()
        # Group 2: Languages that use character counting (East Asian language group)
        elif self.language in ['zh', 'ja', 'ko']:
            if self.language == 'zh': 
                words = re.findall(r'[\u4e00-\u9fff]', response)
            elif self.language == 'ja': 
                words = re.findall(r'[ぁ-んァ-ン一-龥]', response)
            else:  
                words = re.findall(r'[가-힣]', response)
        # Group 3: Languages that use unique character systems
        elif self.language in ['ta', 'te', 'hi']:  # Tamil, Telugu, Hindi
            if self.language == 'ta':  # Tamil
                words = list(re.findall(r'[\u0B80-\u0BFF]+', response))
            elif self.language == 'te':  # Telugu
                words = list(re.findall(r'[\u0C00-\u0C7F]+', response))
            else:  # Hindi
                words = list(re.findall(r'[\u0900-\u097F]+', response))

        word_count = len(words)

        # If it is within the range, return the full score.
        if self.min_words <= word_count <= self.max_words:
            return 1.0

        # Calculate the distance to the nearest boundary.
        if word_count < self.min_words:
            target = self.min_words
            request = self.min_words  # Use the minimum value as the benchmark.
        else:  # word_count > self.max_words
            target = self.max_words
            request = self.max_words  # Use the maximum value as the benchmark.

        # Calculate the deviation ratio
        deviation_ratio = abs(word_count - target) / request

        # Calculate the score using the formula
        score = max(0, 1 - 20 * (deviation_ratio ** 2))

        return score



class AdditionAtEnd(Instruction):
    def build_description(self, addition):
        self.addition = addition
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回复的结尾显式地添加以\"{self.addition}\"开头的附言。"
        elif self.language == 'en':
            return f'Explicitly add a postscript beginning with \"{self.addition}\" at the end of your response.'
        elif self.language == 'ja':
            return f'回答の最後に、「{self.addition}」で始まる追伸を明示的に追加してください。'
        elif self.language == 'fr':
            return f'Ajoutez explicitement un post-scriptum commençant par \"{self.addition}\" à la fin de votre réponse.'
        elif self.language == 'ms':
            return f'Secara jelas tambahkan pos skrip yang bermula dengan \"{self.addition}\" pada akhir jawapan anda.'
        elif self.language == 'tgl':
            return f'Sa dulo ng iyong sagot, tahasang magdagdag ng postscript na nagsisimula sa \"{self.addition}\".'
        elif self.language == 'it':
            return f'Aggiungi esplicitamente una postfazione che inizi con \"{self.addition}\" alla fine della tua risposta.'
        elif self.language == 'bn':
            return f'আপনার প্রতিক্রিয়ার শেষে \"{self.addition}\" দিয়ে শুরু হওয়া একটি পোস্টস্ক্রিপ্ট স্পষ্টভাবে যোগ করুন।'
        elif self.language == 'id':
            return f'Secara eksplisit tambahkan sebuah catatan tambahan yang dimulai dengan \"{self.addition}\" di akhir tanggapan Anda.'
        # New languages
        elif self.language == 'qu':
            return f'Kutichisqaykip tukukuyninpi \"{self.addition}\" nisqawan qallariq yapasqa qillqata churay.'
        elif self.language == 'zu':
            return f'Ngokucacile, faka umbhalo oqala ngo-\"{self.addition}\" ekugcineni kwempendulo yakho.'
        elif self.language == 'mg':
            return f'Asio fanamarihana manomboka amin\'ny \"{self.addition}\" amin\'ny faran\'ny valinteninao.'
        elif self.language == 'sv':
            return f'Lägg uttryckligen till ett postskriptum som börjar med \"{self.addition}\" i slutet av ditt svar.'
        elif self.language == 'ro':
            return f'Adaugă în mod explicit un post-scriptum care începe cu \"{self.addition}\" la sfârșitul răspunsului tău.'
        elif self.language == 'tr':
            return f'Yanıtınızın sonuna \"{self.addition}\" ile başlayan bir not ekleyin.'
        elif self.language == 'ta':
            return f'உங்கள் பதிலின் முடிவில் \"{self.addition}\" என்பதைக் கொண்டு தொடங்கும் குறிப்பை வெளிப்படையாகச் சேர்க்கவும்.'
        elif self.language == 'hy':
            return f'Ձեր պատասխանի վերջում հստակորեն ավելացրեք \"{self.addition}\"-ով սկսվող հետգրություն։'
        elif self.language == 'ko':
            return f'답변 끝에 \"{self.addition}\"(으)로 시작하는 추신을 명시적으로 추가하세요.'
        elif self.language == 'te':
            return f'మీ సమాధానం చివరిలో \"{self.addition}\"తో ప్రారంభమయ్యే పోస్ట్‌స్క్రిప్ట్‌ను స్పష్టంగా జోడించండి.'
        elif self.language == 'ka':
            return f'თქვენი პასუხის ბოლოს მკაფიოდ დაამატეთ პოსტსკრიპტუმი, რომელიც იწყება \"{self.addition}\"-ით.'
        elif self.language == 'ky':
            return f'Жообуңуздун аягына \"{self.addition}\" менен башталган кошумча жазууну ачык түрдө кошуңуз.'
        elif self.language == 'pt':
            return f'Adicione explicitamente um pós-escrito começando com \"{self.addition}\" no final da sua resposta.'
        elif self.language == 'hi':
            return f'अपने उत्तर के अंत में \"{self.addition}\" से शुरू होने वाला एक स्पष्ट पोस्टस्क्रिप्ट जोड़ें।'

    def check_following(self, response):
        # Remove leading and trailing whitespace characters.
        response = response.strip()
        score = 0.0

        # Check if the sentence appears in the text (0.5 points)
        basic_pattern = re.escape(self.addition)
        if re.search(basic_pattern, response, flags=re.IGNORECASE):
            score += 0.5

        # Set the pattern of sentence terminators according to the language.
        # Group 1: Languages that use East Asian punctuation marks
        if self.language in ['zh', 'ja', 'ko']:
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$', 
                r'[。！？]\s*' + re.escape(self.addition) + r'[^。！？]*$' 
            ]
        # Group 2: Languages that use special punctuation marks
        elif self.language in ['bn', 'hi']:  
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$', 
                r'[।॥]\s*' + re.escape(self.addition) + r'[^।॥]*$'  # 
            ]
        elif self.language == 'ta':  
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$',
                r'[.|。|।|!|?|？|முற்று]\s*' + re.escape(self.addition) + r'[^.|。|।|!|?|？|முற்று]*$'
            ]
        elif self.language == 'te':  
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$',
                r'[.|。|।|!|?|？]\s*' + re.escape(self.addition) + r'[^.|。|।|!|?|？]*$'
            ]
        elif self.language == 'hy': 
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$',
                r'[:|։|.|!|?|՝]\s*' + re.escape(self.addition) + r'[^:|։|.|!|?|՝]*$'
            ]
        elif self.language == 'ka':  
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$',
                r'[.|!|?|։]\s*' + re.escape(self.addition) + r'[^.|!|?|։]*$'
            ]
        # Group 3: Languages that use standard Latin punctuation
        else:  # en, fr, ms, tl, it, id, qu, zu, mg, sv, ro, tr, ky, pt
            patterns = [
                r'\s*' + re.escape(self.addition) + r'\s*$',  
                r'\.\s*' + re.escape(self.addition) + r'[^.]*$' 
            ]

        # Check if it is at the end
        if any(bool(re.search(pattern, response, flags=re.IGNORECASE))
               for pattern in patterns):
            score += 0.5

        return score


class TitleBrackets(Instruction):
    def build_description(self, max_length):
        self.max_length = max_length

        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中必须包含一个标题，用双尖括号或书名号包裹，且标题长度不超过{self.max_length}个字。"
        elif self.language == 'en':
            return f'Your response must include a title enclosed in double angle brackets or book title brackets, and the title should not exceed {self.max_length} words.'
        elif self.language == 'ja':
            return f"回答には二重山括弧（<< >>）または書名括弧（《 》）で囲まれたタイトルを含める必要があり、そのタイトルは{self.max_length}文字を超えてはいけません。"
        elif self.language == 'fr':
            return f'Votre réponse doit inclure un titre encadré de doubles chevrons ou de crochets de titre de livre, et le titre ne doit pas dépasser {self.max_length} mots.'
        elif self.language == 'ms':
            return f'Jawapan anda mesti mengandungi tajuk yang disenaraikan dalam tanda sudut ganda atau tanda buku, dan tajuk itu tidak boleh melebihi {self.max_length} perkataan.'
        elif self.language == 'tgl':
            return f'Ang iyong sagot ay dapat maglaman ng isang pamagat, na nakapaloob sa mga double angle bracket o mga panipi, at ang haba ng pamagat ay hindi dapat lumagpas sa {self.max_length} mga salita.'
        elif self.language == 'it':
            return f'La tua risposta deve includere un titolo racchiuso tra parentesi angolari o parentesi di titolo libro, e il titolo non deve superare {self.max_length} parole.'
        elif self.language == 'bn':
            return f'আপনার প্রতিক্রিয়া অবশ্যই ডবল অ্যাঙ্গেল ব্র্যাকেট বা বইয়ের শিরোনাম বন্ধনীতে একটি শিরোনাম অন্তর্ভুক্ত করতে হবে এবং শিরোনামটি {self.max_length} শব্দের বেশি হওয়া উচিত নয়৷'
        elif self.language == 'id':
            return f'Tanggapan Anda harus mencakup sebuah judul yang diletakkan di dalam tanda sudut ganda atau tanda kurung judul buku, dan judul tersebut tidak boleh melebihi {self.max_length} kata.'
        # New languages
        elif self.language == 'qu':
            return f'Kutichisqaykipi huk sutichata yapanaykin «» utaq librup sutinwan qillqana, manataq {self.max_length} simikunamanta aswan hatunchu kanan.'
        elif self.language == 'zu':
            return f'Impendulo yakho kufanele ibe nesihloko esifakwe phakathi kohlobo oluphindiwe lwezimpawu noma izimpawu zesihloko sencwadi, futhi isihloko akufanele seqe amagama angu-{self.max_length}.'
        elif self.language == 'mg':
            return f'Ny valinteninao dia tsy maintsy ahitana lohateny ao anatin\'ny mari-drobaka roa na mari-boky, ary ny lohateny dia tsy tokony hihoatra ny teny {self.max_length}.'
        elif self.language == 'sv':
            return f'Ditt svar måste innehålla en titel inom dubbla vinkelparenteser eller boktitelparenteser, och titeln får inte överstiga {self.max_length} ord.'
        elif self.language == 'ro':
            return f'Răspunsul tău trebuie să includă un titlu încadrat între paranteze unghiulare duble sau paranteze de titlu de carte, iar titlul nu trebuie să depășească {self.max_length} cuvinte.'
        elif self.language == 'tr':
            return f'Yanıtınız çift açılı parantez veya kitap başlığı parantezi içinde bir başlık içermeli ve başlık {self.max_length} kelimeyi geçmemelidir.'
        elif self.language == 'ta':
            return f'உங்கள் பதிலில் இரட்டை கோண அடைப்புக்குறி அல்லது புத்தக தலைப்பு அடைப்புக்குறிக்குள் ஒரு தலைப்பு இருக்க வேண்டும், மேலும் தலைப்பு {self.max_length} சொற்களை மீறக்கூடாது.'
        elif self.language == 'hy':
            return f'Ձեր պատասխանը պետք է ներառի վերնագիր՝ տեղադրված կրկնակի անկյունային փակագծերում կամ գրքի վերնագրի փակագծերում, և վերնագիրը չպետք է գերազանցի {self.max_length} բառը։'
        elif self.language == 'ko':
            return f'답변에는 이중 꺾쇠 괄호나 책 제목 괄호로 둘러싼 제목이 포함되어야 하며, 제목은 {self.max_length}자를 초과하지 않아야 합니다.'
        elif self.language == 'te':
            return f'మీ సమాధానంలో రెండు కోణపు బ్రాకెట్లు లేదా పుస్తక శీర్షిక బ్రాకెట్లలో ఒక శీర్షిక ఉండాలి, మరియు శీర్షిక {self.max_length} పదాలను మించకూడదు.'
        elif self.language == 'ka':
            return f'თქვენი პასუხი უნდა შეიცავდეს სათაურს ორმაგ კუთხოვან ფრჩხილებში ან წიგნის სათაურის ფრჩხილებში, და სათაური არ უნდა აღემატებოდეს {self.max_length} სიტყვას.'
        elif self.language == 'ky':
            return f'Жообуңузда кош бурчтуу кашаалар же китеп аталышынын кашаалары менен курчалган аталыш болушу керек, жана аталыш {self.max_length} сөздөн ашпашы керек.'
        elif self.language == 'pt':
            return f'Sua resposta deve incluir um título entre colchetes angulares duplos ou colchetes de título de livro, e o título não deve exceder {self.max_length} palavras.'
        elif self.language == 'hi':
            return f'आपके उत्तर में दोहरे कोणीय कोष्ठक या पुस्तक शीर्षक कोष्ठक में एक शीर्षक होना चाहिए, और शीर्षक {self.max_length} शब्दों से अधिक नहीं होना चाहिए।'

    def check_following(self, response):
        # A regular expression that matches titles, matching multiple types of title markers
        patterns = {
            'default': [
                r'(?:<<|《)(.+?)(?:>>|》)',  # Double angle brackets and book title marks
                r'"(.+?)"',  # double quotes
                r'"(.+?)"',  # British English quotation marks
                r'«(.+?)»',  # French quotation marks and Italian quotation marks
                r'„(.+?)"',  # German quotation marks
            ],
            'ko': [  # Korean special parentheses
                r'(?:<<|《)(.+?)(?:>>|》)',
                r'『(.+?)』',
                r'「(.+?)」',
            ],
            'ta': [  # Tamil special parentheses
                r'(?:<<|《)(.+?)(?:>>|》)',
                r'["\"](.+?)["\"]',
            ],
            'te': [  # Telugu special parentheses
                r'(?:<<|《)(.+?)(?:>>|》)',
                r'["\"](.+?)["\"]',
            ],
            'hy': [  # Armenian special parentheses
                r'(?:<<|《)(.+?)(?:>>|》)',
                r'«(.+?)»',
                r'„(.+?)"',
            ],
            'ka': [  # Georgian special parentheses
                r'(?:<<|《)(.+?)(?:>>|》)',
                r'„(.+?)"',
            ]
        }

        # Get the pattern set of the current language; if there is no specific pattern, use the default pattern.
        current_patterns = patterns.get(self.language, patterns['default'])

        
        for pattern in current_patterns:
            match = re.search(pattern, response)
            if match:
                title_text = match.group(1).strip()
                score = 0.1  

                # Calculate the length according to language groups.
                # Group 1: Languages that use character counting
                if self.language in ['zh', 'ja', 'ko']:
                    char_count = len(title_text)
                    if char_count <= self.max_length:
                        score += 0.9
                    else:
                        diff = (char_count - self.max_length) / self.max_length
                        length_score = max(0, 0.9 - 0.1 * (diff ** 2))
                        score += length_score

                # Group 2: Languages that use special character systems
                elif self.language in ['ta', 'te', 'hi']:
                    if self.language == 'ta':
                        char_count = len(re.findall(r'[\u0B80-\u0BFF]', title_text))
                    elif self.language == 'te':
                        char_count = len(re.findall(r'[\u0C00-\u0C7F]', title_text))
                    else:  # Hindi
                        char_count = len(re.findall(r'[\u0900-\u097F]', title_text))

                    if char_count <= self.max_length:
                        score += 0.9
                    else:
                        diff = (char_count - self.max_length) / self.max_length
                        length_score = max(0, 0.9 - 0.1 * (diff ** 2))
                        score += length_score

                # Group 3: Languages that use spaces to separate words
                else:
                    word_count = len(title_text.split())
                    if word_count <= self.max_length:
                        score += 0.9
                    else:
                        diff = (word_count - self.max_length) / self.max_length
                        length_score = max(0, 0.9 - 0.1 * (diff ** 2))
                        score += length_score

                return score

        return 0.0  # No title markers meeting the requirements were found.

class MarkdownHighlight(Instruction):
    def build_description(self, n):
        self.n = n
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回复中至少用Markdown高亮{n}个部分。使用双星号（**）来标记高亮文本。"
        elif self.language == 'en':
            return f"In your response, highlight at least {n} parts using Markdown, use double asterisks (**) to mark highlighted text."
        elif self.language == 'ja':
            return f"回答の中で、少なくとも{n}箇所をMarkdownで強調してください。強調したいテキストを二重アスタリスク（**）で囲んでください。"
        elif self.language == 'fr':
            return f"Dans votre réponse, mettez en surbrillance au moins {n} parties en utilisant Markdown, utilisez des doubles astérisques (**) pour marquer le texte surligné."
        elif self.language == 'ms':
            return f"Dalam jawapan anda, sorot sekurang-kurangnya {n} bahagian menggunakan Markdown, gunakan tanda bintang berganda (**) untuk menandai teks yang disorot."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, i-highlight ang hindi bababa sa {n} na bahagi gamit ang Markdown. Gumamit ng double asterisks (**) upang markahan ang naka-highlight na teksto."
        elif self.language == 'it':
            return f"Nella tua risposta, evidenzia almeno {n} parti utilizzando Markdown, usa i doppi asterischi (**) per segnare il testo evidenziato."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়াতে, মার্কডাউন ব্যবহার করে কমপক্ষে {n}টি অংশ হাইলাইট করুন, হাইলাইট করা পাঠ্যকে চিহ্নিত করতে ডবল তারকাচিহ্ন (**) ব্যবহার করুন।"
        elif self.language == 'id':
            return f"Dalam tanggapan Anda, sorot setidaknya {n}bagian menggunakan Markdown, dengan menggunakan tanda bintang ganda (**) untuk menandai teks yang disorot."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, {n} rakirisqakunata Markdownwan k'ancharichinayki. Iskay kuti turu qillqawan (**) k'ancharichisqa qillqata qillqay."
        elif self.language == 'zu':
            return f"Empendulweni yakho, khanyisa okungenani izingxenye ezingu-{n} usebenzisa i-Markdown, sebenzisa izinkanyezi ezimbili (**) ukumaka umbhalo okhanyisiwe."
        elif self.language == 'mg':
            return f"Amin'ny valinteninao, asongadino farafahakeliny {n} ampahany amin'ny alalan'ny Markdown, ampiasao ny kintana roa (**) mba hanondroana ny lahatsoratra nasongadina."
        elif self.language == 'sv':
            return f"I ditt svar, markera minst {n} delar med Markdown, använd dubbla asterisker (**) för att markera markerad text."
        elif self.language == 'ro':
            return f"În răspunsul tău, evidențiază cel puțin {n} părți folosind Markdown, folosește asteriscuri duble (**) pentru a marca textul evidențiat."
        elif self.language == 'tr':
            return f"Yanıtınızda, Markdown kullanarak en az {n} bölümü vurgulayın, vurgulanmış metni işaretlemek için çift yıldız (**) kullanın."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில், குறைந்தது {n} பகுதிகளை மார்க்டவுன் பயன்படுத்தி சிறப்பிக்கவும், சிறப்பிக்கப்பட்ட உரையைக் குறிக்க இரட்டை நட்சத்திரங்களை (**) பயன்படுத்தவும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում ընդգծեք առնվազն {n} հատված՝ օգտագործելով Markdown, օգտագործեք կրկնակի աստղանիշներ (**) ընդգծված տեքստը նշելու համար։"
        elif self.language == 'ko':
            return f"답변에서 Markdown을 사용하여 최소 {n}개의 부분을 강조하세요. 강조할 텍스트를 표시하기 위해 이중 별표(**)를 사용하세요."
        elif self.language == 'te':
            return f"మీ సమాధానంలో, కనీసం {n} భాగాలను మార్క్‌డౌన్ ఉపయోగించి హైలైట్ చేయండి, హైలైట్ చేసిన వచనాన్ని గుర్తించడానికి డబల్ ఆస్టరిస్క్‌లను (**) ఉపయోగించండి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში გამოყავით მინიმუმ {n} ნაწილი Markdown-ის გამოყენებით, გამოიყენეთ ორმაგი ვარსკვლავები (**) გამოყოფილი ტექსტის მოსანიშნად."
        elif self.language == 'ky':
            return f"Жообуңузда Markdown колдонуп, жок дегенде {n} бөлүктү белгилеңиз, белгиленген текстти белгилөө үчүн кош жылдызчаларды (**) колдонуңуз."
        elif self.language == 'pt':
            return f"Em sua resposta, destaque pelo menos {n} partes usando Markdown, use asteriscos duplos (**) para marcar o texto destacado."
        elif self.language == 'hi':
            return f"अपने उत्तर में, कम से कम {n} भागों को मार्कडाउन का उपयोग करके हाइलाइट करें, हाइलाइट किए गए पाठ को चिह्नित करने के लिए दोहरे तारांकन (**) का प्रयोग करें।"

    def check_following(self, response):
        # Count the number of highlighted parts.
        actual_count = response.count('**') // 2  # Each pair of **counts as one highlighted part.

        # If the required quantity is met or exceeded, return full marks.
        if actual_count >= self.n:
            return 1.0

        # Calculate the absolute value of the difference.
        diff = self.n - actual_count

        # Calculate the score using a formula.
        score = max(0, 1 - 0.1 * (diff ** 2))

        return score

class JsonOutput(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的整个回复应包裹在 JSON 格式中。请确保 JSON 格式正确且可以被解析。"
        elif self.language == 'en':
            return "Your entire output should be wrapped in JSON format. Please ensure that the JSON format is valid and can be parsed."
        elif self.language == 'ja':
            return "回答全体をJSON形式で記述してください。JSONの形式が正しく、解析可能であることを確認してください。"
        elif self.language == 'fr':
            return "Toute votre sortie doit être enveloppée dans un format JSON. Veuillez vous assurer que le format JSON est valide et peut être analysé."
        elif self.language == 'ms':
            return "Keluaran keseluruhan anda harus dibungkus dalam format JSON. Sila pastikan format JSON adalah sah dan boleh dihurai."
        elif self.language == 'tgl':
            return "Ang iyong buong sagot ay dapat nakabalot sa JSON format. Siguraduhing ang JSON format ay wasto at maaaring ma-parse."
        elif self.language == 'it':
            return "Il tuo intero output deve essere racchiuso nel formato JSON. Assicurati che il formato JSON sia valido e possa essere analizzato."
        elif self.language == 'bn':
            return "আপনার সম্পূর্ণ আউটপুট JSON ফর্ম্যাটে মোড়ানো উচিত। দয়া করে নিশ্চিত করুন যে JSON ফর্ম্যাটটি বৈধ এবং পার্স করা যেতে পারে৷"
        elif self.language == 'id':
            return "Seluruh output Anda harus dibungkus dalam format JSON. Pastikan bahwa format JSON tersebut valid dan dapat diparsing."
        # New languages
        elif self.language == 'qu':
            return "Llapan kutichiyniykin JSON formatupi p'isturisqa kanan. Ama hina kaspa, JSON formatuta allin kasqanta chaymanta parsiy atikusqanta qawaykuy."
        elif self.language == 'zu':
            return "Yonke impendulo yakho kufanele igoqwe ngefomethi ye-JSON. Sicela uqinisekise ukuthi ifomethi ye-JSON iyavumeleka futhi ingahlahlwa."
        elif self.language == 'mg':
            return "Ny valiny rehetra dia tokony ho voafono ao anatin'ny JSON format. Azafady hamarino fa azo ampiasaina sy azo tsinjaraina ny JSON format."
        elif self.language == 'sv':
            return "Hela din utdata ska vara insvept i JSON-format. Se till att JSON-formatet är giltigt och kan parsas."
        elif self.language == 'ro':
            return "Întreaga ieșire trebuie să fie încadrată în format JSON. Asigură-te că formatul JSON este valid și poate fi analizat."
        elif self.language == 'tr':
            return "Tüm çıktınız JSON formatında sarmalanmış olmalıdır. Lütfen JSON formatının geçerli ve ayrıştırılabilir olduğundan emin olun."
        elif self.language == 'ta':
            return "உங்கள் முழு வெளியீடும் JSON வடிவத்தில் சுற்றப்பட்டிருக்க வேண்டும். JSON வடிவம் செல்லுபடியாகும் மற்றும் அலகிடக்கூடியதாக இருப்பதை உறுதிசெய்யவும்."
        elif self.language == 'hy':
            return "Ձեր ամբողջ պատասխանը պետք է լինի JSON ձևաչափով։ Խնդրում ենք համոզվել, որ JSON ձևաչափը վավեր է և կարող է վերլուծվել։"
        elif self.language == 'ko':
            return "전체 출력은 JSON 형식으로 감싸져야 합니다. JSON 형식이 유효하고 파싱될 수 있는지 확인하세요."
        elif self.language == 'te':
            return "మీ మొత్తం అవుట్‌పుట్ JSON ఫార్మాట్‌లో చుట్టబడి ఉండాలి. JSON ఫార్మాట్ చెల్లుబాటు అయ్యేదిగా మరియు పార్స్ చేయగలిగేదిగా ఉండేలా చూసుకోండి."
        elif self.language == 'ka':
            return "თქვენი მთლიანი გამოტანა უნდა იყოს JSON ფორმატში. გთხოვთ, დარწმუნდეთ, რომ JSON ფორმატი სწორია და შეიძლება დამუშავდეს."
        elif self.language == 'ky':
            return "Сиздин бүткүл жообуңуз JSON форматында болушу керек. JSON форматынын жарактуу жана талдоого мүмкүн болгонун текшериңиз."
        elif self.language == 'pt':
            return "Toda a sua saída deve estar envolvida no formato JSON. Por favor, certifique-se de que o formato JSON é válido e pode ser analisado."
        elif self.language == 'hi':
            return "आपका पूरा आउटपुट JSON प्रारूप में लिपटा होना चाहिए। कृपया सुनिश्चित करें कि JSON प्रारूप मान्य है और पार्स किया जा सकता है।"

    def check_following(self, response):
        # Remove possible Markdown code block markers.
        response = response.strip()

        # Regular expressions: Remove code block markers in forms such as ```json, ```python, ```javascript, or other similar forms.
        # Match any code block markers that start with ``` and may be followed by a language identifier (such as json, python, javascript, etc.)
        response = re.sub(r'^```[a-zA-Z]*', '', response)
        response = re.sub(r'^```', '', response)  # Process the opening ``` (without a language identifier)
        response = re.sub(r'```$', '', response)  # Process the closing ```

        response = response.strip()  # Remove leading and trailing whitespace characters again.

        try:
            # Check if the JSON format is correct.
            json.loads(response)
            return 1.0  # If the JSON format is correct, return 1 point.
        except json.JSONDecodeError:
            return 0.0  # If the JSON format is incorrect, return 0 points.


class TwoAnswersWithSeparator(Instruction):
    def build_description(self, sentence):
        self.sentence = sentence
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你应该给出两个不同的回答。回答之间先换行，然后用\"{self.sentence}\"来分隔。"
        elif self.language == 'en':
            return f'You should provide two different responses. Start with a line break between responses, then separate them with \"{self.sentence}\".'
        elif self.language == 'ja':
            return f'二つの異なる回答を提供してください。回答と回答の間は改行し、"{self.sentence}"で区切ってください。'
        elif self.language == 'fr':
            return f'Vous devez fournir deux réponses différentes. Commencez par un saut de ligne entre les réponses, puis séparez-les par "{self.sentence}".'
        elif self.language == 'ms':
            return f'Anda harus menyediakan dua jawapan yang berbeza. Mulakan dengan pemisah baris antara jawapan, kemudian pisahkan mereka dengan \"{self.sentence}\".'
        elif self.language == 'tgl':
            return f'Dapat kang magbigay ng dalawang magkaibang sagot. Maglagay ng line break sa pagitan ng mga sagot, pagkatapos ay gumamit ng \"{self.sentence}\" para paghiwaliyin ito.'
        elif self.language == 'it':
            return f'Dovresti fornire due risposte diverse. Inizia con una riga vuota tra le risposte, poi separale con \"{self.sentence}\".'
        elif self.language == 'bn':
            return f'আপনি দুটি ভিন্ন প্রতিক্রিয়া প্রদান করা উচিত. প্রতিক্রিয়াগুলির মধ্যে একটি লাইন বিরতি দিয়ে শুরু করুন, তারপর \"{self.sentence}\" দিয়ে আলাদা করুন।'
        elif self.language == 'id':
            return f'Anda harus memberikan dua tanggapan yang berbeda. Mulailah dengan baris kosong antara tanggapan, lalu pisahkan dengan \"{self.sentence}\".'
        # New languages
        elif self.language == 'qu':
            return f'Iskay wak kutichiykunata qunaykin. Kutichiykunapura huk seq\'eta churay, chaymantaqa \"{self.sentence}\" nisqawan t\'aqay.'
        elif self.language == 'zu':
            return f'Kufanele unikeze izimpendulo ezimbili ezehlukile. Qala ngokushiya umugqa phakathi kwezimpendulo, bese uzehlukanisa ngo-\"{self.sentence}\".'
        elif self.language == 'mg':
            return f'Tokony hanome valiny roa samihafa ianao. Atombohy amin\'ny elanelana iray eo anelanelan\'ny valiny, avy eo sarahina amin\'ny \"{self.sentence}\".'
        elif self.language == 'sv':
            return f'Du bör ge två olika svar. Börja med en radbrytning mellan svaren, separera dem sedan med \"{self.sentence}\".'
        elif self.language == 'ro':
            return f'Ar trebui să oferi două răspunsuri diferite. Începe cu o linie nouă între răspunsuri, apoi separă-le cu \"{self.sentence}\".'
        elif self.language == 'tr':
            return f'İki farklı yanıt vermelisiniz. Yanıtlar arasında bir satır boşluğuyla başlayın, ardından \"{self.sentence}\" ile ayırın.'
        elif self.language == 'ta':
            return f'நீங்கள் இரண்டு வெவ்வேறு பதில்களை வழங்க வேண்டும். பதில்களுக்கு இடையில் வரி இடைவெளியுடன் தொடங்கி, பின்னர் அவற்றை \"{self.sentence}\" கொண்டு பிரிக்கவும்.'
        elif self.language == 'hy':
            return f'Դուք պետք է տաք երկու տարբեր պատասխաններ։ Սկսեք պատասխանների միջև տողադարձով, այնուհետև բաժանեք դրանք \"{self.sentence}\"-ով։'
        elif self.language == 'ko':
            return f'두 가지 다른 답변을 제공해야 합니다. 답변 사이에 줄바꿈을 하고 \"{self.sentence}\"로 구분하세요.'
        elif self.language == 'te':
            return f'మీరు రెండు వేర్వేరు సమాధానాలు ఇవ్వాలి. సమాధానాల మధ్య లైన్ బ్రేక్‌తో ప్రారంభించి, తర్వాత వాటిని \"{self.sentence}\"తో వేరు చేయండి.'
        elif self.language == 'ka':
            return f'თქვენ უნდა მოგვაწოდოთ ორი განსხვავებული პასუხი. დაიწყეთ პასუხებს შორის ხაზის გადატანით, შემდეგ გამოყავით ისინი \"{self.sentence}\"-ით.'
        elif self.language == 'ky':
            return f'Сиз эки башка жооп бериши керексиз. Жооптордун ортосунда сап таштап баштап, андан кийин аларды \"{self.sentence}\" менен бөлүңүз.'
        elif self.language == 'pt':
            return f'Você deve fornecer duas respostas diferentes. Comece com uma quebra de linha entre as respostas, depois separe-as com \"{self.sentence}\".'
        elif self.language == 'hi':
            return f'आपको दो अलग-अलग उत्तर देने चाहिए। उत्तरों के बीच एक लाइन ब्रेक से शुरू करें, फिर उन्हें \"{self.sentence}\" से अलग करें।'

    def clean_text(self, text):
        """Remove all punctuation marks and extra whitespace characters, leaving only letters and numbers."""
        return re.sub(r'\W+', '', text.strip().lower())  # Convert to lowercase and remove non-alphanumeric characters.

    def check_following(self, response):
        # Cleaned separated sentences (ignoring punctuation marks and whitespace characters, and ignoring case)
        clean_separator = self.clean_text(self.sentence)

        # Response after removing punctuation marks and extra whitespace characters
        clean_response = self.clean_text(response)

        # Check the number of times the delimiter appears in the response.
        separator_count = clean_response.count(clean_separator)

        # If the delimiter appears exactly once, return 1 point; otherwise, return 0 points.
        return 1.0 if separator_count == 1 else 0.0


class MarkdownTitle(Instruction):
    def build_description(self, max_length):
        self.max_length = max_length
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中，必须有一个带有 # 标记的标题，且标题长度不超过{max_length}个字。"
        elif self.language == 'en':
            return f"In your response, a #-marked title, not exceeding {max_length} words, is required."
        elif self.language == 'ja':
            return f"回答の中に、#記号で示されたタイトルを含める必要があり、そのタイトルは{max_length}文字を超えてはいけません。"
        elif self.language == 'fr':
            return f"Dans votre réponse, un titre marqué par #, ne dépassant pas {max_length} mots, est requis."
        elif self.language == 'ms':
            return f"Dalam jawapan anda, tajuk dengan #-marked, tidak melebihi {max_length} perkataan, diperlukan."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, kinakailangan na mayroong isang pamagat na may # na tanda, at ang haba ng pamagat ay hindi lalagpas sa {max_length} na mga salita."
        elif self.language == 'it':
            return f"Nella tua risposta, è richiesto un titolo contrassegnato con #, che non superi {max_length} caratteri."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়ায়, একটি #-চিহ্নিত শিরোনাম, {max_length} অক্ষরের বেশি নয়, প্রয়োজন৷"
        elif self.language == 'id':
            return f"Dalam tanggapan Anda, diperlukan sebuah judul yang diawali dengan tanda #, dan judul tersebut tidak boleh melebihi {max_length} karakter."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, huk # qillqawan qallariyniyuq sutichayuq kanan, manataq {max_length} simikunamanta aswan hatunchu kanan."
        elif self.language == 'zu':
            return f"Empendulweni yakho, kudingeka isihloko esinemakhi ye-#, esingedluli amagama angu-{max_length}."
        elif self.language == 'mg':
            return f"Ao amin'ny valinteninao, ilaina ny lohateny misy marika #, tsy mihoatra ny teny {max_length}."
        elif self.language == 'sv':
            return f"I ditt svar krävs en #-markerad rubrik som inte överstiger {max_length} ord."
        elif self.language == 'ro':
            return f"În răspunsul tău, este necesar un titlu marcat cu #, care să nu depășească {max_length} cuvinte."
        elif self.language == 'tr':
            return f"Yanıtınızda, # işareti ile belirtilmiş ve {max_length} kelimeyi geçmeyen bir başlık bulunmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில், # குறியீடு கொண்ட தலைப்பு ஒன்று தேவை, மேலும் அது {max_length} சொற்களை மீறக்கூடாது."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում պահանջվում է #-նշված վերնագիր, որը չպետք է գերազանցի {max_length} բառը։"
        elif self.language == 'ko':
            return f"답변에는 # 기호로 표시된 제목이 있어야 하며, 제목은 {max_length}자를 초과하지 않아야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో, # గుర్తుతో కూడిన శీర్షిక ఉండాలి, మరియు అది {max_length} పదాలను మించకూడదు."
        elif self.language == 'ka':
            return f"თქვენს პასუხში საჭიროა #-ით მონიშნული სათაური, რომელიც არ უნდა აღემატებოდეს {max_length} სიტყვას."
        elif self.language == 'ky':
            return f"Жообуңузда # белгиси менен белгиленген жана {max_length} сөздөн ашпаган аталыш болушу керек."
        elif self.language == 'pt':
            return f"Em sua resposta, é necessário um título marcado com #, não excedendo {max_length} palavras."
        elif self.language == 'hi':
            return f"आपके उत्तर में # चिह्न के साथ एक शीर्षक होना चाहिए, जो {max_length} शब्दों से अधिक नहीं होना चाहिए।"

    def clean_title(self, title):
        """Clean up special characters and Markdown tags in the title."""
        title = re.sub(r'\*\*(.*?)\*\*', r'\1', title) 
        title = re.sub(r'\*(.*?)\*', r'\1', title)  
        title = re.sub(r'`(.*?)`', r'\1', title)  
        title = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', title)  
        return title.strip()

    def check_following(self, response):
        pattern = r'^\s*(#{1,6})\s+(.+)$'
        lines = response.split('\n')

        # First, check if there are any markdown headings.
        has_title = False
        title_length = 0

        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                has_title = True
                title = match.group(2).strip()
                cleaned_title = self.clean_title(title)

                # Calculate the title length based on language grouping.
                # Group 1: Languages that use character counting
                if self.language in ['zh', 'ja', 'ko']:
                    if self.language == 'zh':
                        chars = re.findall(r'[\u4e00-\u9fff]', cleaned_title)
                    elif self.language == 'ja':
                        chars = re.findall(r'[ぁ-んァ-ン一-龥]', cleaned_title)
                    else:  # ko
                        chars = re.findall(r'[가-힣]', cleaned_title)
                    title_length = len(chars)

                # Group 2: Languages that use a special character system
                elif self.language in ['ta', 'te', 'hi']:
                    if self.language == 'ta':
                        chars = re.findall(r'[\u0B80-\u0BFF]', cleaned_title)
                    elif self.language == 'te':
                        chars = re.findall(r'[\u0C00-\u0C7F]', cleaned_title)
                    else:  # hi
                        chars = re.findall(r'[\u0900-\u097F]', cleaned_title)
                    title_length = len(chars)

                # Group 3: Languages that use spaces to separate words
                else:
                    words = re.findall(r'\b\w+\b', cleaned_title.lower())
                    title_length = len(words)
                break

        # If no markdown heading is found, return 0 points.
        if not has_title:
            return 0.0

        # If there is a title, 0.1 points will be given first.
        score = 0.1

        # If the length is within the range, an additional 0.9 points will be awarded.
        if title_length <= self.max_length:
            return 1.0

        # Calculate the length difference and score it.
        diff = title_length - self.max_length
        length_score = max(0, 0.9 - 0.1 * (diff ** 2))

        return score + length_score


class OrderedList(Instruction):
    def build_description(self, n):
        self.n = n
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中，必须包含一个有序列表，列表项数量为{n}个，并且每个列表项应以数字和句点开头，例如\"1.\"、\"2.\"等。"
        elif self.language == 'en':
            return f"Your response must include an ordered list with {n} items and each list item should start with a number and a period, such as '1.', '2.', etc."
        elif self.language == 'ja':
            return f"回答の中に、{n}項目の番号付きリストを含める必要があります。各項目は「1.」「2.」などのように番号とピリオドで始めてください。"
        elif self.language == 'fr':
            return f"Votre réponse doit inclure une liste ordonnée avec {n} éléments et chaque élément de la liste doit commencer par un numéro et un point, comme \"1.\", \"2.\", etc."
        elif self.language == 'ms':
            return f"Jawapan anda mesti mengandungi senarai susunan dengan {n} item dan setiap item senarai mesti bermula dengan nombor dan titik, seperti '1.', '2.', dll."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, kinakailangang maglaman ito ng isang nakaayos na listahan na may {n} na mga item, at bawat item ay dapat magsimula sa numero at tuldok, tulad ng '1.', '2.', atbp."
        elif self.language == 'it':
            return f"La tua risposta deve includere un elenco numerato con {n} voci, e ogni voce dell'elenco dovrebbe iniziare con un numero e un punto, come '1.', '2.', ecc."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া অবশ্যই {n} আইটেম সহ একটি অর্ডার করা তালিকা অন্তর্ভুক্ত করতে হবে এবং প্রতিটি তালিকা আইটেম একটি সংখ্যা এবং একটি পিরিয়ড দিয়ে শুরু হওয়া উচিত, যেমন '1.', '2.', ইত্যাদি।"
        elif self.language == 'id':
            return f"Tanggapan Anda harus mencakup daftar terurut dengan {n} item, dan setiap item dalam daftar harus diawali dengan angka dan titik, seperti '1.', '2.', dan seterusnya."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi {n} qillqakunayuq yupasqa yupana kanan. Sapa qillqaqa yupawan puntuyuqwan qallarinqa, kayhina '1.', '2.', hukninkuna."
        elif self.language == 'zu':
            return f"Impendulo yakho kufanele ibe nohlu oluhlelelwe olune-{n} izinto, futhi into ngayinye kufanele iqale ngenombolo kanye nangongqi, njenge-'1.', '2.', njll."
        elif self.language == 'mg':
            return f"Ny valinteninao dia tsy maintsy ahitana lisitra misy zavatra {n}, ary ny zavatra tsirairay dia tokony hanomboka amin'ny isa sy teboka, toy ny '1.', '2.', sns."
        elif self.language == 'sv':
            return f"Ditt svar måste innehålla en ordnad lista med {n} objekt och varje listobjekt ska börja med ett nummer och en punkt, som '1.', '2.', osv."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să includă o listă ordonată cu {n} elemente, și fiecare element trebuie să înceapă cu un număr și un punct, precum '1.', '2.', etc."
        elif self.language == 'tr':
            return f"Yanıtınız {n} öğeli sıralı bir liste içermeli ve her liste öğesi bir sayı ve nokta ile başlamalıdır, örneğin '1.', '2.' vb."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் {n} உருப்படிகள் கொண்ட வரிசைப்படுத்தப்பட்ட பட்டியல் இருக்க வேண்டும், மேலும் ஒவ்வொரு பட்டியல் உருப்படியும் எண் மற்றும் புள்ளியுடன் தொடங்க வேண்டும், எ.கா. '1.', '2.' போன்றவை."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը պետք է պարունակի կարգավորված ցուցակ {n} տարրերով, և յուրաքանչյուր ցուցակի տարր պետք է սկսվի թվով և կետով, օրինակ՝ '1.', '2.' և այլն։"
        elif self.language == 'ko':
            return f"답변에는 {n}개의 항목이 있는 순서가 있는 목록이 포함되어야 하며, 각 목록 항목은 숫자와 마침표로 시작해야 합니다(예: '1.', '2.' 등)."
        elif self.language == 'te':
            return f"మీ సమాధానంలో {n} అంశాలతో క్రమబద్ధమైన జాబితా ఉండాలి, మరియు ప్రతి జాబితా అంశం సంఖ్య మరియు చుక్కతో ప్రారంభం కావాలి, ఉదాహరణకు '1.', '2.' మొదలైనవి."
        elif self.language == 'ka':
            return f"თქვენი პასუხი უნდა შეიცავდეს დალაგებულ სიას {n} ელემენტით, და თითოეული სიის ელემენტი უნდა იწყებოდეს რიცხვით და წერტილით, მაგალითად '1.', '2.' და ა.შ."
        elif self.language == 'ky':
            return f"Жообуңузда {n} элементтен турган иреттүү тизме болушу керек, жана ар бир тизме элементи сан жана чекит менен башталышы керек, мисалы '1.', '2.' ж.б."
        elif self.language == 'pt':
            return f"Sua resposta deve incluir uma lista ordenada com {n} itens, e cada item da lista deve começar com um número e um ponto, como '1.', '2.', etc."
        elif self.language == 'hi':
            return f"आपके उत्तर में {n} वस्तुओं की एक क्रमबद्ध सूची होनी चाहिए, और प्रत्येक सूची वस्तु संख्या और बिंदु से शुरू होनी चाहिए, जैसे '1.', '2.' आदि।"

    def check_following(self, response):
        lines = response.split('\n')

        # Expand the regular expression to match ordered list items in more formats, including punctuation commonly used in different languages.
        pattern = r'^\d+[\.\、\)\។\।\፡\։\।]'  # Some commonly used punctuation marks from other languages have been added.
        list_items = [line.strip() for line in lines if re.match(pattern, line.strip())]

        actual_count = len(list_items)

        # If the required quantity is met or exceeded, return the full score.
        if actual_count >= self.n:
            return 1.0

        # Calculate the absolute value of the difference
        diff = self.n - actual_count

        # Calculate the score using the formula.
        score = max(0, 1 - 0.1 * (diff ** 2))

        return score


class MarkdownBoldItalicParagraph(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "在你的回复中，所有的段落必须以Markdown的\"***\"开头，表示加粗和斜体。"
        elif self.language == 'en':
            return "In your response, all paragraphs must start with Markdown's \"***\" to indicate bold and italic."
        elif self.language == 'ja':
            return "回答の中の全ての段落は、太字と斜体を示すMarkdownの\"***\"で始めなければなりません。"
        elif self.language == 'fr':
            return "Dans votre réponse, tous les paragraphes doivent commencer par \"***\" de Markdown pour indiquer le gras et l'italique."
        elif self.language == 'ms':
            return "Dalam jawapan anda, semua perenggan mesti bermula dengan Markdown's \"***\" untuk menunjukkan tebal dan italik."
        elif self.language == 'tgl':
            return "Sa iyong sagot, lahat ng talata ay dapat magsimula sa \"***\" ng Markdown, na nangangahulugang naka-bold at italic."
        elif self.language == 'it':
            return "Nella tua risposta, tutti i paragrafi devono iniziare con il \"***\" di Markdown per indicare il grassetto e il corsivo."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়াতে, সমস্ত অনুচ্ছেদগুলিকে অবশ্যই Markdown \"***\" দিয়ে শুরু করতে হবে যাতে বোল্ড এবং তির্যক নির্দেশ করা হয়।"
        elif self.language == 'id':
            return "Dalam tanggapan Anda, setiap paragraf harus dimulai dengan tanda \"***\" untuk menunjukkan teks yang dicetak tebal dan miring."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi, llapan rakirisqakuna Markdown \"***\" nisqawan qallarinankuna sinchi qillqawan q'iwiyuqwan qawachisqa kananpaq."
        elif self.language == 'zu':
            return "Empendulweni yakho, zonke izigaba kufanele ziqale ngo-\"***\" we-Markdown ukukhombisa okugqamile nokuthambekile."
        elif self.language == 'mg':
            return "Amin'ny valinteninao, ny tapany rehetra dia tsy maintsy manomboka amin'ny \"***\" amin'ny Markdown mba hanehoana ny matevina sy italika."
        elif self.language == 'sv':
            return "I ditt svar måste alla stycken börja med Markdowns \"***\" för att indikera fet stil och kursiv."
        elif self.language == 'ro':
            return "În răspunsul tău, toate paragrafele trebuie să înceapă cu \"***\" din Markdown pentru a indica textul îngroșat și italic."
        elif self.language == 'tr':
            return "Yanıtınızda, tüm paragraflar kalın ve italik göstermek için Markdown'ın \"***\" işareti ile başlamalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலில், அனைத்து பத்திகளும் தடித்த மற்றும் சாய்வு எழுத்தைக் குறிக்க மார்க்டவுனின் \"***\" உடன் தொடங்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանում բոլոր պարբերությունները պետք է սկսվեն Markdown-ի \"***\"-ով՝ թավ և շեղատառ նշելու համար։"
        elif self.language == 'ko':
            return "답변의 모든 문단은 굵게와 기울임꼴을 나타내는 Markdown의 \"***\"로 시작해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో, అన్ని పేరాలు బోల్డ్ మరియు ఇటాలిక్‌ని సూచించడానికి మార్క్‌డౌన్ యొక్క \"***\"తో ప్రారంభం కావాలి."
        elif self.language == 'ka':
            return "თქვენს პასუხში ყველა პარაგრაფი უნდა იწყებოდეს Markdown-ის \"***\"-ით მუქი და დახრილი შრიფტის მისათითებლად."
        elif self.language == 'ky':
            return "Жообуңузда, бардык абзацтар калың жана курсив көрсөтүү үчүн Markdown'дун \"***\" белгиси менен башталышы керек."
        elif self.language == 'pt':
            return "Em sua resposta, todos os parágrafos devem começar com \"***\" do Markdown para indicar negrito e itálico."
        elif self.language == 'hi':
            return "आपके उत्तर में, सभी अनुच्छेदों को बोल्ड और इटैलिक दर्शाने के लिए Markdown के \"***\" से शुरू होना चाहिए।"

    def check_following(self, response):
        # Use regular expressions to split paragraphs and handle cases with multiple line breaks.
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', response) if p.strip()]

        # Count the number of paragraphs that do not meet the requirements.
        invalid_paragraphs = sum(1 for p in paragraphs if not p.lstrip().startswith('***'))

        # If all paragraphs meet the requirements, return the full score.
        if invalid_paragraphs == 0:
            return 1.0

        # Calculate the score
        score = max(0, 1 - 0.1 * (invalid_paragraphs ** 2))

        return score


class CopyRequest(Instruction):
    def build_description(self, request):
        self.request = request
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "在你的回复前面，先不加改动地重复一遍我的请求。"
        elif self.language == 'en':
            return "Repeat my request without any changes and then provide the answer."
        elif self.language == 'ja':
            return "まず私のリクエストをそのまま繰り返してから、回答を提供してください。"
        elif self.language == 'fr':
            return "Répétez ma demande sans aucune modification, puis fournissez la réponse."
        elif self.language == 'ms':
            return "Ulangi permintaan saya tanpa membuat sebarang perubahan dan kemudian berikan jawapan."
        elif self.language == 'tgl':
            return "Sa unahan ng iyong sagot, ulitin muna ang aking kahilingan nang walang pagbabago."
        elif self.language == 'it':
            return "Ripeti la mia richiesta senza modifiche e poi fornisci la risposta."
        elif self.language == 'bn':
            return "কোনো পরিবর্তন ছাড়াই আমার অনুরোধের পুনরাবৃত্তি করুন এবং তারপর উত্তর প্রদান করুন।"
        elif self.language == 'id':
            return "Ulangi permintaan saya tanpa ada perubahan, lalu berikan jawabannya."
        # New languages
        elif self.language == 'qu':
            return "Mañarqusqayta mana imatapas tikraspa ñawpaqta kutichiway."
        elif self.language == 'zu':
            return "Phinda isicelo sami ngaphandle kokushintja bese unikeza impendulo."
        elif self.language == 'mg':
            return "Avereno tsy misy fanovana ny fangatahako ary avy eo dia omeo ny valiny."
        elif self.language == 'sv':
            return "Upprepa min förfrågan utan några ändringar och ge sedan svaret."
        elif self.language == 'ro':
            return "Repetă cererea mea fără nicio modificare și apoi oferă răspunsul."
        elif self.language == 'tr':
            return "Önce isteğimi hiçbir değişiklik yapmadan tekrarlayın, sonra yanıtı verin."
        elif self.language == 'ta':
            return "எனது கோரிக்கையை எந்த மாற்றமும் இல்லாமல் திரும்பச் சொல்லி, பின்னர் பதிலை வழங்கவும்."
        elif self.language == 'hy':
            return "Կրկնեք իմ խնդրանքն առանց որևէ փոփոխության, այնուհետև տվեք պատասխանը։"
        elif self.language == 'ko':
            return "먼저 제 요청을 어떤 변경도 없이 반복한 다음 답변을 제공해 주세요."
        elif self.language == 'te':
            return "నా అభ్యర్థనను ఎటువంటి మార్పులు లేకుండా పునరావృతం చేసి, తర్వాత సమాధానం ఇవ్వండి."
        elif self.language == 'ka':
            return "გაიმეორეთ ჩემი თხოვნა ყოველგვარი ცვლილების გარეშე და შემდეგ მოგვაწოდეთ პასუხი."
        elif self.language == 'ky':
            return "Менин өтүнүчүмдү эч өзгөртүүсүз кайталап, андан кийин жооп бериңиз."
        elif self.language == 'pt':
            return "Repita meu pedido sem nenhuma alteração e depois forneça a resposta."
        elif self.language == 'hi':
            return "मेरे अनुरोध को बिना किसी बदलाव के दोहराएं और फिर उत्तर प्रदान करें।"

    def check_following(self, response):
        # Remove all non-alphanumeric characters at the beginning of "request" and "response".
        clean_request = re.sub(r'^[^\w\s]+', '', self.request.strip())
        clean_response = re.sub(r'^[^\w\s]+', '', response.strip())

        # Choose different text processing methods according to the language type.
        # Group 1: Languages using the Latin alphabet
        if self.language in ['en', 'fr', 'ms', 'tgl', 'it', 'id', 'qu', 'zu', 'mg', 'sv', 'ro', 'tr', 'pt']:
            clean_request = self.normalize_text(clean_request.lower())
            clean_response = self.normalize_text(clean_response.lower())

        # Group 2: Languages with special character systems
        elif self.language in ['ta', 'te', 'hi']:
            # Tamil (U+0B80-U+0BFF), Telugu (U+0C00-U+0C7F), Devanagari (U+0900-U+097F)
            clean_request = self.clean_special_script(clean_request)
            clean_response = self.clean_special_script(clean_response)

        # Group 3: Languages using CJK characters
        elif self.language in ['zh', 'ja', 'ko']:
            clean_request = self.to_halfwidth(clean_request)
            clean_response = self.to_halfwidth(clean_response)

        # Group 4: Languages using other non-Latin alphabet systems
        elif self.language in ['bn', 'hy', 'ka', 'ky']:
            # Keep it as it is, only remove whitespace characters.
            clean_request = ' '.join(clean_request.split())
            clean_response = ' '.join(clean_response.split())

        # Check if clean_response starts with clean_request.
        if clean_response.startswith(clean_request):
            return 1.0
        return 0.0

    def to_halfwidth(self, text):
        """ Convert full-width characters to half-width characters. """
        return ''.join([chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in text])

    def normalize_text(self, text):
        """Remove accent marks and special characters."""
        import unicodedata
        # Convert accented characters to basic letters.
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        return text

    def clean_special_script(self, text):
        """Clean text with special writing systems"""
        # Remove all whitespace characters because whitespace may not be important in these language systems.
        text = ''.join(text.split())
        return text


class BeforeAnswer(Instruction):
    def build_description(self, sentence, repeat_num):
        self.sentence = sentence
        self.repeat_num = repeat_num
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回答之前，重复{repeat_num}次\"{sentence}\"。"
        elif self.language == 'en':
            return f'Repeat {repeat_num} times \"{sentence}\" before response.'
        elif self.language == 'ja':
            return f'回答の前に、"{sentence}"を{repeat_num}回繰り返してください。'
        elif self.language == 'fr':
            return f'Répétez {repeat_num} fois "{sentence}" avant la réponse.'
        elif self.language == 'ms':
            return f'Ulangi {repeat_num} kali \"{sentence}\" sebelum jawapan.'
        elif self.language == 'tgl':
            return f'Bago ang iyong sagot, ulitin ng {repeat_num} beses ang \"{sentence}\".'
        elif self.language == 'it':
            return f'Ripeti {repeat_num} volte \"{sentence}\" prima della risposta.'
        elif self.language == 'bn':
            return f'প্রতিক্রিয়ার আগে {repeat_num} বার \"{sentence}\" পুনরাবৃত্তি করুন।'
        elif self.language == 'id':
            return f'Ulangi {repeat_num} kali \"{sentence}\" sebelum tanggapan.'
        # New languages
        elif self.language == 'qu':
            return f'Kutichisqaykimanta ñawpaqta \"{sentence}\" nisqata {repeat_num} kuti yapay.'
        elif self.language == 'zu':
            return f'Ngaphambi kwempendulo yakho, phinda u-\"{sentence}\" ka-{repeat_num}.'
        elif self.language == 'mg':
            return f'Alohan\'ny valinteninao, avereno in-{repeat_num} ny \"{sentence}\".'
        elif self.language == 'sv':
            return f'Upprepa \"{sentence}\" {repeat_num} gånger innan svaret.'
        elif self.language == 'ro':
            return f'Înainte de răspuns, repetă \"{sentence}\" de {repeat_num} ori.'
        elif self.language == 'tr':
            return f'Cevaptan önce \"{sentence}\" ifadesini {repeat_num} kez tekrarlayın.'
        elif self.language == 'ta':
            return f'உங்கள் பதிலுக்கு முன், \"{sentence}\" என்பதை {repeat_num} முறை திரும்பச் சொல்லுங்கள்.'
        elif self.language == 'hy':
            return f'Պատասխանից առաջ կրկնեք \"{sentence}\"-ը {repeat_num} անգամ։'
        elif self.language == 'ko':
            return f'답변하기 전에 \"{sentence}\"을(를) {repeat_num}번 반복하세요.'
        elif self.language == 'te':
            return f'మీ సమాధానానికి ముందు, \"{sentence}\"ని {repeat_num} సార్లు పునరావృతం చేయండి.'
        elif self.language == 'ka':
            return f'პასუხის გაცემამდე გაიმეორეთ \"{sentence}\" {repeat_num}-ჯერ.'
        elif self.language == 'ky':
            return f'Жооп берүүдөн мурун \"{sentence}\" дегенди {repeat_num} жолу кайталаңыз.'
        elif self.language == 'pt':
            return f'Antes da resposta, repita \"{sentence}\" {repeat_num} vezes.'
        elif self.language == 'hi':
            return f'अपने उत्तर से पहले \"{sentence}\" को {repeat_num} बार दोहराएं।'

    def normalize_text(self, text):
        """Remove accent marks and special characters (mainly used for languages that use the Latin alphabet)"""
        import unicodedata
        # Convert accented characters to basic letters
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        return text

    def check_following(self, response):
        # Choose different text cleaning methods according to the language type.
        # Group 1: Languages that use the Latin alphabet and have accent marks
        if self.language in ['fr', 'tgl', 'it', 'ro', 'pt']:
            clean_sentence = self.normalize_text(re.sub(r'[^\w\s]', '', self.sentence).strip())
            clean_response = self.normalize_text(re.sub(r'[^\w\s]', '', response).strip())

        # Group 2: Languages that use the Latin alphabet but do not require handling accents
        elif self.language in ['en', 'ms', 'id', 'qu', 'zu', 'mg', 'sv', 'tr']:
            clean_sentence = re.sub(r'[^\w\s]', '', self.sentence).strip()
            clean_response = re.sub(r'[^\w\s]', '', response).strip()

        # Group 3: Languages using CJK characters
        elif self.language in ['zh', 'ja', 'ko']:
            clean_sentence = re.sub(r'[^\w\s]', '', self.sentence).strip()
            clean_response = re.sub(r'[^\w\s]', '', response).strip()

        # Group 4: Languages using special character systems
        elif self.language in ['ta', 'te', 'hi']:
            # Retain characters within the corresponding Unicode range.
            if self.language == 'ta':
                pattern = r'[^\u0B80-\u0BFF\s]'
            elif self.language == 'te':
                pattern = r'[^\u0C00-\u0C7F\s]'
            else:  # hi
                pattern = r'[^\u0900-\u097F\s]'
            clean_sentence = re.sub(pattern, '', self.sentence).strip()
            clean_response = re.sub(pattern, '', response).strip()

        # Group 5: Languages that use other non-Latin alphabet systems
        else:  # bn, hy, ka, ky
            clean_sentence = re.sub(r'[^\w\s]', '', self.sentence).strip()
            clean_response = re.sub(r'[^\w\s]', '', response).strip()

        # Calculate the actual number of occurrences of duplicates
        actual_count = 0
        remaining_response = clean_response
        expected_sentence = clean_sentence.lower()

        while remaining_response.lower().startswith(expected_sentence):
            actual_count += 1
            remaining_response = remaining_response[len(expected_sentence):].lstrip()

        # If there are no duplicates at all, return 0 points directly.
        if actual_count == 0:
            return 0.0

        # Calculate the difference from the required number of repetitions
        diff = abs(self.repeat_num - actual_count)

        # Calculate the score using a formula.
        score = max(0, 1 - 0.2 * (diff ** 2))

        return score



class FirstLastSame(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的第一句话应该和最后一句完全相同。"
        elif self.language == 'en':
            return "The first sentence of your response should be exactly the same as the last sentence."
        elif self.language == 'ja':
            return "回答の最初の文と最後の文は完全に同じでなければなりません。"
        elif self.language == 'fr':
            return "La première phrase de votre réponse doit être exactement la même que la dernière phrase."
        elif self.language == 'ms':
            return "Ayat pertama dalam jawapan anda haruslah sama persis dengan pernyataan terakhir."
        elif self.language == 'tgl':
            return "Ang unang pangungusap ng iyong sagot ay dapat eksaktong kapareho ng huling pangungusap."
        elif self.language == 'it':
            return "La prima frase della tua risposta deve essere esattamente la stessa dell'ultima frase."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ার প্রথম বাক্যটি শেষ বাক্যটির মতোই হওয়া উচিত।"
        elif self.language == 'id':
            return "Kalimat pertama dalam tanggapan Anda harus persis sama dengan kalimat terakhir."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi ñawpaq rimasqayki qhipa rimasqaykiwan kaqlla kanan."
        elif self.language == 'zu':
            return "Umusho wokuqala empendulweni yakho kufanele ufane ncamashi nomusho wokugcina."
        elif self.language == 'mg':
            return "Ny fehezan-teny voalohany amin'ny valinteninao dia tokony hitovy tanteraka amin'ny fehezan-teny farany."
        elif self.language == 'sv':
            return "Den första meningen i ditt svar ska vara exakt samma som den sista meningen."
        elif self.language == 'ro':
            return "Prima propoziție din răspunsul tău trebuie să fie exact la fel ca ultima propoziție."
        elif self.language == 'tr':
            return "Yanıtınızın ilk cümlesi son cümle ile tamamen aynı olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் முதல் வாக்கியம் கடைசி வாக்கியத்தை போலவே இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի առաջին նախադասությունը պետք է լինի ճիշտ նույնը, ինչ վերջին նախադասությունը։"
        elif self.language == 'ko':
            return "답변의 첫 문장과 마지막 문장이 정확히 동일해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలోని మొదటి వాక్యం చివరి వాక్యంతో ఖచ్చితంగా ఒకేలా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის პირველი წინადადება უნდა იყოს ზუსტად იგივე, რაც ბოლო წინადადება."
        elif self.language == 'ky':
            return "Жообуңуздун биринчи сүйлөмү акыркы сүйлөм менен так бирдей болушу керек."
        elif self.language == 'pt':
            return "A primeira frase da sua resposta deve ser exatamente igual à última frase."
        elif self.language == 'hi':
            return "आपके उत्तर का पहला वाक्य अंतिम वाक्य के बिल्कुल समान होना चाहिए।"

    def normalize_text(self, text):
        """Remove accent marks and special characters"""
        import unicodedata
        # Convert accented characters to basic letters.
        text = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in text if not unicodedata.combining(c))

    def check_following(self, response):
        # Remove quotation marks [x]
        response_cleaned = re.sub(r'\[\d+\]', '', response.strip())

        # Define sentence termination symbols for various languages.
        sentence_endings = {
            'default': r'[.!?]',  # Latin language family
            'cjk': r'[。！？]',  # Chinese, Japanese and Korean (CJK)
            'bn': r'[।]',  # Bengali
            'ta': r'[.|。|।|!|?|？|முற்று]',  # Tamil
            'te': r'[.|。|।|!|?|？]',  # Telugu
            'hy': r'[:|։|.|!|?|՝]',  # Armenian
            'ka': r'[.|!|?|։]',  # Georgian
            'hi': r'[.|।|?|!]'  # Hindi
        }

        # Select appropriate sentence termination symbols according to the language.
        if self.language in ['zh', 'ja', 'ko']:
            ending = sentence_endings['cjk']
        elif self.language == 'bn':
            ending = sentence_endings['bn']
        elif self.language == 'ta':
            ending = sentence_endings['ta']
        elif self.language == 'te':
            ending = sentence_endings['te']
        elif self.language == 'hy':
            ending = sentence_endings['hy']
        elif self.language == 'ka':
            ending = sentence_endings['ka']
        elif self.language == 'hi':
            ending = sentence_endings['hi']
        else:
            ending = sentence_endings['default']

        # Split sentences
        sentences = re.split(f'(?<={ending})\s+', response_cleaned.strip())

        if len(sentences) < 2:
            return 0.0

        # Get the first sentence and the last sentence
        first_sentence = sentences[0].strip()
        last_sentence = sentences[-1].strip()

        # Clean the text
        def clean_text(text):
            # Remove all punctuation marks, numbers, and extra whitespace characters
            text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation marks
            text = re.sub(r'\d+', '', text)  # Delete numbers
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace characters
            return text.strip()

        first_sentence = clean_text(first_sentence)
        last_sentence = clean_text(last_sentence)

        # Special handling is required for languages that need to process accent marks.
        if self.language in ['fr', 'tgl', 'it', 'ro', 'pt']:
            first_sentence = self.normalize_text(first_sentence)
            last_sentence = self.normalize_text(last_sentence)

        # Compare while ignoring case.
        if re.match(re.escape(first_sentence), last_sentence, flags=re.IGNORECASE):
            return 1.0
        return 0.0


class LastSentence(Instruction):
    def build_description(self, repeat_num):
        self.repeat_num = repeat_num
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"在你的回复的最后，重复最后一句话{repeat_num}次。"
        elif self.language == 'en':
            return f"At the end of your response, repeat the last sentence {repeat_num} times."
        elif self.language == 'ja':
            return f"回答の最後に、最後の文を{repeat_num}回繰り返してください。"
        elif self.language == 'fr':
            return f"À la fin de votre réponse, répétez la dernière phrase {repeat_num} fois."
        elif self.language == 'ms':
            return f"Dalam pengakhiran jawapan anda, ulangi ayat terakhir {repeat_num} kali."
        elif self.language == 'tgl':
            return f"Sa dulo ng iyong sagot, ulitin ang huling pangungusap ng {repeat_num} beses."
        elif self.language == 'it':
            return f"Alla fine della tua risposta, ripeti l'ultima frase {repeat_num} volte."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া শেষে, শেষ বাক্যটি {repeat_num} বার পুনরাবৃত্তি করুন।"
        elif self.language == 'id':
            return f"Di akhir tanggapan Anda, ulangi kalimat terakhir {repeat_num} kali."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykip tukukuyninpi, qhipa rimasqaykita {repeat_num} kuti yapay."
        elif self.language == 'zu':
            return f"Ekupheleni kwempendulo yakho, phinda umusho wokugcina izikhathi ezingu-{repeat_num}."
        elif self.language == 'mg':
            return f"Amin'ny faran'ny valinteninao, avereno in-{repeat_num} ny fehezan-teny farany."
        elif self.language == 'sv':
            return f"I slutet av ditt svar, upprepa den sista meningen {repeat_num} gånger."
        elif self.language == 'ro':
            return f"La sfârșitul răspunsului tău, repetă ultima propoziție de {repeat_num} ori."
        elif self.language == 'tr':
            return f"Yanıtınızın sonunda, son cümleyi {repeat_num} kez tekrarlayın."
        elif self.language == 'ta':
            return f"உங்கள் பதிலின் முடிவில், கடைசி வாக்கியத்தை {repeat_num} முறை திரும்பச் சொல்லுங்கள்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանի վերջում կրկնեք վերջին նախադասությունը {repeat_num} անգամ։"
        elif self.language == 'ko':
            return f"답변의 마지막에 마지막 문장을 {repeat_num}번 반복하세요."
        elif self.language == 'te':
            return f"మీ సమాధానం చివరలో, చివరి వాక్యాన్ని {repeat_num} సార్లు పునరావృతం చేయండి."
        elif self.language == 'ka':
            return f"პასუხის ბოლოს გაიმეორეთ ბოლო წინადადება {repeat_num}-ჯერ."
        elif self.language == 'ky':
            return f"Жообуңуздун аягында, акыркы сүйлөмдү {repeat_num} жолу кайталаңыз."
        elif self.language == 'pt':
            return f"No final da sua resposta, repita a última frase {repeat_num} vezes."
        elif self.language == 'hi':
            return f"अपने उत्तर के अंत में, अंतिम वाक्य को {repeat_num} बार दोहराएं।"

    def normalize_text(self, text):
        "Remove accent marks and special characters"
        import unicodedata
        # Convert accented characters to basic letters
        text = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in text if not unicodedata.combining(c))

    def check_following(self, response):
        # Define sentence terminators for various languages
        sentence_endings = {
            'default': r'[.!?;:]',  
            'cjk': r'[。！？；：]',  
            'bn': r'[।]',  
            'ta': r'[.|。|।|!|?|？|முற்று]',  
            'te': r'[.|。|।|!|?|？]',  
            'hy': r'[:|։|.|!|?|՝]',  
            'ka': r'[.|!|?|։]',  
            'hi': r'[.|।|?|!]'  
        }

        # Choose appropriate sentence terminators according to the language.
        if self.language in ['zh', 'ja', 'ko']:
            ending = sentence_endings['cjk']
        elif self.language == 'bn':
            ending = sentence_endings['bn']
        elif self.language == 'ta':
            ending = sentence_endings['ta']
        elif self.language == 'te':
            ending = sentence_endings['te']
        elif self.language == 'hy':
            ending = sentence_endings['hy']
        elif self.language == 'ka':
            ending = sentence_endings['ka']
        elif self.language == 'hi':
            ending = sentence_endings['hi']
        else:
            ending = sentence_endings['default']

        # Split sentences
        sentences = [s.strip() for s in re.split(f'(?<={ending})\s+', response.strip()) if s.strip()]

        # If the number of sentences is insufficient, return 0 points directly.
        if len(sentences) < self.repeat_num + 1:
            return 0.0

        # Get the (repeat_num + 1)th sentence from the end (as the sentence to be repeated)
        target_sentence = sentences[-(self.repeat_num + 1)]

        # Choose an appropriate text processing method according to the language.
        if self.language in ['fr', 'tgl', 'it', 'ro', 'pt']:  # Languages that need to handle accent marks
            target_sentence = self.normalize_text(target_sentence)
            sentences = [self.normalize_text(s) for s in sentences[-self.repeat_num:]]

        # Calculate how many of the last n sentences are the same as the target sentence.
        actual_repeats = sum(1 for s in sentences[-self.repeat_num:]
                           if re.match(re.escape(target_sentence), s, flags=re.IGNORECASE))

        # If there is no repetition at all, return 0 points directly.
        if actual_repeats == 0:
            return 0.0

        # Calculate the difference from the required number of repetitions.
        diff = self.repeat_num - actual_repeats

        # Calculate the score using a formula.
        score = max(0, 1 - 0.2 * (diff ** 2))

        return score


class SentenceNTimes(Instruction):
    def build_description(self, n, sentence):
        self.n = n
        self.sentence = sentence
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中，必须出现{n} 次\"{sentence}\"。"
        elif self.language == 'en':
            return f"In your response, \"{sentence}\" must appear {n} times."
        elif self.language == 'ja':
            return f"回答の中に、\"{sentence}\"が{n}回出現しなければなりません。"
        elif self.language == 'fr':
            return f"Dans votre réponse, \"{sentence}\" doit apparaître {n} fois."
        elif self.language == 'ms':
            return f"Dalam jawapan anda, \"{sentence}\" mesti muncul {n} kali."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, kinakailangang lumabas ang \"{sentence}\" ng {n} beses."
        elif self.language == 'it':
            return f"Nella tua risposta, \"{sentence}\" deve apparire {n} volte."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়াতে, \"{sentence}\" অবশ্যই {n} বার উপস্থিত হবে।"
        elif self.language == 'id':
            return f"Dalam tanggapan Anda, \"{sentence}\" harus muncul {n} kali."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, \"{sentence}\" nisqa {n} kuti rikunan."
        elif self.language == 'zu':
            return f"Empendulweni yakho, \"{sentence}\" kufanele kuvele izikhathi ezingu-{n}."
        elif self.language == 'mg':
            return f"Ao amin'ny valinteninao, \"{sentence}\" dia tsy maintsy miseho in-{n}."
        elif self.language == 'sv':
            return f"I ditt svar måste \"{sentence}\" förekomma {n} gånger."
        elif self.language == 'ro':
            return f"În răspunsul tău, \"{sentence}\" trebuie să apară de {n} ori."
        elif self.language == 'tr':
            return f"Yanıtınızda \"{sentence}\" {n} kez görünmelidir."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில், \"{sentence}\" {n} முறை தோன்ற வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում \"{sentence}\"-ը պետք է հայտնվի {n} անգամ։"
        elif self.language == 'ko':
            return f"답변에서 \"{sentence}\"이(가) {n}번 나타나야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో \"{sentence}\" {n} సార్లు కనిపించాలి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში \"{sentence}\" უნდა გამოჩნდეს {n}-ჯერ."
        elif self.language == 'ky':
            return f"Жообуңузда \"{sentence}\" {n} жолу көрүнүшү керек."
        elif self.language == 'pt':
            return f"Na sua resposta, \"{sentence}\" deve aparecer {n} vezes."
        elif self.language == 'hi':
            return f"आपके उत्तर में \"{sentence}\" {n} बार आना चाहिए।"

    def remove_punctuation(self, text):
        "Remove punctuation marks"
        return re.sub(r'[^\w\s]', '', text)

    def normalize_text(self, text):
        "Remove accent marks and special characters"
        import unicodedata
        # Convert accented characters to basic letters
        text = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in text if not unicodedata.combining(c))

    def check_following(self, response):
        # Sentences and replies after removing punctuation marks
        clean_sentence = self.remove_punctuation(self.sentence.strip())
        clean_response = self.remove_punctuation(response.strip())

        # Choose different text processing methods according to the language type.
        # Group 1: Languages that need to have accent marks removed
        if self.language in ['fr', 'tgl', 'it', 'ro', 'pt']:
            clean_sentence = self.normalize_text(clean_sentence)
            clean_response = self.normalize_text(clean_response)

        # Group 2: Languages that use special number systems
        if self.language in ['bn', 'ta', 'te', 'hi']:
            # Digital mapping dictionary
            digit_maps = {
                'bn': {'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
                      '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'},
                'ta': {'௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4',
                      '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9'},
                'te': {'౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4',
                      '౫': '5', '౬': '6', '౭': '7', '౮': '8', '౯': '9'},
                'hi': {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
                      '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
            }
            if self.language in digit_maps:
                for native, arabic in digit_maps[self.language].items():
                    clean_sentence = clean_sentence.replace(native, arabic)
                    clean_response = clean_response.replace(native, arabic)

        # Use regular expressions to match, ignoring case, and count the number of occurrences of the sentence.
        actual_count = len(re.findall(re.escape(clean_sentence), clean_response, flags=re.IGNORECASE))

        # If it does not appear at all, return 0 points directly.
        if actual_count == 0:
            return 0.0

        # Calculate the difference from the required number of times.
        diff = abs(self.n - actual_count)

        # Calculate the score using a formula.
        score = max(0, 1 - 0.2 * (diff ** 2))

        return score

class AllSentencesTwice(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中，所有的句子必须重复两次。"
        elif self.language == 'en':
            return "All sentences in your response must be repeated twice."
        elif self.language == 'ja':
            return "回答の中の全ての文章を二回ずつ繰り返して書いてください。"
        elif self.language == 'fr':
            return "Toutes les phrases de votre réponse doivent être répétées deux fois."
        elif self.language == 'ms':
            return "Semua ayat dalam jawapan anda mesti diulangi dua kali."
        elif self.language == 'tgl':
            return "Sa iyong sagot, lahat ng mga pangungusap ay dapat ulitin ng dalawang beses."
        elif self.language == 'it':
            return "Tutte le frasi della tua risposta devono essere ripetute due volte."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়াতে সমস্ত বাক্য অবশ্যই দুবার পুনরাবৃত্তি করতে হবে।"
        elif self.language == 'id':
            return "Semua kalimat dalam tanggapan Anda harus diulang dua kali."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi, llapan rimasqakuna iskay kuti qillqakuna kanan."
        elif self.language == 'zu':
            return "Yonke imisho empendulweni yakho kufanele iphindwe kabili."
        elif self.language == 'mg':
            return "Ny fehezan-teny rehetra ao amin'ny valinteninao dia tsy maintsy averina indroa."
        elif self.language == 'sv':
            return "Alla meningar i ditt svar måste upprepas två gånger."
        elif self.language == 'ro':
            return "Toate propozițiile din răspunsul tău trebuie repetate de două ori."
        elif self.language == 'tr':
            return "Yanıtınızdaki tüm cümleler iki kez tekrarlanmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் உள்ள அனைத்து வாக்கியங்களும் இரண்டு முறை திரும்ப வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի բոլոր նախադասությունները պետք է կրկնվեն երկու անգամ։"
        elif self.language == 'ko':
            return "답변의 모든 문장을 두 번씩 반복해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలోని అన్ని వాక్యాలు రెండుసార్లు పునరావృతం కావాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ყველა წინადადება უნდა გამეორდეს ორჯერ."
        elif self.language == 'ky':
            return "Жообуңуздагы бардык сүйлөмдөр эки жолудан кайталанышы керек."
        elif self.language == 'pt':
            return "Todas as frases em sua resposta devem ser repetidas duas vezes."
        elif self.language == 'hi':
            return "आपके उत्तर में सभी वाक्यों को दो बार दोहराया जाना चाहिए।"

    def normalize_text(self, text):
        "Remove accent marks and special characters"
        import unicodedata
        # Convert accented characters to basic letters.
        text = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in text if not unicodedata.combining(c))

    def check_following(self, response):
        # Define sentence terminators for various languages.
        sentence_endings = {
            'default': r'[.!?;:]',  
            'cjk': r'[。！？；：]', 
            'bn': r'[।]', 
            'ta': r'[.|。|।|!|?|？|முற்று]',  
            'te': r'[.|。|।|!|?|？]',  
            'hy': r'[:|։|.|!|?|՝]',  
            'ka': r'[.|!|?|։]',  
            'hi': r'[.|।|?|!]'  
        }

        # Select the appropriate sentence terminators based on the language.
        if self.language in ['zh', 'ja', 'ko']:
            ending = sentence_endings['cjk']
        elif self.language == 'bn':
            ending = sentence_endings['bn']
        elif self.language == 'ta':
            ending = sentence_endings['ta']
        elif self.language == 'te':
            ending = sentence_endings['te']
        elif self.language == 'hy':
            ending = sentence_endings['hy']
        elif self.language == 'ka':
            ending = sentence_endings['ka']
        elif self.language == 'hi':
            ending = sentence_endings['hi']
        else:
            ending = sentence_endings['default']

    
        sentences = [s.strip() for s in re.split(f'(?<={ending})\s+', response.strip()) if s.strip()]

        # If the number of sentences is odd, it means that at least one sentence is unpaired.
        if len(sentences) % 2 != 0:
            return 0.0

        # Special handling is applied to languages that require processing of accent marks.
        if self.language in ['fr', 'tgl', 'it', 'ro', 'pt']:
            sentences = [self.normalize_text(s) for s in sentences]

        # Calculate the number of sentence pairs that are not correctly repeated.
        invalid_pairs = sum(1 for i in range(0, len(sentences), 2)
                          if not re.match(re.escape(sentences[i]), sentences[i + 1], flags=re.IGNORECASE))

        # Calculate the score
        score = max(0, 1 - 0.2 * (invalid_pairs ** 2))

        return score



class WrapInQuotes(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "用双引号包裹你的整个回复。"
        elif self.language == 'en':
            return "Enclose your entire response in double quotes."
        elif self.language == 'ja':
            return "回答全体を二重引用符（""）で囲んでください。"
        elif self.language == 'fr':
            return "Enveloppez toute votre réponse dans des guillemets doubles."
        elif self.language == 'ms':
            return "Gunakan tanda petikan dalam keseluruhan jawapan anda."
        elif self.language == 'tgl':
            return "Ipaloob ang iyong buong sagot sa mga panipi."
        elif self.language == 'it':
            return "Racchiudi l'intera risposta tra virgolette doppie."
        elif self.language == 'bn':
            return "আপনার সম্পূর্ণ প্রতিক্রিয়া দ্বিগুণ উদ্ধৃতিতে সংযুক্ত করুন।"
        elif self.language == 'id':
            return "Letakkan seluruh tanggapan Anda di dalam tanda kutip ganda."
        # New languages
        elif self.language == 'qu':
            return "Llapan kutichisqaykita iskay qillqa sananawan muyuriy."
        elif self.language == 'zu':
            return "Faka impendulo yakho yonke phakathi kokumaki okuphindwe kabili."
        elif self.language == 'mg':
            return "Asio ny valinteninao rehetra ao anatin'ny teny natao indroa."
        elif self.language == 'sv':
            return "Omslut hela ditt svar med dubbla citattecken."
        elif self.language == 'ro':
            return "Încadrează întregul răspuns între ghilimele duble."
        elif self.language == 'tr':
            return "Tüm yanıtınızı çift tırnak işareti içine alın."
        elif self.language == 'ta':
            return "உங்கள் முழு பதிலையும் இரட்டை மேற்கோள் குறிகளுக்குள் வைக்கவும்."
        elif self.language == 'hy':
            return "Ձեր ամբողջ պատասխանը տեղադրեք կրկնակի չակերտների մեջ։"
        elif self.language == 'ko':
            return "전체 답변을 큰따옴표로 묶으세요."
        elif self.language == 'te':
            return "మీ మొత్తం సమాధానాన్ని ద్విత్వ ఉద్ధరణ చిహ్నాలలో ఉంచండి."
        elif self.language == 'ka':
            return "მოათავსეთ მთელი თქვენი პასუხი ორმაგ ბრჭყალებში."
        elif self.language == 'ky':
            return "Бүткүл жообуңузду кош тырмакчанын ичине жайгаштырыңыз."
        elif self.language == 'pt':
            return "Coloque toda a sua resposta entre aspas duplas."
        elif self.language == 'hi':
            return "अपने पूरे उत्तर को दोहरे उद्धरण चिह्नों में रखें।"

    def check_following(self, response):
        response = response.strip()

        # Define quotation mark pairs for different languages.
        quote_pairs = {
            'default': [('"', '"'), ('"', '"')],  
            'ja': [('「', '」'), ('『', '』'), ('"', '"')],  
            'ko': [('「', '」'), ('『', '』'), ('"', '"')],  
            'zh': [('「', '」'), ('『', '』'), ('"', '"')],  
            'ta': [('\"', '\"'), ('"', '"')],  
            'te': [('\"', '\"'), ('"', '"')],  
            'hy': [('«', '»'), ('„', '"')],  
            'ka': [('„', '"'), ('«', '»')],  
            'hi': [('\"', '\"'), ('"', '"')]  
        }

        # Select the appropriate pair of quotation marks according to the language.
        if self.language in quote_pairs:
            valid_quotes = quote_pairs[self.language]
        else:
            valid_quotes = quote_pairs['default']

        # Check if any valid pairs of quotation marks are used.
        has_quotes = any(response.startswith(start) and response.endswith(end)
                        for start, end in valid_quotes)

        return 1.0 if has_quotes else 0.0



class NoCommas(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "在你的整个回复中，避免使用任何逗号。"
        elif self.language == 'en':
            return "Avoid using any commas throughout your response."
        elif self.language == 'ja':
            return "回答の中ではカンマ（、）を一切使用しないでください。"
        elif self.language == 'fr':
            return "Évitez d'utiliser des virgules tout au long de votre réponse."
        elif self.language == 'ms':
            return "Jangan gunakan koma sama sekali dalam jawapan anda."
        elif self.language == 'tgl':
            return "Sa iyong buong sagot, iwasan ang paggamit ng anumang kuwit."
        elif self.language == 'it':
            return "Evita di usare virgole nella tua risposta."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া জুড়ে কোনো কমা ব্যবহার এড়িয়ে চলুন।"
        elif self.language == 'id':
            return "Hindari menggunakan tanda koma di seluruh tanggapan Anda."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi ama ima phankuta churankichu."
        elif self.language == 'zu':
            return "Gwema ukusebenzisa izinqaba kunoma yiyiphi indawo empendulweni yakho."
        elif self.language == 'mg':
            return "Aza mampiasa faingo amin'ny valinteninao."
        elif self.language == 'sv':
            return "Undvik att använda kommatecken i hela ditt svar."
        elif self.language == 'ro':
            return "Evită să folosești virgule în tot răspunsul tău."
        elif self.language == 'tr':
            return "Yanıtınız boyunca virgül kullanmaktan kaçının."
        elif self.language == 'ta':
            return "உங்கள் முழு பதிலிலும் காற்புள்ளிகளைப் பயன்படுத்துவதைத் தவிர்க்கவும்."
        elif self.language == 'hy':
            return "Ձեր ամբողջ պատասխանի մեջ խուսափեք ստորակետեր օգտագործելուց։"
        elif self.language == 'ko':
            return "답변 전체에서 쉼표 사용을 피하세요."
        elif self.language == 'te':
            return "మీ మొత్తం సమాధానంలో కామాలను ఉపయోగించడం నివారించండి."
        elif self.language == 'ka':
            return "თქვენს პასუხში მძიმეების გამოყენებას მოერიდეთ."
        elif self.language == 'ky':
            return "Жообуңузда үтүрлөрдү колдонбоңуз."
        elif self.language == 'pt':
            return "Evite usar vírgulas em toda a sua resposta."
        elif self.language == 'hi':
            return "अपने पूरे उत्तर में किसी भी अल्पविराम का प्रयोग न करें।"

    def check_following(self, response):
        # Define the comma characters of various languages.
        comma_chars = {
            'default': [','],  
            'zh': ['，', ','], 
            'ja': ['、', '，', ','],  
            'ko': ['、', '，', ','],  
            'bn': [',', '،'], 
            'ta': ['،', ','],  
            'te': ['،', ','],  
            'hy': [',', '，'], 
            'ka': [',', '，'],  
            'hi': [',', '，', '،']  
        }

        # Choose the appropriate comma character according to the language.
        if self.language in comma_chars:
            commas = comma_chars[self.language]
        else:
            commas = comma_chars['default']

        # Calculate the total number of occurrences of all types of commas.
        comma_count = sum(response.count(comma) for comma in commas)

        # Calculate the score using a formula.

        score = max(0, 1 - 0.03 * (comma_count ** 2))

        return score



class ReplaceWithExclamations(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "将你的回复中的所有逗号、句号和问号全部转换为感叹号。"
        elif self.language == 'en':
            return "Replace all commas, periods, and question marks in your response into exclamation marks."
        elif self.language == 'ja':
            return "回答の中の全ての読点（、）と句点（。）と疑問符（？）を感嘆符（！）に変換してください！"
        elif self.language == 'fr':
            return "Convertissez toutes les virgules, les points et les points d'interrogation de votre réponse en points d'exclamation."
        elif self.language == 'ms':
            return "Tukar semua koma, titik dan tanda soal dalam jawapan anda kepada tanda seru."
        elif self.language == 'tgl':
            return "Palitan ang lahat ng kuwit, tuldok, at tandang pananong sa iyong sagot ng tandang padamdam."
        elif self.language == 'it':
            return "Converti tutte le virgole, i punti e i punti interrogativi nella tua risposta in punti esclamativi."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া সমস্ত কমা, পিরিয়ড এবং প্রশ্ন চিহ্নকে বিস্ময়বোধক চিহ্নে রূপান্তর করুন।"
        elif self.language == 'id':
            return "Ubah semua tanda koma, titik, dan tanda tanya dalam tanggapan Anda menjadi tanda seru."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi llapan phankuta, puntuta, tapuna sanawantapas admiración sanawanwan rantiy."
        elif self.language == 'zu':
            return "Shintsha zonke izinqaba, amachashazi, nezimpawu zemibuzo empendulweni yakho zibe izimpawu zokuhlaba umkhosi."
        elif self.language == 'mg':
            return "Solohy famantarana fanontaniana ho famantarana hafaliana ny faingo, teboka ary famantarana fanontaniana rehetra ao amin'ny valinteninao."
        elif self.language == 'sv':
            return "Ersätt alla kommatecken, punkter och frågetecken i ditt svar med utropstecken."
        elif self.language == 'ro':
            return "Înlocuiește toate virgulele, punctele și semnele de întrebare din răspunsul tău cu semne de exclamare."
        elif self.language == 'tr':
            return "Yanıtınızdaki tüm virgülleri, noktaları ve soru işaretlerini ünlem işaretine dönüştürün."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் உள்ள அனைத்து காற்புள்ளிகள், முற்றுப்புள்ளிகள் மற்றும் கேள்விக்குறிகளை வியப்புக்குறிகளாக மாற்றவும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի բոլոր ստորակետերը, վերջակետերը և հարցական նշանները փոխարինեք բացականչական նշաններով։"
        elif self.language == 'ko':
            return "답변의 모든 쉼표, 마침표, 물음표를 느낌표로 바꾸세요."
        elif self.language == 'te':
            return "మీ సమాధానంలోని అన్ని కామాలు, పూర్ణవిరామాలు మరియు ప్రశ్నార్థక చిహ్నాలను ఆశ్చర్యార్థక చిహ్నాలుగా మార్చండి."
        elif self.language == 'ka':
            return "თქვენს პასუხში ყველა მძიმე, წერტილი და კითხვის ნიშანი შეცვალეთ ძახილის ნიშნით."
        elif self.language == 'ky':
            return "Жообуңуздагы бардык үтүрлөрдү, чекиттерди жана суроо белгилерин илеп белгисине алмаштырыңыз."
        elif self.language == 'pt':
            return "Substitua todas as vírgulas, pontos e pontos de interrogação na sua resposta por pontos de exclamação."
        elif self.language == 'hi':
            return "अपने उत्तर में सभी अल्पविराम, पूर्ण विराम और प्रश्नवाचक चिह्नों को विस्मयादिबोधक चिह्न में बदलें।"

    def check_following(self, response):
        # Define the punctuation mark mappings for various languages.
        punctuation_marks = {
            'default': [',', '.', '?'],  
            'zh': [',', '，', '.', '。', '?', '？'], 
            'ja': [',', '、', '.', '。', '?', '？'],  
            'ko': [',', '，', '.', '。', '?', '？'],  
            'bn': [',', '।', '?', ','],  
            'ta': [',', '।', '?', '？', '.'],  
            'te': [',', '।', '?', '？', '.'],  
            'hy': [',', '։', '՞', '.'],  
            'ka': [',', '.', '?', '։'],  
            'hi': [',', '।', '?', '？', '.']  
        }

        # Determine the punctuation marks that need to be checked.
        if self.language in punctuation_marks:
            to_check = punctuation_marks[self.language]
        else:
            to_check = punctuation_marks['default']

        # First, check if there is an exclamation mark (at least one exclamation mark is required).
        exclamation_marks = ['!', '！']
        if not any(mark in response for mark in exclamation_marks):
            return 0.0

        # Calculate the number of occurrences of punctuation marks that should not appear.
        wrong_punct_count = sum(response.count(punct) for punct in to_check)

        # Calculate the score using a formula.
        score = max(0, 1 - 0.03 * (wrong_punct_count ** 2))

        return score



class EndWithSemicolons(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中的所有句子必须以分号而不是句号结束。"
        elif self.language == 'en':
            return "All sentences in your response must end with a semicolon instead of a period."
        elif self.language == 'ja':
            return "回答の中の全ての文章は句点（。）ではなくセミコロン（；）で終わらせてください。"
        elif self.language == 'fr':
            return "Toutes les phrases de votre réponse doivent se terminer par un point-virgule au lieu d'un point."
        elif self.language == 'ms':
            return "Kesemuanya ayat dalam jawapan anda mesti diakhiri dengan titik koma bukan titik."
        elif self.language == 'tgl':
            return "Ang lahat ng mga pangungusap sa iyong sagot ay dapat magtapos sa tuldok-kuwit at hindi tuldok."
        elif self.language == 'it':
            return "Tutte le frasi della tua risposta devono finire con un punto e virgola invece che con un punto."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ায়, সমস্ত বাক্য অবশ্যই একটি সেমিকোলন দিয়ে শেষ হবে, একটি পিরিয়ড নয়।"
        elif self.language == 'id':
            return "Semua kalimat dalam tanggapan Anda harus diakhiri dengan titik koma, bukan dengan titik."
        # New languages
        elif self.language == 'qu':
            return "Llapan rimasqaykipi semicolonwan tukukunki mana puntuwan."
        elif self.language == 'zu':
            return "Yonke imisho empendulweni yakho kufanele iphethe ngekhoma-khefana kungekhona ngongqi."
        elif self.language == 'mg':
            return "Ny fehezan-teny rehetra ao amin'ny valinteninao dia tsy maintsy mifarana amin'ny teboka sy faingo fa tsy teboka."
        elif self.language == 'sv':
            return "Alla meningar i ditt svar måste avslutas med semikolon istället för punkt."
        elif self.language == 'ro':
            return "Toate propozițiile din răspunsul tău trebuie să se termine cu punct și virgulă în loc de punct."
        elif self.language == 'tr':
            return "Yanıtınızdaki tüm cümleler nokta yerine noktalı virgülle bitmelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் உள்ள அனைத்து வாக்கியங்களும் முற்றுப்புள்ளிக்கு பதிலாக அரைப்புள்ளியுடன் முடிய வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի բոլոր նախադասությունները պետք է ավարտվեն կետ-ստորակետով՝ վերջակետի փոխարեն։"
        elif self.language == 'ko':
            return "답변의 모든 문장은 마침표 대신 쌍반점으로 끝나야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలోని అన్ని వాక్యాలు పూర్ణవిరామం బదులుగా సెమీకోలన్‌తో ముగియాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ყველა წინადადება უნდა დასრულდეს წერტილ-მძიმით და არა წერტილით."
        elif self.language == 'ky':
            return "Жообуңуздагы бардык сүйлөмдөр чекит эмес, үтүрлүү чекит менен бүтүшү керек."
        elif self.language == 'pt':
            return "Todas as frases em sua resposta devem terminar com ponto e vírgula em vez de ponto final."
        elif self.language == 'hi':
            return "आपके उत्तर के सभी वाक्य पूर्णविराम के बजाय अर्धविराम से समाप्त होने चाहिए।"

    def check_following(self, response):
        # Define the sentence terminators and semicolon mappings for various languages.
        language_marks = {
            'default': {'endings': ['.', '!', '?'], 'semicolon': ';'}, 
            'cjk': {'endings': ['。', '！', '？'], 'semicolon': '；'},  
            'bn': {'endings': ['।'], 'semicolon': ';'},  
            'ta': {'endings': ['।', '.'], 'semicolon': ';'},  
            'te': {'endings': ['।', '.'], 'semicolon': ';'},  
            'hy': {'endings': ['։', '.'], 'semicolon': '；'},  
            'ka': {'endings': ['።', '.'], 'semicolon': ';'},  
            'hi': {'endings': ['।', '.'], 'semicolon': ';'}  
        }

        # # Select an Appropriate Set of Punctuation Marks
        if self.language in ['zh', 'ja', 'ko']:
            marks = language_marks['cjk']
        elif self.language in language_marks:
            marks = language_marks[self.language]
        else:
            marks = language_marks['default']

        # Construct sentence segmentation patterns
        ending_pattern = '|'.join(map(re.escape, marks['endings']))
        sentences = [s.strip() for s in re.split(f'(?<=[{ending_pattern}])\s+', response.strip()) if s.strip()]

        # If there are no sentences, return a score of 0.
        if not sentences:
            return 0.0

        # Calculate the number of sentences that do not end with a semicolon.
        wrong_endings = sum(1 for sentence in sentences
                          if not sentence.endswith(marks['semicolon']))

        # Calculate the score using a formula.
        score = max(0, 1 - 0.03 * (wrong_endings ** 2))

        return score




class ReplaceWithAsterisks(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中，所有的符号（逗号、句号、感叹号等）都必须用星号 * 替代。"
        elif self.language == 'en':
            return "In your response, all punctuation marks (commas, periods, exclamation marks, etc.) must be replaced with asterisks *."
        elif self.language == 'ja':
            return "回答の中の全ての句読点（読点、句点、感嘆符など）をアスタリスク（*）に置き換えてください。"
        elif self.language == 'fr':
            return "Dans votre réponse, tous les signes de ponctuation (virgules, points, points d'exclamation, etc.) doivent être remplacés par des astérisques *."
        elif self.language == 'ms':
            return "Dalam jawapan anda, semua tanda bacaan (koma, titik, tanda seru, dll.) mesti ditukar dengan bintang asterisk *."
        elif self.language == 'tgl':
            return "Sa iyong sagot, lahat ng mga pananda (koma, tuldok, tandang padamdam, atbp.) ay dapat palitan ng asterisks *."
        elif self.language == 'it':
            return "Nella tua risposta, tutti i segni di punteggiatura (virgole, punti, punti esclamativi, ecc.) devono essere sostituiti con asterischi * ."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ায়, সমস্ত বিরাম চিহ্ন (কমা, পিরিয়ড, বিস্ময় চিহ্ন, ইত্যাদি) তারকাচিহ্ন * দিয়ে প্রতিস্থাপিত করতে হবে।"
        elif self.language == 'id':
            return "Dalam tanggapan Anda, semua tanda baca (koma, titik, tanda seru, dll.) harus diganti dengan tanda bintang *."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi, llapan sanakuna (phankukuna, puntukuna, admiracionkuna, hukkuna) qoyllurchaki * nisqawan rantisqa kanan."
        elif self.language == 'zu':
            return "Empendulweni yakho, zonke izimpawu zokubhala (amakhoma, amachashazi, izimpawu zokuhlaba umkhosi, njll.) kufanele zishintshwe nge-asterisk *."
        elif self.language == 'mg':
            return "Amin'ny valinteninao, ny marika rehetra (faingo, teboka, famantarana hafaliana, sns.) dia tokony hosoloina kintana *."
        elif self.language == 'sv':
            return "I ditt svar måste alla skiljetecken (kommatecken, punkter, utropstecken, etc.) ersättas med asterisker *."
        elif self.language == 'ro':
            return "În răspunsul tău, toate semnele de punctuație (virgule, puncte, semne de exclamare, etc.) trebuie înlocuite cu asteriscuri *."
        elif self.language == 'tr':
            return "Yanıtınızda, tüm noktalama işaretleri (virgül, nokta, ünlem işareti vb.) yıldız işareti * ile değiştirilmelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில், அனைத்து நிறுத்தற்குறிகளும் (காற்புள்ளி, முற்றுப்புள்ளி, வியப்புக்குறி முதலியன) நட்சத்திரக்குறி * ஆல் மாற்றப்பட வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանում բոլոր կետադրական նշանները (ստորակետեր, վերջակետեր, բացականչական նշաններ և այլն) պետք է փոխարինվեն աստղանիշով *։"
        elif self.language == 'ko':
            return "답변에서 모든 문장부호(쉼표, 마침표, 느낌표 등)를 별표 *로 바꾸어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో, అన్ని విరామ చిహ్నాలు (కామాలు, పూర్ణవిరామాలు, ఆశ్చర్యార్థక చిహ్నాలు, మొదలైనవి) నక్షత్ర చిహ్నం *తో భర్తీ చేయాలి."
        elif self.language == 'ka':
            return "თქვენს პასუხში ყველა სასვენი ნიშანი (მძიმეები, წერტილები, ძახილის ნიშნები და ა.შ.) უნდა შეიცვალოს ვარსკვლავით *."
        elif self.language == 'ky':
            return "Жообуңузда бардык тыныш белгилери (үтүр, чекит, илеп белгиси ж.б.) жылдызча * менен алмаштырылышы керек."
        elif self.language == 'pt':
            return "Em sua resposta, todos os sinais de pontuação (vírgulas, pontos, pontos de exclamação, etc.) devem ser substituídos por asteriscos *."
        elif self.language == 'hi':
            return "आपके उत्तर में, सभी विराम चिह्नों (अल्पविराम, पूर्णविराम, विस्मयादिबोधक चिह्न, आदि) को तारांकन * से बदला जाना चाहिए।"

    def check_following(self, response):
        # Define the set of punctuation marks for various languages.
        punctuation_marks = {
            'default': [',', '.', '!', '?', ';', ':', '"', "'"],  
            'cjk': [',', '，', '.', '。', '!', '！', '?', '？', ';', '；', ':', '：', '"', '"', ''', '''],  # 中日韩标点
            'bn': [',', '।', '!', '?', ';', ':', '"', "'", ','],  
            'ta_te': [',', '।', '.', '!', '?', ':', '"', "'", '॥'],  
            'hy': [',', '։', '՜', '՞', '։', '՝', '«', '»', '—'],  
            'ka': [',', '.', '!', '?', ':', ';', '„', '"', '–', '—'],  
            'hi': [',', '।', '!', '?', ':', ';', '"', '\'', '॥']  
        }

        # Add special punctuation marks of European languages.
        european_extra = ['«', '»', '‹', '›', '„', '"', '‚', '\'', '—', '–']
        for lang in ['fr', 'ro', 'sv']:
            punctuation_marks[lang] = punctuation_marks['default'] + european_extra

        # Select an appropriate set of punctuation marks.
        if self.language in ['zh', 'ja', 'ko']:
            to_check = punctuation_marks['cjk']
        elif self.language in punctuation_marks:
            to_check = punctuation_marks[self.language]
        elif self.language in ['ta', 'te']:
            to_check = punctuation_marks['ta_te']
        else:
            to_check = punctuation_marks['default']

        # First, check if there is an asterisk (at least one asterisk is required).
        if '*' not in response:
            return 0.0

        # Calculate the number of occurrences of punctuation marks that should not appear.
        wrong_punct_count = sum(response.count(punct) for punct in to_check)

        # Calculate the score using a formula.
        score = max(0, 1 - 0.03 * (wrong_punct_count ** 2))

        return score



class SquareBrackets(Instruction):
    def build_description(self, n):
        self.n = n
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中至少包含{n}个引用，且引用内容必须用 [x] 的格式表示。"
        elif self.language == 'en':
            return f"Your response must contain at least {n} quotes, and the quoted content must be in [x] format."
        elif self.language == 'ja':
            return f"回答の中に少なくとも{n}個の引用を含める必要があり、引用内容は[x]の形式で表示しなければなりません。"
        elif self.language == 'fr':
            return f"Votre réponse doit contenir au moins {n} citations, et le contenu cité doit être au format [x]."
        elif self.language == 'ms':
            return f"Jawapan anda mesti mengandungi sekurang-kurangnya {n} petikan, dan kandungan yang dipetikan mesti dalam format [x]."
        elif self.language == 'tgl':
            return f"Ang iyong sagot ay dapat maglaman ng hindi bababa sa {n} na sipi, at ang nilalaman ng sipi ay dapat nasa [x] format."
        elif self.language == 'it':
            return f"La tua risposta deve contenere almeno {n} citazioni, e il contenuto citato deve essere nel formato [x]."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়াতে কমপক্ষে {n}টি উদ্ধৃতি থাকতে হবে এবং উদ্ধৃত সামগ্রী অবশ্যই [x] বিন্যাসে হতে হবে৷"
        elif self.language == 'id':
            return f"Tanggapan Anda harus mengandung setidaknya {n} kutipan, dan konten yang dikutip harus dalam format [x]."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi {n} willakuykunata churanayki, chaykunataq [x] nisqapi kanan."
        elif self.language == 'zu':
            return f"Impendulo yakho kufanele ibe nezicaphuno ezingekho ngaphansi kuka-{n}, futhi okuqoshiwe kufanele kube ngefomethi ye-[x]."
        elif self.language == 'mg':
            return f"Ny valinteninao dia tsy maintsy ahitana farafahakeliny teny nalaina {n}, ary ny votoatiny nalaina dia tsy maintsy amin'ny endrika [x]."
        elif self.language == 'sv':
            return f"Ditt svar måste innehålla minst {n} citat, och det citerade innehållet måste vara i [x]-format."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să conțină cel puțin {n} citate, iar conținutul citat trebuie să fie în formatul [x]."
        elif self.language == 'tr':
            return f"Yanıtınız en az {n} alıntı içermeli ve alıntılanan içerik [x] biçiminde olmalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் குறைந்தது {n} மேற்கோள்கள் இருக்க வேண்டும், மேலும் மேற்கோள் காட்டப்பட்ட உள்ளடக்கம் [x] வடிவத்தில் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը պետք է պարունակի առնվազն {n} մեջբերում, և մեջբերված բովանդակությունը պետք է լինի [x] ձևաչափով։"
        elif self.language == 'ko':
            return f"답변에는 최소 {n}개의 인용문이 포함되어야 하며, 인용된 내용은 [x] 형식이어야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో కనీసం {n} ఉల్లేఖనలు ఉండాలి, మరియు ఉల్లేఖించిన విషయం తప్పనిసరిగా [x] ఆకృతిలో ఉండాలి."
        elif self.language == 'ka':
            return f"თქვენი პასუხი უნდა შეიცავდეს მინიმუმ {n} ციტატას, და ციტირებული შინაარსი უნდა იყოს [x] ფორმატში."
        elif self.language == 'ky':
            return f"Жообуңузда жок дегенде {n} шилтеме болушу керек, жана шилтеме берилген мазмун [x] форматында болушу керек."
        elif self.language == 'pt':
            return f"Sua resposta deve conter pelo menos {n} citações, e o conteúdo citado deve estar no formato [x]."
        elif self.language == 'hi':
            return f"आपके उत्तर में कम से कम {n} उद्धरण होने चाहिए, और उद्धृत सामग्री [x] प्रारूप में होनी चाहिए।"

    def check_following(self, response):
        # Find all citations in the format [x] (with content inside the square brackets).
        citations = re.findall(r'\[.+?\]', response)

        # If there are no citations, return a score of 0 directly.
        if not citations:
            return 0.0

        # Calculate the difference between the number of citations and the required number.
        diff = max(0, self.n - len(citations))

        # Check if all citations conform to the [x] format.
        valid_format = all(re.match(r'\[.+?\]', citation) for citation in citations)

        # Calculate the base score using a formula.
        base_score = max(0, 1 - 0.3 * (diff ** 2))

        # If the format is incorrect, an additional 0.5 points will be deducted.
        final_score = max(0, base_score - (0 if valid_format else 0.5))

        return final_score



class StartFromZero(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中必须包含参考文献（用\"[x]\"的格式，x代表数字），且应该从第0个开始。"
        elif self.language == 'en':
            return "Your response must contain references, and your references should start from number 0."
        elif self.language == 'ja':
            return "回答の中に参考文献を含める必要があり、参考文献は[0]から始まる番号形式で表示してください。"
        elif self.language == 'fr':
            return "Votre réponse doit contenir des références, et vos références doivent commencer par le numéro 0."
        elif self.language == 'ms':
            return "Jawapan anda mesti mengandungi rujukan, dan rujukan anda harus bermula dari nombor 0."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat maglaman ng mga sanggunian (gamitin ang format na \"[x]\", kung saan ang x ay kumakatawan sa numero), at dapat magsimula mula sa 0."
        elif self.language == 'it':
            return "La tua risposta deve contenere riferimenti (nel formato \"[x]\", dove x rappresenta un numero) e i tuoi riferimenti dovrebbero partire dal numero 0."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অবশ্যই রেফারেন্স থাকতে হবে এবং আপনার রেফারেন্স 0 নম্বর থেকে শুরু হওয়া উচিত।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mengandung referensi, dan referensi Anda harus dimulai dari nomor 0."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi willakuykunata churanayki (\"[x]\" nisqawan, x yupayta qawachin), 0 yupaywan qallarispan."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibe nezindlela zokucaphuna (sebenzisa ifomethi \"[x]\", lapho u-x emele inombolo), futhi kufanele kuqale kunombolo 0."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy misy filazana ny loharano (mampiasa ny endrika \"[x]\", izay x dia manondro isa), ary tokony hanomboka amin'ny 0."
        elif self.language == 'sv':
            return "Ditt svar måste innehålla referenser (använd formatet \"[x]\", där x representerar ett nummer) och dina referenser ska börja från nummer 0."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să conțină referințe (folosind formatul \"[x]\", unde x reprezintă un număr) și referințele tale trebuie să înceapă de la numărul 0."
        elif self.language == 'tr':
            return "Yanıtınız referanslar içermeli (\"[x]\" biçiminde, x sayıyı temsil eder) ve referanslarınız 0 numaradan başlamalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் மேற்கோள்கள் இருக்க வேண்டும் (\"[x]\" வடிவத்தில், x என்பது எண்ணைக் குறிக்கிறது), மேலும் உங்கள் மேற்கோள்கள் 0 என்ற எண்ணில் இருந்து தொடங்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է պարունակի հղումներ (օգտագործելով \"[x]\" ձևաչափը, որտեղ x-ը թիվ է), և ձեր հղումները պետք է սկսվեն 0 համարից։"
        elif self.language == 'ko':
            return "답변에는 참고문헌이 포함되어야 하며(\"[x]\" 형식 사용, x는 숫자를 나타냄), 참고문헌은 0번부터 시작해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో సూచనలు ఉండాలి (\"[x]\" ఆకృతిని ఉపయోగించండి, ఇక్కడ x అంటే సంఖ్య), మరియు మీ సూచనలు 0 నుండి ప్రారంభం కావాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა შეიცავდეს მითითებებს (გამოიყენეთ ფორმატი \"[x]\", სადაც x არის რიცხვი) და თქვენი მითითებები უნდა დაიწყოს ნომრით 0."
        elif self.language == 'ky':
            return "Жообуңузда шилтемелер болушу керек (\"[x]\" форматын колдонуңуз, мында x сан дегенди билдирет) жана шилтемелериңиз 0 номеринен башталышы керек."
        elif self.language == 'pt':
            return "Sua resposta deve conter referências (usando o formato \"[x]\", onde x representa um número) e suas referências devem começar do número 0."
        elif self.language == 'hi':
            return "आपके उत्तर में संदर्भ होने चाहिए (\"[x]\" प्रारूप का उपयोग करें, जहां x एक संख्या है), और आपके संदर्भ संख्या 0 से शुरू होने चाहिए।"

    def check_following(self, response):
        # Check if citations in the format [x] (where x is any number) are used.
        has_format = bool(re.search(r'\[\d+\]', response))

        # Check if it starts from [0]
        starts_from_zero = bool(re.search(r'\[0\]', response))

        # Calculate the score
        format_score = 0.7 if has_format else 0.0
        zero_score = 0.3 if starts_from_zero else 0.0

        # If no citation format is used, the total score is 0.
        if not has_format:
            return 0.0

        return format_score + zero_score


class Inline(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中参考文献应该直接写在引用内容后面的括号里而不是写在回答末尾。"
        elif self.language == 'en':
            return "Your response must contain references, and the references should be included directly in parentheses after the quoted content rather than at the end of the response."
        elif self.language == 'ja':
            return "回答の中で参考文献は、回答の最後ではなく、引用内容の直後の括弧内に記載してください。"
        elif self.language == 'fr':
            return "Votre réponse doit contenir des références, et les références doivent être incluses directement entre parenthèses après le contenu cité plutôt qu'à la fin de la réponse."
        elif self.language == 'ms':
            return "Jawapan anda mesti mengandungi rujukan, dan rujukan itu patut dimasukkan secara langsung dalam tanda kurung selepas kandungan yang dipetikan dan bukan pada akhir jawapan."
        elif self.language == 'tgl':
            return "Sa halip na ilagay ang mga sanggunian sa dulo ng iyong sagot, ang mga sanggunian ay dapat na nakasulat nang direkta sa loob ng mga panaklong pagkatapos ng sipi."
        elif self.language == 'it':
            return "La tua risposta deve contenere riferimenti, e i riferimenti dovrebbero essere inclusi direttamente tra parentesi dopo il contenuto citato piuttosto che alla fine della risposta."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অবশ্যই উল্লেখ থাকতে হবে,উদ্ধৃতি চিহ্নের পরে রেফারেন্সগুলি সরাসরি বন্ধনীতে অন্তর্ভুক্ত করা উচিত,প্রতিক্রিয়া শেষে নয়।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mengandung referensi, dan referensi tersebut harus disertakan langsung dalam tanda kurung setelah konten yang dikutip, bukan di akhir tanggapan."
        # New languages
        elif self.language == 'qu':
            return "Willakuykunaqa qillqasqaykip chawpinpi churanayki, mana tukukuyninpichu, parentesis ukhupi."
        elif self.language == 'zu':
            return "Izindlela zokucaphuna zakho kufanele zifakwe ngqo kubakaki ngemuva kombhalo ocashunwe kuwo, kunokuba ekugcineni kwempendulo."
        elif self.language == 'mg':
            return "Ny loharano dia tokony ho ao anatin'ny fonon-teny avy hatrany aorian'ny votoatiny nalaina fa tsy any amin'ny faran'ny valinteny."
        elif self.language == 'sv':
            return "Referenser ska inkluderas direkt inom parentes efter det citerade innehållet, inte i slutet av svaret."
        elif self.language == 'ro':
            return "Referințele trebuie incluse direct în paranteze după conținutul citat, nu la sfârșitul răspunsului."
        elif self.language == 'tr':
            return "Kaynaklar, yanıtın sonunda değil, alıntılanan içeriğin hemen ardından parantez içinde yer almalıdır."
        elif self.language == 'ta':
            return "மேற்கோள்கள் பதிலின் முடிவில் அல்லாமல், மேற்கோள் காட்டப்பட்ட உள்ளடக்கத்திற்குப் பிறகு நேரடியாக அடைப்புக்குறிக்குள் இடம்பெற வேண்டும்."
        elif self.language == 'hy':
            return "Հղումները պետք է ներառվեն ուղղակիորեն փակագծերում՝ մեջբերված բովանդակությունից հետո, այլ ոչ թե պատասխանի վերջում։"
        elif self.language == 'ko':
            return "참고문헌은 답변 끝이 아닌, 인용된 내용 바로 뒤 괄호 안에 직접 포함되어야 합니다."
        elif self.language == 'te':
            return "మీ సూచనలు సమాధానం చివర కాకుండా, ఉల్లేఖించిన విషయం తర్వాత నేరుగా బ్రాకెట్లలో చేర్చాలి."
        elif self.language == 'ka':
            return "მითითებები უნდა იყოს მოთავსებული პირდაპირ ფრჩხილებში ციტირებული შინაარსის შემდეგ და არა პასუხის ბოლოს."
        elif self.language == 'ky':
            return "Шилтемелер жообуңуздун аягында эмес, цитата келтирилген мазмундун артында кашаанын ичинде түздөн-түз берилиши керек."
        elif self.language == 'pt':
            return "As referências devem ser incluídas diretamente entre parênteses após o conteúdo citado, não no final da resposta."
        elif self.language == 'hi':
            return "संदर्भों को उत्तर के अंत में नहीं, बल्कि उद्धृत सामग्री के तुरंत बाद कोष्ठक में सीधे शामिल किया जाना चाहिए।"

    def check_following(self, response):
        # Use regular expressions to match all citations in parentheses.
        inline_citations = re.findall(r'\([^()]+\)', response)

        # If there are no in-parentheses citations, return a score of 0.
        if not inline_citations:
            return 0.0

        # Check if the last line also contains a parenthetical citation.
        last_line = response.strip().split('\n')[-1]
        has_citation_in_last_line = bool(re.findall(r'\([^()]+\)', last_line))

        # If there is a citation in the last line, it indicates that it may be a list of references, and a score of 0 will be returned.
        if has_citation_in_last_line and len(last_line.strip()) < len(response.strip()):
            return 0.0

        return 1.0



class EmojiEnd(Instruction):
    def build_description(self, emoji_num, emoji):
        self.emoji_num = emoji_num
        self.emoji = emoji
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中必须以{emoji_num}个{emoji}来结尾。"
        elif self.language == 'en':
            return f"Your response must end with {emoji_num} \"{emoji}\"."
        elif self.language == 'ja':
            return f"回答の最後に{emoji}を{emoji_num}個付けてください。"
        elif self.language == 'fr':
            return f"Votre réponse doit se terminer par {emoji_num} {emoji}."
        elif self.language == 'ms':
            return f"Jawapan anda mesti diakhiri dengan {emoji_num} {emoji}."
        elif self.language == 'tgl':
            return f"Ang iyong sagot ay dapat magtapos sa {emoji_num} {emoji}."
        elif self.language == 'it':
            return f"La tua risposta deve terminare con {emoji_num} {emoji}."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া অবশ্যই {emoji_num} {emoji} দিয়ে শেষ করতে হবে।"
        elif self.language == 'id':
            return f"Tanggapan Anda harus diakhiri dengan {emoji_num} {emoji}."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykiqa {emoji_num} {emoji} nisqawan tukukunan."
        elif self.language == 'zu':
            return f"Impendulo yakho kufanele iphethe ngo-{emoji} ongu-{emoji_num}."
        elif self.language == 'mg':
            return f"Ny valinteninao dia tsy maintsy miafara amin'ny {emoji} {emoji_num}."
        elif self.language == 'sv':
            return f"Ditt svar måste avslutas med {emoji_num} {emoji}."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să se termine cu {emoji_num} {emoji}."
        elif self.language == 'tr':
            return f"Yanıtınız {emoji_num} adet {emoji} ile bitmelidir."
        elif self.language == 'ta':
            return f"உங்கள் பதில் {emoji_num} {emoji} உடன் முடிய வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը պետք է ավարտվի {emoji_num} հատ {emoji}-ով։"
        elif self.language == 'ko':
            return f"답변은 {emoji} {emoji_num}개로 끝나야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానం {emoji_num} {emoji}తో ముగియాలి."
        elif self.language == 'ka':
            return f"თქვენი პასუხი უნდა დასრულდეს {emoji_num} ცალი {emoji}-ით."
        elif self.language == 'ky':
            return f"Жообуңуз {emoji_num} даана {emoji} менен бүтүшү керек."
        elif self.language == 'pt':
            return f"Sua resposta deve terminar com {emoji_num} {emoji}."
        elif self.language == 'hi':
            return f"आपका उत्तर {emoji_num} {emoji} के साथ समाप्त होना चाहिए।"

    def check_following(self, response):
        response = response.strip()
        expected_ending = self.emoji * self.emoji_num

        # If there are no emojis at the end, return a score of 0 directly.
        if not response.endswith(self.emoji):
            return 0.0

        # Calculate the actual number of emojis at the end.
        actual_count = 0
        for i in range(len(response) - 1, -1, -1):
            if response[i] == self.emoji:
                actual_count += 1
            else:
                break

        # If there are no emojis at all, return a score of 0.
        if actual_count == 0:
            return 0.0

        # Calculate the difference from the required quantity
        diff = abs(self.emoji_num - actual_count)

        # Calculate the score using a formula
        score = max(0, 1 - 0.3 * (diff ** 2))

        return score



class EmojiFrequency(Instruction):
    relation_mapping = {
        # Original languages remain unchanged...
        'zh': {"at_least": "最少", "exactly": "正好", "at_most": "最多"},
        'en': {"at_least": "at least", "exactly": "exactly", "at_most": "at most"},
        'ja': {"at_least": "最低", "exactly": "ちょうど", "at_most": "最大"},
        'fr': {"at_least": "au moins", "exactly": "exactement", "at_most": "au plus"},
        'ms': {"at_least": "sekurang-kurangnya", "exactly": "tepat", "at_most": "paling banyak"},
        'tgl': {"at_least": "hindi bababa sa", "exactly": "eksaktong", "at_most": "hindi hihigit sa"},
        'it': {"at_least": "almeno", "exactly": "esattamente", "at_most": "al massimo"},
        'bn': {"at_least": "কমপক্ষে", "exactly": "ঠিক", "at_most": "সর্বাধিক"},
        'id': {"at_least": "setidaknya", "exactly": "tepat", "at_most": "paling banyak"},
        # New languages
        'qu': {"at_least": "aswan", "exactly": "chaylla", "at_most": "mana aswan"},
        'zu': {"at_least": "okungenani", "exactly": "ngqo", "at_most": "okungeqile"},
        'mg': {"at_least": "farafahakeliny", "exactly": "marina", "at_most": "farafahabetsany"},
        'sv': {"at_least": "minst", "exactly": "exakt", "at_most": "högst"},
        'ro': {"at_least": "cel puțin", "exactly": "exact", "at_most": "cel mult"},
        'tr': {"at_least": "en az", "exactly": "tam olarak", "at_most": "en fazla"},
        'ta': {"at_least": "குறைந்தது", "exactly": "சரியாக", "at_most": "அதிகபட்சம்"},
        'hy': {"at_least": "առնվազն", "exactly": "ճշգրիտ", "at_most": "առավելագույնը"},
        'ko': {"at_least": "최소", "exactly": "정확히", "at_most": "최대"},
        'te': {"at_least": "కనీసం", "exactly": "ఖచ్చితంగా", "at_most": "గరిష్టంగా"},
        'ka': {"at_least": "მინიმუმ", "exactly": "ზუსტად", "at_most": "მაქსიმუმ"},
        'ky': {"at_least": "жок дегенде", "exactly": "так", "at_most": "көбүнчө"},
        'pt': {"at_least": "pelo menos", "exactly": "exatamente", "at_most": "no máximo"},
        'hi': {"at_least": "कम से कम", "exactly": "ठीक", "at_most": "अधिक से अधिक"}
    }

    def build_description(self, relation, emoji_num, emoji):
        natural_relation = self.relation_mapping[self.language].get(relation, relation)
        self.emoji_num = emoji_num
        self.emoji = emoji
        self.relation = relation

        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中，emoji\"{emoji}\"应{natural_relation}出现{emoji_num}次。"
        elif self.language == 'en':
            return f"In your response, emoji \"{emoji}\" should appear {natural_relation} {emoji_num} times."
        elif self.language == 'ja':
            return f"回答の中で、絵文字{emoji}は{natural_relation}{emoji_num}回出現するようにしてください。"
        elif self.language == 'fr':
            return f"Dans votre réponse, l'emoji {emoji} doit apparaître {natural_relation} {emoji_num} fois."
        elif self.language == 'ms':
            return f"Dalam jawapan anda, emoji {emoji} mesti muncul {natural_relation} {emoji_num} kali."
        elif self.language == 'tgl':
            return f"Sa iyong sagot, dapat lumabas ang emoji {emoji} ng {natural_relation} {emoji_num} beses."
        elif self.language == 'it':
            return f"Nella tua risposta, l'emoji {emoji} dovrebbe apparire {natural_relation} {emoji_num} volte."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়াতে, ইমোজি {emoji} {natural_relation} {emoji_num} বার দেখা উচিত।"
        elif self.language == 'id':
            return f"Dalam tanggapan Anda, emoji {emoji} harus muncul {natural_relation} {emoji_num} kali."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi, {emoji} nisqa emoji {natural_relation} {emoji_num} kuti rikurinan."
        elif self.language == 'zu':
            return f"Empendulweni yakho, i-emoji {emoji} kufanele ivele {natural_relation} {emoji_num} izikhathi."
        elif self.language == 'mg':
            return f"Ao amin'ny valinteninao, ny emoji {emoji} dia tokony hiseho {natural_relation} {emoji_num}."
        elif self.language == 'sv':
            return f"I ditt svar ska emoji {emoji} visas {natural_relation} {emoji_num} gånger."
        elif self.language == 'ro':
            return f"În răspunsul tău, emoji-ul {emoji} trebuie să apară {natural_relation} de {emoji_num} ori."
        elif self.language == 'tr':
            return f"Yanıtınızda {emoji} emoji'si {natural_relation} {emoji_num} kez görünmelidir."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் {emoji} எமோஜி {natural_relation} {emoji_num} முறை தோன்ற வேண்டும்."
        elif self.language == 'hy':
            return f"Ձեր պատասխանում {emoji} էմոջին պետք է հայտնվի {natural_relation} {emoji_num} անգամ։"
        elif self.language == 'ko':
            return f"답변에서 {emoji} 이모지가 {natural_relation} {emoji_num}번 나타나야 합니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో {emoji} ఎమోజీ {natural_relation} {emoji_num} సార్లు కనిపించాలి."
        elif self.language == 'ka':
            return f"თქვენს პასუხში ემოჯი {emoji} უნდა გამოჩნდეს {natural_relation} {emoji_num}-ჯერ."
        elif self.language == 'ky':
            return f"Жообуңузда {emoji} эмодзи {natural_relation} {emoji_num} жолу көрүнүшү керек."
        elif self.language == 'pt':
            return f"Na sua resposta, o emoji {emoji} deve aparecer {natural_relation} {emoji_num} vezes."
        elif self.language == 'hi':
            return f"आपके उत्तर में {emoji} इमोजी {natural_relation} {emoji_num} बार आना चाहिए।"

    def check_following(self, response):
        count = response.count(self.emoji)  # Count the number of emojis in the reply

        # Calculate differences based on different relationships.
        if self.relation == "exactly":
            diff = abs(count - self.emoji_num)
        elif self.relation == "at_least":
            diff = max(0, self.emoji_num - count)
        elif self.relation == "at_most":
            diff = max(0, count - self.emoji_num)
        else:
            return 0.0

        # Calculate the score using a formula
        score = max(0, 1 - 0.1 * (diff ** 2))

        return score



class EmojiBanned(Instruction):
    def build_description(self, emoji):
        self.emoji = emoji
        # Original languages remain unchanged...
        if self.language == 'zh':
            return f"你的回复中应该出现emoji表情，但是不能出现\"{emoji}\"。"
        elif self.language == 'en':
            return f"Your response should include emoji expressions, but \"{emoji}\" must not appear."
        elif self.language == 'ja':
            return f"回答の中に絵文字を含める必要がありますが、{emoji}は使用しないでください。"
        elif self.language == 'fr':
            return f"Votre réponse doit inclure des expressions emoji, mais {emoji} ne doit pas apparaître."
        elif self.language == 'ms':
            return f"Dalam jawapan anda mesti termasuk ungkapan emoji, tetapi {emoji} tidak boleh muncul."
        elif self.language == 'tgl':
            return f"Ang iyong sagot ay dapat maglaman ng mga emoji, ngunit huwag isama ang {emoji}."
        elif self.language == 'it':
            return f"La tua risposta dovrebbe includere espressioni emoji, ma {emoji} non deve apparire."
        elif self.language == 'bn':
            return f"আপনার প্রতিক্রিয়া ইমোজি অন্তর্ভুক্ত করা উচিত, কিন্তু {emoji} প্রদর্শিত হবে না।"
        elif self.language == 'id':
            return f"Tanggapan Anda harus mencakup ekspresi emoji, tetapi {emoji} tidak boleh muncul."
        # New languages
        elif self.language == 'qu':
            return f"Kutichisqaykipi emojikuna kanan, ichaqa {emoji} ama rikurichunchu."
        elif self.language == 'zu':
            return f"Impendulo yakho kufanele ibe nama-emoji, kodwa i-{emoji} akufanele ivele."
        elif self.language == 'mg':
            return f"Ny valinteninao dia tokony hisy emoji, fa tsy tokony hisy ny {emoji}."
        elif self.language == 'sv':
            return f"Ditt svar ska innehålla emojis, men {emoji} får inte förekomma."
        elif self.language == 'ro':
            return f"Răspunsul tău trebuie să includă emoji-uri, dar {emoji} nu trebuie să apară."
        elif self.language == 'tr':
            return f"Yanıtınızda emoji kullanmalısınız ancak {emoji} kullanılmamalıdır."
        elif self.language == 'ta':
            return f"உங்கள் பதிலில் எமோஜிகள் இருக்க வேண்டும், ஆனால் {emoji} இருக்கக்கூடாது."
        elif self.language == 'hy':
            return f"Ձեր պատասխանը պետք է պարունակի էմոջիներ, բայց {emoji}-ը չպետք է հայտնվի։"
        elif self.language == 'ko':
            return f"답변에 이모지를 포함해야 하지만 {emoji}는 사용하면 안 됩니다."
        elif self.language == 'te':
            return f"మీ సమాధానంలో ఎమోజీలు ఉండాలి, కానీ {emoji} ఉండకూడదు."
        elif self.language == 'ka':
            return f"თქვენს პასუხში უნდა იყოს ემოჯები, მაგრამ {emoji} არ უნდა გამოჩნდეს."
        elif self.language == 'ky':
            return f"Жообуңузда эмодзи болушу керек, бирок {emoji} колдонулбашы керек."
        elif self.language == 'pt':
            return f"Sua resposta deve incluir emojis, mas {emoji} não deve aparecer."
        elif self.language == 'hi':
            return f"आपके उत्तर में इमोजी होना चाहिए, लेकिन {emoji} नहीं होना चाहिए।"

    def check_following(self, response):
        # Check if any emoji is included.
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)

        contains_emoji = bool(emoji_pattern.search(response))
        does_not_contain_banned_emoji = self.emoji not in response

        # Calculate the score
        emoji_score = 0.1 if contains_emoji else 0.0
        banned_score = 0.9 if does_not_contain_banned_emoji else 0.0

        return emoji_score + banned_score



# style
class FormalLanguageStyle(Instruction):
    def build_description(self):
        # Original languages remain unchanged...
        if self.language == 'zh':
            return "你的回复必须使用正式语言风格，避免使用口语或俚语。"
        elif self.language == 'en':
            return "Your response must use formal language; colloquialisms and slang are prohibited."
        elif self.language == 'ja':
            return "回答は必ず丁寧な正式な言葉遣いを使用し、口語表現やスラングは避けてください。"
        elif self.language == 'fr':
            return "Votre réponse doit utiliser un langage formel ; les colloquialismes et le langage familier sont interdits."
        elif self.language == 'ms':
            return "Jawapan anda mesti menggunakan bahasa formal; istilah colokial dan slang dilarang."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat gumamit ng pormal na estilo ng wika, iwasan ang paggamit ng kolokyalismo o balbal na mga salita."
        elif self.language == 'it':
            return "La tua risposta deve utilizzare un linguaggio formale; sono vietati colloquialismi e slang."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অবশ্যই একটি আনুষ্ঠানিক ভাষা শৈলী ব্যবহার করতে হবে এবং কথোপকথন বা অপবাদ এড়াতে হবে।"
        elif self.language == 'id':
            return "Tanggapan Anda harus menggunakan bahasa formal; bahasa sehari-hari dan slang dilarang."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi allin qillqasqa simita llamk'anayki, ama rimay simita nitaq waqlisqa simita churankichu."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele isebenzise ulimi olusemthethweni; izingxoxo zansuku zonke kanye namagama asetshenziswa emphakathini awamukelekile."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy mampiasa fiteny ôfisialy; ny fiteny andavanandro sy ny teny fampiasa eny an-dalambe dia voarara."
        elif self.language == 'sv':
            return "Ditt svar måste använda formellt språk; vardagligt språk och slang är förbjudet."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să folosească un limbaj formal; expresiile colocviale și argoul sunt interzise."
        elif self.language == 'tr':
            return "Yanıtınızda resmi dil kullanmalısınız; gündelik konuşma dili ve argo kullanımı yasaktır."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் முறையான மொழி நடையைப் பயன்படுத்த வேண்டும்; பேச்சு வழக்கு மற்றும் வட்டார வழக்கு சொற்கள் தடை செய்யப்பட்டுள்ளன."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է օգտագործի պաշտոնական լեզու. խոսակցական լեզուն և ժարգոնը արգելված են։"
        elif self.language == 'ko':
            return "답변에는 반드시 격식체를 사용해야 하며, 구어체와 속어는 금지됩니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో అధికారిక భాషను ఉపయోగించాలి; వాడుక భాష మరియు జాతీయాలు నిషేధించబడ్డాయి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა იყენებდეს ოფიციალურ ენას; სასაუბრო ენა და ჟარგონი აკრძალულია."
        elif self.language == 'ky':
            return "Жообуңузда расмий тилди колдонушуңуз керек; күнүмдүк сүйлөшүү тили жана жаргон колдонууга тыюу салынат."
        elif self.language == 'pt':
            return "Sua resposta deve usar linguagem formal; coloquialismos e gírias são proibidos."
        elif self.language == 'hi':
            return "आपके उत्तर में औपचारिक भाषा का प्रयोग होना चाहिए; बोलचाल की भाषा और शब्दजाल का प्रयोग निषिद्ध है।"


class InformalLanguageStyle(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复必须使用非正式语言风格，使用口语化表达。"
        elif self.language == 'en':
            return "Your response must use informal language and colloquial expressions."
        elif self.language == 'ja':
            return "回答はカジュアルな言葉遣いで、くだけた表現を使ってください。"
        elif self.language == 'fr':
            return "Votre réponse doit utiliser un langage informel et des expressions familières."
        elif self.language == 'ms':
            return "Jawapan anda mesti menggunakan bahasa informal dan ungkapan colokial."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat gumamit ng impormal na estilo ng wika, gumamit ng mga kolokyal na ekspresyon."
        elif self.language == 'it':
            return "La tua risposta deve utilizzare un linguaggio informale e espressioni colloquiali."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অবশ্যই অনানুষ্ঠানিক ভাষা ব্যবহার করতে হবে এবং কথোপকথন ব্যবহার করতে হবে।"
        elif self.language == 'id':
            return "Tanggapan Anda harus menggunakan bahasa informal dan ekspresi kolokial."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa rimay simipi, sapa p'unchaw rimay hinachu kanan."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele isebenzise ulimi olungekho semthethweni kanye namagama asetshenziswa nsuku zonke."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy mampiasa fiteny andavanandro sy fomba fiteny mahazatra."
        elif self.language == 'sv':
            return "Ditt svar måste använda vardagligt språk och informella uttryck."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să folosească un limbaj informal și expresii colocviale."
        elif self.language == 'tr':
            return "Yanıtınızda günlük konuşma dili ve gündelik ifadeler kullanmalısınız."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் முறைசாரா மொழி மற்றும் பேச்சு வழக்கு சொற்களைப் பயன்படுத்த வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է օգտագործի ոչ պաշտոնական լեզու և խոսակցական արտահայտություններ։"
        elif self.language == 'ko':
            return "답변에는 반드시 구어체와 일상적인 표현을 사용해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో అనౌపచారిక భాష మరియు వాడుక భాష పదాలను ఉపయోగించాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა იყენებდეს არაფორმალურ ენას და სასაუბრო გამოთქმებს."
        elif self.language == 'ky':
            return "Жообуңузда күнүмдүк сүйлөшүү тилин жана кадимки сөздөрдү колдонушуңуз керек."
        elif self.language == 'pt':
            return "Sua resposta deve usar linguagem informal e expressões coloquiais."
        elif self.language == 'hi':
            return "आपके उत्तर में अनौपचारिक भाषा और बोलचाल के शब्दों का प्रयोग होना चाहिए।"



class ProfessionalTerminology(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中应包含至少3个与某个特定学科或领域相关的专业术语。"
        elif self.language == 'en':
            return "Your response should include at least three technical terms related to a specific discipline or field."
        elif self.language == 'ja':
            return "回答の中に特定の学問分野や専門領域に関する専門用語を少なくとも3つ含めてください。"
        elif self.language == 'fr':
            return "Votre réponse doit inclure au moins trois termes techniques liés à une discipline ou un domaine spécifique."
        elif self.language == 'ms':
            return "Jawapan anda mesti mengandungi sekurang-kurangnya tiga terma teknikal yang berkaitan dengan satu disiplin atau bidang tertentu."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat maglaman ng hindi bababa sa tatlong teknikal na terminong may kaugnayan sa isang partikular na larangan o disiplina."
        elif self.language == 'it':
            return "La tua risposta dovrebbe includere almeno tre termini tecnici relativi a una disciplina o campo specifico."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া একটি নির্দিষ্ট শৃঙ্খলা বা ক্ষেত্রের সাথে সম্পর্কিত কমপক্ষে তিনটি প্রযুক্তিগত পদ অন্তর্ভুক্ত করা উচিত।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mencakup setidaknya tiga istilah teknis yang terkait dengan disiplin atau bidang tertentu."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi kimsa yachay simikuna kanan huk allin yachay kamaypi."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibe namagama obuchwepheshe amathathu okungenani ahlobene nomkhakha othile."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy ahitana farafahakeliny teny teknika telo mikasika taranja na sehatra manokana."
        elif self.language == 'sv':
            return "Ditt svar ska innehålla minst tre tekniska termer relaterade till en specifik disciplin eller ett specifikt område."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să includă cel puțin trei termeni tehnici legați de o disciplină sau un domeniu specific."
        elif self.language == 'tr':
            return "Yanıtınız belirli bir disiplin veya alana ilişkin en az üç teknik terim içermelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் குறிப்பிட்ட துறை அல்லது பிரிவுடன் தொடர்புடைய குறைந்தது மூன்று தொழில்நுட்பச் சொற்கள் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է ներառի առնվազն երեք տեխնիկական տերմին՝ կապված որոշակի գիտակարգի կամ ոլորտի հետ։"
        elif self.language == 'ko':
            return "답변에는 특정 분야나 영역과 관련된 전문 용어를 최소 3개 포함해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో నిర్దిష్ట విభాగం లేదా రంగానికి సంబంధించిన కనీసం మూడు సాంకేతిక పదాలు ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა შეიცავდეს მინიმუმ სამ ტექნიკურ ტერმინს, რომლებიც დაკავშირებულია კონკრეტულ დისციპლინასთან ან სფეროსთან."
        elif self.language == 'ky':
            return "Жообуңузда белгилүү бир тармак же багытка байланыштуу жок дегенде үч техникалык термин болушу керек."
        elif self.language == 'pt':
            return "Sua resposta deve incluir pelo menos três termos técnicos relacionados a uma disciplina ou campo específico."
        elif self.language == 'hi':
            return "आपके उत्तर में किसी विशिष्ट विषय या क्षेत्र से संबंधित कम से कम तीन तकनीकी शब्द शामिल होने चाहिए।"



class PoeticStyle(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复必须带有诗歌般的语言风格，用到押韵的技巧。"
        elif self.language == 'en':
            return "Your response must employ a poetic style with rhyming techniques."
        elif self.language == 'ja':
            return "回答は韻を踏むような詩的な言葉遣いで表現してください。"
        elif self.language == 'fr':
            return "Votre réponse doit employer un style poétique avec des techniques de rime."
        elif self.language == 'ms':
            return "Jawapan anda mesti menggunakan gaya puisi dengan teknik irama."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat gumamit ng makatang estilo ng pagsulat, gumamit ng mga teknik ng pagtutugma ng mga salita."
        elif self.language == 'it':
            return "La tua risposta deve adottare uno stile poetico con tecniche di rima."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অবশ্যই ছন্দের কৌশল সহ একটি কাব্যিক শৈলী নিয়োগ করবে।"
        elif self.language == 'id':
            return "Tanggapan Anda harus menggunakan gaya puitis dengan teknik rima."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa harawikuna hina kanan, taki simikunata churaspa."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele isebenzise isitayela senkondlo kanye namasu okuqondanisa amazwi."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy mampiasa fomba fiteny ara-poety miaraka amin'ny teknika firindran-teny."
        elif self.language == 'sv':
            return "Ditt svar måste använda en poetisk stil med rimtekniker."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să folosească un stil poetic cu tehnici de rimare."
        elif self.language == 'tr':
            return "Yanıtınız kafiye teknikleri kullanan şiirsel bir üslupla yazılmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதில் கவிதை பாணியில், எதுகை மோனைத் தொடைகளுடன் அமைய வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է օգտագործի բանաստեղծական ոճ՝ հանգավորման տեխնիկաներով։"
        elif self.language == 'ko':
            return "답변은 운율 기법을 사용한 시적인 문체로 작성되어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం ప్రాస పద్ధతులతో కూడిన కవితా శైలిని ఉపయోగించాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა იყენებდეს პოეტურ სტილს რითმული ტექნიკებით."
        elif self.language == 'ky':
            return "Жообуңуз уйкаштык ыкмаларын колдонгон ырдай стилде болушу керек."
        elif self.language == 'pt':
            return "Sua resposta deve empregar um estilo poético com técnicas de rima."
        elif self.language == 'hi':
            return "आपके उत्तर में काव्यात्मक शैली का प्रयोग होना चाहिए, जिसमें तुकबंदी की तकनीकें हों।"



class FormalLetterFormat(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复必须用正式信件的格式撰写。"
        elif self.language == 'en':
            return "Your response must be written in a formal letter format."
        elif self.language == 'ja':
            return "回答は正式な手紙の形式で書いてください。"
        elif self.language == 'fr':
            return "Votre réponse doit être rédigée dans un format de lettre formelle."
        elif self.language == 'ms':
            return "Jawapan anda mesti ditulis dalam format surat formal."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat nakasulat sa pormal na pormat ng liham."
        elif self.language == 'it':
            return "La tua risposta deve essere scritta in formato lettera formale."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া একটি আনুষ্ঠানিক চিঠি বিন্যাসে লিখতে হবে।"
        elif self.language == 'id':
            return "Tanggapan Anda harus ditulis dalam format surat resmi."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa allin qillqa kartahina kanan."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibhalwe ngendlela yencwadi esemthethweni."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy atao amin'ny endrika taratasy ôfisialy."
        elif self.language == 'sv':
            return "Ditt svar måste skrivas i ett formellt brevformat."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să fie scris în format de scrisoare formală."
        elif self.language == 'tr':
            return "Yanıtınız resmi mektup formatında yazılmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதில் முறையான கடித வடிவத்தில் எழுதப்பட வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է գրված լինի պաշտոնական նամակի ձևաչափով։"
        elif self.language == 'ko':
            return "답변은 반드시 공식 편지 형식으로 작성되어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం లాంఛన పత్ర ఆకృతిలో రాయబడి ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა დაიწეროს ოფიციალური წერილის ფორმატში."
        elif self.language == 'ky':
            return "Жообуңуз расмий кат форматында жазылышы керек."
        elif self.language == 'pt':
            return "Sua resposta deve ser escrita em formato de carta formal."
        elif self.language == 'hi':
            return "आपका उत्तर औपचारिक पत्र के प्रारूप में लिखा होना चाहिए।"



# tone
class HumorousTone(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的主基调必须是幽默或轻松的情感表达。"
        elif self.language == 'en':
            return "The tone of your response must be humorous or light-hearted."
        elif self.language == 'ja':
            return "回答は必ずユーモアのある明るい調子で表現してください。"
        elif self.language == 'fr':
            return "Le ton de votre réponse doit être humoristique ou léger."
        elif self.language == 'ms':
            return "Ton jawapan anda mesti lucu atau tenang hati."
        elif self.language == 'tgl':
            return "Ang pangunahing tono ng iyong sagot ay dapat nakakatawa o magaan sa damdamin."
        elif self.language == 'it':
            return "Il tono della tua risposta deve essere umoristico o leggero."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ার স্বর অবশ্যই হাস্যকর বা হালকা হতে হবে।"
        elif self.language == 'id':
            return "Nada tanggapan Anda harus humoris atau ringan."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa asichikuq utaq kusisqa rimaywan kanan."
        elif self.language == 'zu':
            return "Indlela yempendulo yakho kufanele ibe nehlaya noma ibe lula."
        elif self.language == 'mg':
            return "Ny fomba famalianao dia tsy maintsy mampihomehy na maivana."
        elif self.language == 'sv':
            return "Tonen i ditt svar måste vara humoristisk eller lättsam."
        elif self.language == 'ro':
            return "Tonul răspunsului tău trebuie să fie umoristic sau relaxat."
        elif self.language == 'tr':
            return "Yanıtınızın tonu mizahi veya eğlenceli olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் தொனி நகைச்சுவையாக அல்லது இலகுவாக இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի տոնը պետք է լինի հումորային կամ թեթև։"
        elif self.language == 'ko':
            return "답변의 어조는 반드시 유머러스하거나 가벼운 느낌이어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం యొక్క ధోరణి హాస్యంగా లేదా తేలికగా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ტონი უნდა იყოს იუმორისტული ან მსუბუქი."
        elif self.language == 'ky':
            return "Жообуңуздун тону тамашалуу же жеңил болушу керек."
        elif self.language == 'pt':
            return "O tom da sua resposta deve ser humorístico ou descontraído."
        elif self.language == 'hi':
            return "आपके उत्तर का स्वर हास्यपूर्ण या हल्का-फुल्का होना चाहिए।"



class PositiveTone(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的主基调必须是积极或乐观的情感表达。"
        elif self.language == 'en':
            return "The tone of your response must be positive or optimistic."
        elif self.language == 'ja':
            return "回答は必ず前向きで楽観的な調子で表現してください。"
        elif self.language == 'fr':
            return "Le ton de votre réponse doit être positif ou optimiste."
        elif self.language == 'ms':
            return "Ton jawapan anda mesti positif atau optimis."
        elif self.language == 'tgl':
            return "Ang pangunahing tono ng iyong sagot ay dapat positibo o puno ng pag-asa."
        elif self.language == 'it':
            return "Il tono della tua risposta deve essere positivo o ottimista."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ার স্বর অবশ্যই ইতিবাচক বা আশাবাদী হতে হবে।"
        elif self.language == 'id':
            return "Nada tanggapan Anda harus positif atau optimis."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa kusikuywan utaq allin qawaywan kanan."
        elif self.language == 'zu':
            return "Indlela yempendulo yakho kufanele ibe nethemba noma igcwale ithemba."
        elif self.language == 'mg':
            return "Ny fomba famalianao dia tsy maintsy ho tsara na feno fanantenana."
        elif self.language == 'sv':
            return "Tonen i ditt svar måste vara positiv eller optimistisk."
        elif self.language == 'ro':
            return "Tonul răspunsului tău trebuie să fie pozitiv sau optimist."
        elif self.language == 'tr':
            return "Yanıtınızın tonu olumlu veya iyimser olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் தொனி நேர்மறையாக அல்லது நம்பிக்கையுடன் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի տոնը պետք է լինի դրական կամ լավատեսական։"
        elif self.language == 'ko':
            return "답변의 어조는 반드시 긍정적이거나 낙관적이어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం యొక్క ధోరణి సానుకూలంగా లేదా ఆశావాదంగా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ტონი უნდა იყოს პოზიტიური ან ოპტიმისტური."
        elif self.language == 'ky':
            return "Жообуңуздун тону оң же ишенимдүү болушу керек."
        elif self.language == 'pt':
            return "O tom da sua resposta deve ser positivo ou otimista."
        elif self.language == 'hi':
            return "आपके उत्तर का स्वर सकारात्मक या आशावादी होना चाहिए।"



class NegativeTone(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的主基调必须是消极或悲观的情感表达。"
        elif self.language == 'en':
            return "The tone of your response must be negative or pessimistic."
        elif self.language == 'ja':
            return "回答は必ず否定的または悲観的な調子で表現してください。"
        elif self.language == 'fr':
            return "Le ton de votre réponse doit être négatif ou pessimiste."
        elif self.language == 'ms':
            return "Ton jawapan anda mesti negatif atau pesimis."
        elif self.language == 'tgl':
            return "Ang pangunahing tono ng iyong sagot ay dapat negatibo o walang pag-asa."
        elif self.language == 'it':
            return "Il tono della tua risposta deve essere negativo o pessimista."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ার স্বন অবশ্যই নেতিবাচক বা হতাশাবাদী হতে হবে।"
        elif self.language == 'id':
            return "Nada tanggapan Anda harus negatif atau pesimis."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa llakikuywan utaq mana allin qawaywan kanan."
        elif self.language == 'zu':
            return "Indlela yempendulo yakho kufanele ibe nomoya ophansi noma ingenathemba."
        elif self.language == 'mg':
            return "Ny fomba famalianao dia tsy maintsy ho ratsy na tsy feno fanantenana."
        elif self.language == 'sv':
            return "Tonen i ditt svar måste vara negativ eller pessimistisk."
        elif self.language == 'ro':
            return "Tonul răspunsului tău trebuie să fie negativ sau pesimist."
        elif self.language == 'tr':
            return "Yanıtınızın tonu olumsuz veya karamsar olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் தொனி எதிர்மறையாக அல்லது நம்பிக்கையற்றதாக இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի տոնը պետք է լինի բացասական կամ հոռետեսական։"
        elif self.language == 'ko':
            return "답변의 어조는 반드시 부정적이거나 비관적이어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం యొక్క ధోరణి ప్రతికూలంగా లేదా నిరాశావాదంగా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ტონი უნდა იყოს უარყოფითი ან პესიმისტური."
        elif self.language == 'ky':
            return "Жообуңуздун тону терс же үмүтсүз болушу керек."
        elif self.language == 'pt':
            return "O tom da sua resposta deve ser negativo ou pessimista."
        elif self.language == 'hi':
            return "आपके उत्तर का स्वर नकारात्मक या निराशावादी होना चाहिए।"



class SarcasticTone(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的主基调必须是讽刺或挖苦的情感表达。"
        elif self.language == 'en':
            return "The tone of your response must be sarcastic or ironic."
        elif self.language == 'ja':
            return "回答は必ず皮肉やあてこすりを含む調子で表現してください。"
        elif self.language == 'fr':
            return "Le ton de votre réponse doit être sarcastique ou ironique."
        elif self.language == 'ms':
            return "Ton jawapan anda mesti sarkastik atau ironis."
        elif self.language == 'tgl':
            return "Ang pangunahing tono ng iyong sagot ay dapat mapang-uyam o mapanuya."
        elif self.language == 'it':
            return "Il tono della tua risposta deve essere sarcastico o ironico."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়ার স্বর অবশ্যই ব্যঙ্গাত্মক বা বিদ্রূপাত্মক হতে হবে।"
        elif self.language == 'id':
            return "Nada tanggapan Anda harus sarkastik atau ironis."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa k'amillayta utaq qhawapayayta rimayniyuq kanan."
        elif self.language == 'zu':
            return "Indlela yempendulo yakho kufanele ibe nokugxeka noma ukuhleka usulu."
        elif self.language == 'mg':
            return "Ny fomba famalianao dia tsy maintsy misy fanarabiana na fieritreretana."
        elif self.language == 'sv':
            return "Tonen i ditt svar måste vara sarkastisk eller ironisk."
        elif self.language == 'ro':
            return "Tonul răspunsului tău trebuie să fie sarcastic sau ironic."
        elif self.language == 'tr':
            return "Yanıtınızın tonu alaycı veya ironik olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் தொனி கேலி அல்லது நையாண்டி நிறைந்ததாக இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի տոնը պետք է լինի հեգնական կամ երգիծական։"
        elif self.language == 'ko':
            return "답변의 어조는 반드시 비꼬는 듯한 또는 풍자적이어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం యొక్క ధోరణి వ్యంగ్యంగా లేదా వ్యాజస్తుతిగా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ტონი უნდა იყოს სარკასტული ან ირონიული."
        elif self.language == 'ky':
            return "Жообуңуздун тону шылдыңдуу же кыжырткан болушу керек."
        elif self.language == 'pt':
            return "O tom da sua resposta deve ser sarcástico ou irônico."
        elif self.language == 'hi':
            return "आपके उत्तर का स्वर व्यंग्यात्मक या कटाक्षपूर्ण होना चाहिए।"



class AngryTone(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复的主基调必须是愤怒或不满的情感表达。"
        elif self.language == 'en':
            return "The tone of your response must be angry or dissatisfied."
        elif self.language == 'ja':
            return "回答は必ず怒りや不満を表す調子で表現してください。"
        elif self.language == 'fr':
            return "Le ton de votre réponse doit être en colère ou insatisfait."
        elif self.language == 'ms':
            return "Ton jawapan anda mesti marah atau tidak puas hati."
        elif self.language == 'tgl':
            return "Ang pangunahing tono ng iyong sagot ay dapat galit o hindi masaya."
        elif self.language == 'it':
            return "Il tono della tua risposta deve essere arrabbiato o insoddisfatto."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া প্রভাবশালী টোন অবশ্যই রাগ বা অসন্তুষ্টি হতে হবে।"
        elif self.language == 'id':
            return "Nada tanggapan Anda harus marah atau tidak puas."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykiqa phiñakusqa utaq mana kusisqa rimayniyuq kanan."
        elif self.language == 'zu':
            return "Indlela yempendulo yakho kufanele ibe nentukuthelo noma ukungagculiseki."
        elif self.language == 'mg':
            return "Ny fomba famalianao dia tsy maintsy ho feno hatezerana na tsy fahafaham-po."
        elif self.language == 'sv':
            return "Tonen i ditt svar måste vara arg eller missnöjd."
        elif self.language == 'ro':
            return "Tonul răspunsului tău trebuie să fie furios sau nemulțumit."
        elif self.language == 'tr':
            return "Yanıtınızın tonu kızgın veya memnuniyetsiz olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலின் தொனி கோபமாக அல்லது அதிருப்தியாக இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանի տոնը պետք է լինի զայրացած կամ դժգոհ։"
        elif self.language == 'ko':
            return "답변의 어조는 반드시 화난 듯하거나 불만이 가득한 것이어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానం యొక్క ధోరణి కోపంగా లేదా అసంతృప్తిగా ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხის ტონი უნდა იყოს გაბრაზებული ან უკმაყოფილო."
        elif self.language == 'ky':
            return "Жообуңуздун тону ачуулуу же нааразы болушу керек."
        elif self.language == 'pt':
            return "O tom da sua resposta deve ser raivoso ou insatisfeito."
        elif self.language == 'hi':
            return "आपके उत्तर का स्वर क्रोधित या असंतुष्ट होना चाहिए।"





# content
class IncludeJokes(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中必须至少包含3个笑话。"
        elif self.language == 'en':
            return "Your response must include at least three jokes."
        elif self.language == 'ja':
            return "回答の中に少なくとも3つの冗談を含めてください。"
        elif self.language == 'fr':
            return "Votre réponse doit inclure au moins trois blagues."
        elif self.language == 'ms':
            return "Jawapan anda mesti mengandungi sekurang-kurangnya tiga perkara lucu."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat maglaman ng hindi bababa sa 3 biro."
        elif self.language == 'it':
            return "La tua risposta deve includere almeno tre battute."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অন্তত তিনটি কৌতুক অন্তর্ভুক্ত করা আবশ্যক।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mencakup setidaknya tiga lelucon."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi kimsa asichikuy simikunata churanayki."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibe nokungenani izindaba ezintathu ezihlekisayo."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy ahitana farafahakeliny vazivazy telo."
        elif self.language == 'sv':
            return "Ditt svar måste innehålla minst tre skämt."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să includă cel puțin trei glume."
        elif self.language == 'tr':
            return "Yanıtınız en az üç fıkra içermelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் குறைந்தது மூன்று நகைச்சுவைகள் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է ներառի առնվազն երեք կատակ։"
        elif self.language == 'ko':
            return "답변에는 최소 3개의 농담이 포함되어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో కనీసం మూడు జోకులు ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა შეიცავდეს მინიმუმ სამ ხუმრობას."
        elif self.language == 'ky':
            return "Жообуңузда жок дегенде үч тамаша болушу керек."
        elif self.language == 'pt':
            return "Sua resposta deve incluir pelo menos três piadas."
        elif self.language == 'hi':
            return "आपके उत्तर में कम से कम तीन चुटकुले शामिल होने चाहिए।"


class IncludeQuotes(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中必须至少引用3个名人名言。"
        elif self.language == 'en':
            return "Your response must quote at least three famous sayings."
        elif self.language == 'ja':
            return "回答の中に少なくとも3つの名言を引用してください。"
        elif self.language == 'fr':
            return "Votre réponse doit citer au moins trois dictons célèbres."
        elif self.language == 'ms':
            return "Jawapan anda mesti mengutip sekurang-kurangnya tiga pepatah yang terkenal."
        elif self.language == 'tgl':
            return "Sa iyong sagot ay dapat magbanggit ng hindi bababa sa 3 tanyag na kasabihan."
        elif self.language == 'it':
            return "La tua risposta deve citare almeno tre detti famosi."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অন্তত তিনটি বিখ্যাত উক্তি উদ্ধৃত করা আবশ্যক।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mengutip setidaknya tiga pepatah terkenal."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi kimsa riqsisqa runakunaq rimasqanta churanayki."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele icaphune okungenani izisho ezintathu ezidumile."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy mitanisa farafahakeliny teny malaza telo."
        elif self.language == 'sv':
            return "Ditt svar måste citera minst tre berömda talesätt."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să citeze cel puțin trei zicători celebre."
        elif self.language == 'tr':
            return "Yanıtınız en az üç ünlü söz içermelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் குறைந்தது மூன்று புகழ்பெற்ற பொன்மொழிகளை மேற்கோள் காட்ட வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է մեջբերի առնվազն երեք հայտնի ասույթներ։"
        elif self.language == 'ko':
            return "답변에는 최소 3개의 유명한 명언을 인용해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో కనీసం మూడు ప్రసిద్ధ సూక్తులను ఉటంకించాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა შეიცავდეს მინიმუმ სამ ცნობილ გამონათქვამს."
        elif self.language == 'ky':
            return "Жообуңузда жок дегенде үч атактуу макал-лакапты келтириш керек."
        elif self.language == 'pt':
            return "Sua resposta deve citar pelo menos três ditados famosos."
        elif self.language == 'hi':
            return "आपके उत्तर में कम से कम तीन प्रसिद्ध कहावतों का उल्लेख होना चाहिए।"


class MentionFamousPerson(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中必须提到一个与主题相关的著名人物，并简要介绍其成就。"
        elif self.language == 'en':
            return "Your response must mention a relevant prominent figure and briefly describe their achievements."
        elif self.language == 'ja':
            return "回答の中で主題に関連する著名人物を取り上げ、その功績を簡潔に説明してください。"
        elif self.language == 'fr':
            return "Votre réponse doit mentionner une personnalité pertinente et décrire brièvement ses réalisations."
        elif self.language == 'ms':
            return "Jawapan anda mesti menyebut seorang ahli penting yang berkaitan dan terperinci menggambarkan pencapaian mereka."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat magbanggit ng isang kilalang tao na may kaugnayan sa paksa at ipaliwanag ang kanyang mga nagawa."
        elif self.language == 'it':
            return "La tua risposta deve menzionare una figura prominente rilevante e descrivere brevemente i suoi successi."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া একটি প্রাসঙ্গিক বিশিষ্ট ব্যক্তিত্ব উল্লেখ এবং সংক্ষিপ্তভাবে তাদের কৃতিত্ব বর্ণনা করা আবশ্যক।"
        elif self.language == 'id':
            return "Tanggapan Anda harus menyebutkan tokoh terkenal yang relevan dan secara singkat menggambarkan pencapaiannya."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi huk riqsisqa runata rimanki, chaymanta pisi simipi rurasqankunata willanayki."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibale umuntu odumile ofanelekile futhi ichaze kafushane izinto azizuzile."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy miresaka olona malaza mifandraika amin'ny lohahevitra ary manazava fohy ny zava-bitany."
        elif self.language == 'sv':
            return "Ditt svar måste nämna en relevant framstående person och kortfattat beskriva deras prestationer."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să menționeze o personalitate relevantă și să descrie pe scurt realizările sale."
        elif self.language == 'tr':
            return "Yanıtınız konuyla ilgili önemli bir kişiden bahsetmeli ve başarılarını kısaca anlatmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் தொடர்புடைய புகழ்பெற்ற நபர் ஒருவரைக் குறிப்பிட்டு, அவரது சாதனைகளை சுருக்கமாக விவரிக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է նշի համապատասխան նշանավոր անձի և համառոտ նկարագրի նրա ձեռքբերումները։"
        elif self.language == 'ko':
            return "답변에는 주제와 관련된 저명한 인물을 언급하고 그들의 업적을 간단히 설명해야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో సంబంధిత ప్రముఖ వ్యక్తిని ప్రస్తావించి, వారి సాధనలను సంక్షిప్తంగా వివరించాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა ახსენებდეს შესაბამის გამოჩენილ პიროვნებას და მოკლედ აღწერდეს მის მიღწევებს."
        elif self.language == 'ky':
            return "Жообуңузда тема боюнча белгилүү инсанды эскерип, анын жетишкендиктерин кыскача сүрөттөп бериш керек."
        elif self.language == 'pt':
            return "Sua resposta deve mencionar uma figura proeminente relevante e descrever brevemente suas realizações."
        elif self.language == 'hi':
            return "आपके उत्तर में विषय से संबंधित एक प्रमुख व्यक्ति का उल्लेख करना और उनकी उपलब्धियों का संक्षिप्त वर्णन करना आवश्यक है।"




# language_switch
class ThreeLanguages(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复中应当至少包含三种不同的语言。"
        elif self.language == 'en':
            return "Your response should contain at least three different languages."
        elif self.language == 'ja':
            return "回答の中に少なくとも3つの異なる言語を含めてください。"
        elif self.language == 'fr':
            return "Votre réponse doit contenir au moins trois langues différentes."
        elif self.language == 'ms':
            return "Jawapan anda hendaklah mengandungi sekurang-kurangnya tiga bahasa yang berbeza."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat gumamit ng hindi bababa sa tatlong magkakaibang wika."
        elif self.language == 'it':
            return "La tua risposta dovrebbe contenere almeno tre lingue diverse."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া অন্তত তিনটি ভিন্ন ভাষা থাকা উচিত।"
        elif self.language == 'id':
            return "Tanggapan Anda harus mengandung setidaknya tiga bahasa yang berbeda."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykipi kimsa huk simikunapi rimana kanan."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele ibe nezilimi ezintathu ezihlukene okungenani."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy ahitana farafahakeliny fiteny telo samihafa."
        elif self.language == 'sv':
            return "Ditt svar ska innehålla minst tre olika språk."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie să conțină cel puțin trei limbi diferite."
        elif self.language == 'tr':
            return "Yanıtınız en az üç farklı dil içermelidir."
        elif self.language == 'ta':
            return "உங்கள் பதிலில் குறைந்தது மூன்று வெவ்வேறு மொழிகள் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է պարունակի առնվազն երեք տարբեր լեզուներ։"
        elif self.language == 'ko':
            return "답변에는 최소 3개의 서로 다른 언어가 포함되어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానంలో కనీసం మూడు వేర్వేరు భాషలు ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა შეიცავდეს მინიმუმ სამ განსხვავებულ ენას."
        elif self.language == 'ky':
            return "Жообуңузда жок дегенде үч башка тил болушу керек."
        elif self.language == 'pt':
            return "Sua resposta deve conter pelo menos três idiomas diferentes."
        elif self.language == 'hi':
            return "आपके उत्तर में कम से कम तीन अलग-अलग भाषाएँ शामिल होनी चाहिए।"



class RepeatInDifferentLanguage(Instruction):
    def build_description(self):
        # Original 9 languages remain unchanged...
        if self.language == 'zh':
            return "你的回复应当重复一次，并且第二次使用不同的语言。"
        elif self.language == 'en':
            return "Your response should be repeated once and the second one should be in different language."
        elif self.language == 'ja':
            return "回答を一度繰り返し、二回目は異なる言語で表現してください。"
        elif self.language == 'fr':
            return "Votre réponse doit être répétée une fois et la deuxième fois doit être dans une langue différente."
        elif self.language == 'ms':
            return "Jawapan anda hendaklah diulang sekali dan yang kedua perlu dalam bahasa yang berbeza."
        elif self.language == 'tgl':
            return "Ang iyong sagot ay dapat ulitin nang isang beses, at sa pangalawang pagkakatao'y gumamit ng ibang wika."
        elif self.language == 'it':
            return "La tua risposta dovrebbe essere ripetuta una volta e la seconda dovrebbe essere in una lingua diversa."
        elif self.language == 'bn':
            return "আপনার প্রতিক্রিয়া একবার পুনরাবৃত্তি করা উচিত এবং দ্বিতীয়টি ভিন্ন ভাষায় হওয়া উচিত।"
        elif self.language == 'id':
            return "Tanggapan Anda harus diulang sekali dan yang kedua harus dalam bahasa yang berbeda."
        # New languages
        elif self.language == 'qu':
            return "Kutichisqaykita huk kutita kutichinayki, chaymanta iskay kutipitaq huk simipi willanayki."
        elif self.language == 'zu':
            return "Impendulo yakho kufanele iphindwe kanye futhi kwesibili kufanele ibe ngolimi oluhlukile."
        elif self.language == 'mg':
            return "Ny valinteninao dia tsy maintsy averina indray mandeha ary ny faharoa dia tsy maintsy amin'ny fiteny hafa."
        elif self.language == 'sv':
            return "Ditt svar ska upprepas en gång och den andra gången ska vara på ett annat språk."
        elif self.language == 'ro':
            return "Răspunsul tău trebuie repetat o dată, iar a doua oară trebuie să fie într-o limbă diferită."
        elif self.language == 'tr':
            return "Yanıtınız bir kez tekrarlanmalı ve ikincisi farklı bir dilde olmalıdır."
        elif self.language == 'ta':
            return "உங்கள் பதில் ஒருமுறை திரும்ப கூறப்பட வேண்டும், இரண்டாவது முறை வேறு மொழியில் இருக்க வேண்டும்."
        elif self.language == 'hy':
            return "Ձեր պատասխանը պետք է կրկնվի մեկ անգամ, և երկրորդը պետք է լինի այլ լեզվով։"
        elif self.language == 'ko':
            return "답변을 한 번 반복해야 하며, 두 번째는 다른 언어로 작성되어야 합니다."
        elif self.language == 'te':
            return "మీ సమాధానాన్ని ఒకసారి పునరావృతం చేయాలి మరియు రెండవది వేరే భాషలో ఉండాలి."
        elif self.language == 'ka':
            return "თქვენი პასუხი უნდა გამეორდეს ერთხელ და მეორე უნდა იყოს განსხვავებულ ენაზე."
        elif self.language == 'ky':
            return "Жообуңуз бир жолу кайталанып, экинчиси башка тилде болушу керек."
        elif self.language == 'pt':
            return "Sua resposta deve ser repetida uma vez e a segunda deve ser em um idioma diferente."
        elif self.language == 'hi':
            return "आपके उत्तर को एक बार दोहराया जाना चाहिए और दूसरी बार अलग भाषा में होना चाहिए।"


instruction_classes = {
    "keywords:frequency": KeywordFrequency,
    "keywords:together": KeywordsTogether,
    "keywords:banned": BannedKeywords,
    "keywords:paragraph_end": ParagraphEnd,
    "keywords:first_word": FirstWord,
    "length:max_words": MaxWords,
    "length:range_words": RangeWords,
    "format:addition_at_end": AdditionAtEnd,
    "format:title_brackets": TitleBrackets,
    "format:markdown_highlight": MarkdownHighlight,
    "format:json_output": JsonOutput,
    "format:two_answers_with_separator": TwoAnswersWithSeparator,
    "format:markdown_title": MarkdownTitle,
    "format:ordered_list": OrderedList,
    "format:markdown_bold_italic_paragraph": MarkdownBoldItalicParagraph,
    "repeat:copy_request": CopyRequest,
    "repeat:before_answer": BeforeAnswer,
    "repeat:first_last_same": FirstLastSame,
    "repeat:last_sentence": LastSentence,
    "repeat:sentence_n_times": SentenceNTimes,
    "repeat:all_sentences_twice": AllSentencesTwice,
    "marks:wrap_in_quotes": WrapInQuotes,
    "marks:no_commas": NoCommas,
    "marks:replace_with_exclamations": ReplaceWithExclamations,
    "marks:end_with_semicolons": EndWithSemicolons,
    "marks:replace_with_asterisks": ReplaceWithAsterisks,
    "citation:square_brackets": SquareBrackets,
    "citation:start_from_zero": StartFromZero,
    "citation:inline": Inline,
    "emoji:end": EmojiEnd,
    "emoji:frequency": EmojiFrequency,
    "emoji:banned": EmojiBanned,
    "style:official": FormalLanguageStyle,
    "style:informal": InformalLanguageStyle,
    "style:technical": ProfessionalTerminology,
    "style:poetic": PoeticStyle,
    "style:letter": FormalLetterFormat,
    "tone:humorous": HumorousTone,
    "tone:positive": PositiveTone,
    "tone:negative": NegativeTone,
    "tone:sarcastic": SarcasticTone,
    "tone:angry": AngryTone,
    "content:jokes": IncludeJokes,
    "content:quotes": IncludeQuotes,
    "content:celebrity": MentionFamousPerson,
    "language_switch:multilingual": ThreeLanguages,
    "language_switch:repeat": RepeatInDifferentLanguage,
}
