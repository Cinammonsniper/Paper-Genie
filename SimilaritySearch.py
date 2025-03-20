from SubjectInfo import Subject

class SimilaritySearch:
    
    def __init__(self, subjects: dict[str, Subject], text: str) -> None:
        self.text = text
        self.subjects = subjects
        
        self.text = self.preprocess_text(self.text)
        self.text_set = set(self.text)
    
    def preprocess_text(self, text) -> str:
        text = text.translate({ord(i): None for i in ' '})
        text = text.lower()
        return text
    
    
    def create_anagram(self, subject: str) -> list[set]: 
        anagram_list = []
        subject_list = list(subject)
        for i, char in enumerate(subject_list):
            anagram = set()
            for j in range(0, len(self.text)):
                if (i+len(self.text)) <= len(subject):
                    anagram.add(subject[i+j])
                else:
                    return anagram_list
            anagram_list.append(anagram)
        return[]
    
    def return_similarity(self, set_list: list[set]) -> bool:
        for _set in set_list:
            inter = _set.intersection(self.text_set)
            uni = _set.union(self.text_set)
            sim = len(inter)/len(uni)
            if sim > 0.70:
                return True
        return False
    
    def process(self) -> dict[str, Subject]:
        similar_subjects = {}
        for code in self.subjects:
            subject_text = self.preprocess_text((self.subjects[code]).name)
            subject_anagrams = self.create_anagram(subject_text)
            similarity = self.return_similarity(subject_anagrams)
            if similarity is True:
                similar_subjects[code] = self.subjects[code]
        return similar_subjects
