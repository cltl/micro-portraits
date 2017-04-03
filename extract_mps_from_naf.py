import sys
from collections import defaultdict
from KafNafParserPy import *

target_pos = ['noun','name','pron']
dep2heads = defaultdict(list)
head2deps = defaultdict(list)
dep_extractor = None
term2lemma = {}


class cMicroportait():
    '''
    Class that captures microportrait information
    '''

    def __init__(self, portraitId):
        '''
        Initiates object
        :param portraitId:
        Each microportrait should have a unique id
        '''

        self.portraitId = portraitId
        self.labels = []
        self.properties = []
        self.activities = []
        self.colabels = []

    def add_label(self, label):

        self.labels.append(label)

    def add_property(self, property):

        self.properties.append(property)

    def add_activity(self, activity):

        self.activities.append(activity)

    def add_colabel(self, colabel):

        self.colabels.append(colabel)

    def get_colabels(self):

        return self.colabels

    def get_identifier(self):

        return self.portraitId



def get_constituent(head_id):
    '''
    Function that creates the largest constituent headed by a given term
    :param head_id: id of head of constituent
    :return: list of term_ids (strings) making up the constituent
    '''
    global dep_extractor

    dependents = dep_extractor.get_full_dependents(head_id, [])
    dependents.append(head_id)

    return dependents

def create_sequence_in_lemmas(nafobj, term_ids):
    '''
    Function that takes a list of term ids and creates a list of lemmas ordered according to surface order
    :param nafobj: input naf object
    :param term_ids: list of term ids
    :return: ordered list of lemmas
    '''
    offset2lemmas = {}

    for tid in term_ids:
        myterm = nafobj.get_term(tid)
        first_token_wid = myterm.get_span().get_span_ids()[0]
        first_token = nafobj.get_token(first_token_wid)
        offset = int(first_token.get_offset())
        offset2lemmas[offset] = myterm.get_lemma()

    #FIXME: make string with extra space dependent on end word and offset next word
    lemma_seq = []
    for offs, lemma in sorted(offset2lemmas.items()):
        lemma_seq.append(lemma)

    lemma_string = " ".join(lemma_seq)
    return lemma_string


def get_constituent_in_ordered_lemmas(nafobj, head_id):

    my_constituent = get_constituent(head_id)
    lemmas = create_sequence_in_lemmas(nafobj, my_constituent)

    return lemmas


def get_lemma_from_term(nafobj, term_id):
    '''
    Function that extracts a terms lemma
    :param nafobj: input naf
    :param term_id: identifier of the term
    :return:
    '''
    term = nafobj.get_term(term_id)
    lemma = term.get_lemma()

    return lemma


def get_pos_from_term(nafobj, term_id):
    '''
    Function that extracts pos of term
    :param nafobj: input naf
    :param term_id: identifier of the term
    :return:
    '''
    term = nafobj.get_term(term_id)
    pos = term.get_pos()

    return pos

def has_predicative_complement(head_id):
    if head_id in head2deps:
        for dep in head2deps.get(head_id):
            if 'hd/predc' in dep:
                return True
    return False


def get_basics_and_constituents_from_coordinated(nafobj, head_id):

    additions = []
    full_constituent = get_constituent_in_ordered_lemmas(nafobj, head_id)
    additions.append(full_constituent)
    for dep in head2deps.get(head_id):
        headlemma = get_lemma_from_term(nafobj, dep[0])
        additions.append(headlemma)
        if dep[0] in head2deps:
            constituent = get_constituent_in_ordered_lemmas(nafobj, dep[0])
            additions.append(constituent)

    return additions


def get_predicative_info(nafobj, head_id):

    for deprel in head2deps.get(head_id):
        gram_rel = deprel[1]
        if gram_rel == 'hd/predc':
            pos = get_pos_from_term(nafobj, deprel[0])
            if pos == 'vg':
                basicroles = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                basicrole = basicroles[0]
            #predicative structure means no agent relation, property instead
            else:
                basicrole = get_lemma_from_term(nafobj, deprel[0])
                basicroles = [basicrole]
            # also add full constituent if longer than one word
                if deprel[0] in head2deps:
                    constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                    basicroles.append(constituent)
    return basicrole, basicroles

def analyze_subject_relations(nafobj, head_id, term_portrait, vcsub=False):

    global head2deps

    #default: subject expresses agent
    basicrole = 'agent;'
    #add lemma of event
    basicrole += get_lemma_from_term(nafobj, head_id)
    basicroles = [basicrole]
    predicative = False

    if has_predicative_complement(head_id):
        basicrole, basicroles = get_predicative_info(nafobj, head_id)
        predicative = True

    if head_id in head2deps:
        for deprel in head2deps.get(head_id):
            #ignore entity that is agent
            gram_rel = deprel[1]

            argpos = get_pos_from_term(nafobj, deprel[0])
            if gram_rel == 'hd/vc':
                if argpos == 'vg':
                    args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                    for arg in args:
                        basicroles.append(basicrole + ' ' + arg)
                else:
                    headlemma = get_lemma_from_term(nafobj, head_id)
                    arglemma = get_lemma_from_term(nafobj, deprel[0])
                    basicrole = 'agent;'
                    if not headlemma in ['heb'] and not argpos == 'noun':
                        basicrole += headlemma + ' '
                    basicrole += arglemma
                    basicroles = [basicrole]
                    if not argpos == 'noun':
                        analyze_subject_relations(nafobj, deprel[0], term_portrait, True)
                    elif deprel[0] in head2deps:
                        constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                        completer_role = basicrole + ' ' + constituent.replace(';',',')
                        basicroles.append(completer_role)
            elif gram_rel in ['hd/obj1', 'hd/ld', 'dp/dp', 'hd/pc', 'hd/pobj1', 'hd/obj2', 'hd/se','hd/mod','hd/predm','whd/body']:
                if argpos == 'vg':
                    args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                    for arg in args:
                        basicroles.append(basicrole + ' ' + arg)
                else:
                    arglemma = get_lemma_from_term(nafobj, deprel[0])
                    completer_role = basicrole + ' ' + arglemma
                    basicroles.append(completer_role)
                    if deprel[0] in head2deps:
                        constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                        completer_role = basicrole + ' ' + constituent.replace(';',',')
                        basicroles.append(completer_role)
            #ignore subject relation (= entity itself)
            elif not gram_rel in ['nucl/sat','hd/su', 'hd/svp', 'nucl/tag', 'tag/nucl', 'hd/sat','-- / --', 'hd/predc', 'cmp/body','hd/vc','sat/nucl']:
                print(gram_rel, 'not covered in subject rules', deprel[0], head_id)

    if predicative:
        for brole in basicroles:
            term_portrait.add_property(brole)
    else:
        for brole in basicroles:
            term_portrait.add_activity(brole)


def analyze_pobject(nafobj, head_id, term_portrait):

    governing_rels = dep2heads.get(head_id)
    basic_role = None
    general_head = head_id
    #sometimes dep has no head, make sure not a None-type
    if governing_rels is None:
        governing_rels = []
        termlemma = get_lemma_from_term(nafobj, head_id)
        #preposition is also head of clause in these cases
        basic_role = termlemma + '-rol;' + termlemma
    #FIXME; we now get one out of two in coordinated structures
    for deprel in governing_rels:

        if deprel[1] in ['hd/mod', 'hd/ld','hd/obj1','cmp/body','hd/predc','crd/mod']:
            prep_lemma = get_lemma_from_term(nafobj, head_id)
            head_pos = get_pos_from_term(nafobj, deprel[0])
            if head_pos == 'vg':
                lemmas = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                basic_role = prep_lemma + '-rol;' + lemmas[0]
                print('Coordination in prepositional structure; taking full constituent only')
            else:
                head_lemma = get_lemma_from_term(nafobj, deprel[0])
                basic_role = prep_lemma + '-rol;' + head_lemma
            general_head = deprel[0]
        elif deprel[1] == 'hd/obj2':
            prep_lemma = get_lemma_from_term(nafobj, head_id)
            head_pos = get_pos_from_term(nafobj, deprel[0])
            if head_pos == 'vg':
                lemmas = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                basic_role = 'recipient;' + lemmas[0]
                print('Coordination in prepositional structure; taking full constituent only')
            else:
                head_lemma = get_lemma_from_term(nafobj, deprel[0])
                basic_role = 'recepient;' + head_lemma
            general_head = deprel[0]
        elif not deprel[1] in ['hd/pc', 'crd/cnj', 'dp/dp']:
            print(deprel, 'between PP and head')
    return basic_role, general_head

def analyze_obj2_relations(nafobj, head_id, term_portrait):
    '''
    Function that creates involvement in activities based on obj2 relations
    :param nafobj: input naf
    :param head_id: identifier of verb
    :param term_portrait: term project object
    :return:
    '''

    headlemma = get_lemma_from_term(nafobj, head_id)
    if not headlemma in ['ben','heb','doe']:
        basicrole = 'recepient;'
    else:
        basicrole = 'hasrole;'
    basicrole += headlemma

    basicroles = [headlemma]

    for deprel in head2deps.get(head_id):
        gramrel = deprel[1]
        if gramrel == 'hd/su' and 'recepient' in basicrole:
            specific_basis = 'recepient;' + headlemma
            argpos = get_lemma_from_term(nafobj, deprel[0])
            if argpos == 'vg':
                args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                for arg in args:
                    basicroles.append(specific_basis + ' FROM ' + arg)
            else:
                arglemma = get_lemma_from_term(nafobj, deprel[0])
                completer_role = specific_basis + ' FROM ' + arglemma
                basicroles.append(completer_role)
                if deprel[0] in head2deps:
                    constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                    completer_role = specific_basis + ' ' + constituent.replace(';',',')
                    basicroles.append(completer_role)
        elif gramrel in ['hd/su', 'hd/obj1','hd/predm','hd/se','hd/mod','hd/svp','hd/vc','hd/predc','hd/ld','dp/dp']:
            argpos = get_lemma_from_term(nafobj, deprel[0])
            if argpos == 'vg':
                args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                for arg in args:
                    basicroles.append(basicrole + ' ' + arg)
            else:
                arglemma = get_lemma_from_term(nafobj, deprel[0])
                completer_role = basicrole + ' ' + arglemma
                basicroles.append(completer_role)
                if deprel[0] in head2deps:
                    constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                    completer_role = basicrole + ' ' + constituent.replace(';',',')
                    basicroles.append(completer_role)
        elif not gramrel in ['hd/obj2','cmp/body','sat/nucl','-- / --']:
            print(gramrel, 'not covered yet for obj2')


def relevant_obj_cooccurence(headpos, gram_rel, basicrole):

    if headpos in ['verb', 'adj']:
        if gram_rel in ['hd/su', 'hd/ld', 'dp/dp', 'hd/pc', 'hd/pobj1', 'hd/obj2', 'hd/se', 'hd/mod','hd/predm','hd/vc']:
            return True
    elif headpos == 'prep':
        if gram_rel in ['hd/su', 'hd/ld', 'dp/dp', 'hd/pc', 'hd/se', 'hd/mod','hd/predm','hd/vc', 'hd/obj1']:
            return True
        elif gram_rel == 'hd/pobj' and 'recepient' in basicrole:
            return True
        elif gram_rel == 'hd/obj2' and not 'recepient' in basicrole:
            return True
    return False

def irrelevant_obj_occurrence(headpos, gram_rel, basicrole):

    if headpos in ['verb','adj']:
        if gram_rel in ['hd/obj1', 'hd/svp', 'nucl/tag', 'tag/nucl', 'hd/sat', '-- / --', 'hd/predc', 'cmp/body', 'sat/nucl','nucl/sat','hd/det']:
            return True
    elif headpos in ['prep','comp']:
        if gram_rel in ['dlink/nucl','hd/svp', 'nucl/tag', 'tag/nucl', 'hd/sat', '-- / --', 'hd/predc', 'cmp/body', 'sat/nucl','nucl/sat','hd/det']:
            return True
        elif gram_rel == 'hd/pobj' and not 'recepient' in basicrole:
            return True
        elif gram_rel == 'hd/obj2' and 'recepient' in basicrole:
            return True
    return False


def analyze_object_relations(nafobj, head_id, term_portrait):
    '''
    Function that creates involvement in activities based on object relations
    :param nafobj:
    :param head_id:
    :param term_portrait:
    :return:
    '''

    headpos = get_pos_from_term(nafobj, head_id)
    basicroles = []
    if headpos in ['prep','comp']:
        #FIXME: if preposition hads the sentence, obj1 is counted double
        basicrole, head_id = analyze_pobject(nafobj, head_id, term_portrait)
        basicroles = [basicrole]
        #print(head_id, get_lemma_from_term(nafobj, head_id))
    elif headpos in ['verb','adj']:
        basicrole = 'undergoer;'
        # add lemma of event
        basicrole += get_lemma_from_term(nafobj, head_id)
        basicroles = [basicrole]
    if headpos in ['verb', 'adj', 'prep', 'comp'] and not basicrole is None:

        for deprel in head2deps.get(head_id):
            # ignore entity that is agent
            gram_rel = deprel[1]
            if gram_rel == 'hd/su':
                argpos = get_pos_from_term(nafobj, deprel[0])
                if argpos == 'vg':
                    args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                    for arg in args:
                        basicroles.append(basicrole + ' BY ' + arg)
                else:
                    arglemma = get_lemma_from_term(nafobj, deprel[0])
                    completer_role = basicrole + ' BY ' + arglemma
                    basicroles.append(completer_role)
                    if deprel[0] in head2deps:
                        constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                        completer_role = basicrole + ' BY ' + constituent.replace(';', ',')
                        basicroles.append(completer_role)
            elif relevant_obj_cooccurence(headpos, gram_rel, basicrole):
                argpos = get_pos_from_term(nafobj, deprel[0])
                if argpos == 'vg':
                    args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                    for arg in args:
                        basicroles.append(basicrole + ' ' + arg)
                else:
                    arglemma = get_lemma_from_term(nafobj, deprel[0])
                    completer_role = basicrole + ' ' + arglemma
                    basicroles.append(completer_role)
                    if deprel[0] in head2deps:
                        constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                        completer_role = basicrole + ' ' + constituent.replace(';',',')
                        basicroles.append(completer_role)
            elif not irrelevant_obj_occurrence(headpos, gram_rel, basicrole):
                print(gram_rel, 'not covered in object1 rules', deprel[0])
    elif not headpos == 'prep':
        print(headpos, 'head of obj1')

    for brole in basicroles:
        if brole is not None:
            term_portrait.add_activity(brole)

def is_passive(deprels):

    rels = []
    for drel in deprels:
        rels.append(drel[1])
    if 'hd/su' in rels and 'hd/obj1' in rels:
        return True
    else:
        return False


def add_information_passive(nafobj, head_id):
    '''
    Function that adds additional arguments to vc for passives
    :param nafobj: input naf
    :param head_id: id of verbal complement
    :param basicrole: basic relation where role is added
    :return:
    '''
    basicroles = []
    for deprel in head2deps.get(head_id):
        # ignore entity that is agent
        gram_rel = deprel[1]
        if gram_rel in ['hd/ld', 'dp/dp', 'hd/pc', 'hd/pobj1', 'hd/obj2', 'hd/se', 'hd/mod']:
            argpos = get_pos_from_term(nafobj, deprel[0])
            if argpos == 'vg':
                args = get_basics_and_constituents_from_coordinated(nafobj, deprel[0])
                for arg in args:
                    basicroles.append(arg)
            else:
                arglemma = get_lemma_from_term(nafobj, deprel[0])
                basicroles.append(arglemma)
                if deprel[0] in head2deps:
                    constituent = get_constituent_in_ordered_lemmas(nafobj, deprel[0])
                    basicroles.append(constituent.replace(';',','))
        elif not gram_rel in ['hd/su', 'hd/obj1', 'hd/svp', 'nucl/tag', 'tag/nucl', 'hd/sat', '-- / --', 'hd/predc','hd/vc']:
            print(gram_rel, 'not covered in rules for vc head passives')
    return basicroles

def analyze_passive_structure(nafobj, entityid, term_portrait):
    '''
    Function to analyze passive structure
    :param nafobj: input naf
    :param head_id: identifier of head
    :param term_portrait: microportrait object
    :return:
    '''
    heads = dep2heads.get(entityid)
    basicrole = 'undergoer;'
    basicroles = []
    #obj_additions = []
    #subj_additions = []
    #FIXME: add rule that makes sure agent is recovered as well
    for head in heads:
        if head[1] == 'hd/obj1':
            event_lemma = get_lemma_from_term(nafobj, head[0])
            basicrole += event_lemma
            basicroles.append(basicrole)
            #creates finished roles (we have the basic
            obj_additions = add_information_passive(nafobj, head[0])
        elif head[1] == 'hd/su':
            subj_additions = add_information_passive(nafobj, head[0])

    for obj_add in obj_additions:
        fullrole = basicrole + ' ' + obj_add
        basicroles.append(fullrole)
    for su_add in subj_additions:
        fullrole = basicrole + ' ' + su_add
        basicroles.append(fullrole)

    for br in basicroles:
        term_portrait.add_activity(br)


def analyze_coord_relations(nafobj, head_id, term_portrait):
    '''
    Function that deals with activities for coordinated structures
    :param nafobj: input naf
    :param head_id: identifier of coordinated head
    :param term_portrait: microportrait object
    :return:
    '''
    heads = dep2heads.get(head_id)
    if heads is None:
        heads = []
        #FIXME: in these cases, microportraits are not merged (todo: what is label or property; same term should not be label or property more than once)
    if len(heads) == 1 or not is_passive(heads):
        for myhead in heads:
            myhead = heads[0]
            if myhead[1] == 'hd/su':
                analyze_subject_relations(nafobj, myhead[0], term_portrait)
            elif myhead[1] == 'hd/obj1':
                analyze_object_relations(nafobj, myhead[0], term_portrait)
            elif myhead[1] == 'hd/obj2':
                analyze_obj2_relations(nafobj, myhead[0], term_portrait)
            elif myhead[1] == 'crd/cnj':
                analyze_coord_relations(nafobj, myhead[0], term_portrait)
            elif not myhead[1] in ['dp/dp','tag/nucl','hd/predc','hd/predm','hd/hd', 'hd/mod', 'cmp/body', 'hd/app', 'mwp/mwp', '-- / --', 'dp/dp','nucl/sat']:
                print(myhead[1], 'in coordinated relation', myhead[0])
    else:
        analyze_passive_structure(nafobj, head_id, term_portrait)



def investigate_relations(nafobj, tid, term_portrait):

    heads = dep2heads.get(tid)
    if len(heads) == 1 or not is_passive(heads):
        for head_rel in heads:
            if head_rel[1] == 'hd/su':
                analyze_subject_relations(nafobj, head_rel[0], term_portrait)
            elif head_rel[1] in ['hd/obj1','hd/se','hd/pobj1','hd/vc','dlink/nucl']:
                analyze_object_relations(nafobj, head_rel[0], term_portrait)
            elif head_rel[1] in ['crd/cnj','cnj/cnj']:
                analyze_coord_relations(nafobj, head_rel[0], term_portrait)
            elif head_rel[1] == 'hd/obj2':
                analyze_obj2_relations(nafobj, head_rel[0], term_portrait)
            elif not head_rel[1] in ['hd/sup','rhd/body','hd/predc', 'hd/hd', 'hd/mod', 'hd/me', 'cmp/body', 'hd/app', 'mwp/mwp', '-- / --', 'dp/dp','nucl/sat','tag/nucl']:
                print(head_rel[1], 'relations investigation', head_rel[0])
    else:
        analyze_passive_structure(nafobj, tid, term_portrait)


def get_activity_relations(nafobj, term_portrait):
    '''
    Function that identifies whether entity is involved in activity according to syntactic structure
    :param nafobj: input nafobj
    :param term_portrait: the microportrait object
    :return: None
    '''
    global dep2heads

    tid = term_portrait.get_identifier()
    investigate_relations(nafobj, tid, term_portrait)


def extract_sentence_portrait(nafobj, term):
    '''
    Extracts portrait information
    :param nafobj: input file nafobj
    :param term: the term for which the portrait is being extracted
    :return: microportrait information
    '''
    global dep2heads, head2deps
    #create portrait for term with id as microportrait id
    tid = term.get_id()
    term_portrait = cMicroportait(tid)
    #check if mwp
    mwp = False
    if tid in head2deps:
        for dep in head2deps.get(tid):
            if dep[1] == 'hd/app':
                apposed_constituent = get_constituent(dep[0])
                app_string = create_sequence_in_lemmas(nafobj, apposed_constituent)
                term_portrait.add_label(app_string)
                term_portrait.add_colabel(dep[0])
            elif dep[1] in ['mwp/mwp','hd/det']:
                mwe_constituent = get_constituent(tid)
                mwe_string = create_sequence_in_lemmas(nafobj, mwe_constituent)
                term_portrait.add_label(mwe_string)
                term_portrait.add_colabel(dep[0])
                if 'mwp' in dep[1]:
                    mwp = True
            elif dep[1] in ['hd/mod','dp/dp','cnj/cnj','rhd/body','hd/vc','tag/nucl','nucl/tag','-- / --','whd/body','hd/me','sat/nucl','rhd/mod']:
                modifier_constituent = get_constituent(dep[0])
                modifier_string = create_sequence_in_lemmas(nafobj, modifier_constituent)
                term_portrait.add_property(modifier_string)
            else:
                print(dep[1], 'new dependency of entity')
    if not mwp:
        term_portrait.add_label(term.get_lemma())

    if tid in dep2heads:
        get_activity_relations(nafobj, term_portrait)
    return term_portrait


def get_term_info(nafobj):

    global term2lemma

    for term in nafobj.get_terms():
        tid = term.get_id()
        term2lemma[tid] = term.get_lemma()




def fill_headdep_dicts(nafobj):
    '''
    Function that creates dictionaries of dep to heads and head to deps
    :param nafobj: nafobj from input file
    :return: None
    '''
    global dep2heads, head2deps

    for dep in nafobj.get_dependencies():
        head = dep.get_from()
        mydep = dep.get_to()
        relation = dep.get_function()
        dep2heads[mydep].append([head, relation])
        head2deps[head].append([mydep, relation])


def create_info_dicts(nafobj):
    '''
    Funtction that extracts information form naf which we will need a lot
    :param nafobj: input naf
    :return: None
    '''
    fill_headdep_dicts(nafobj)
    get_term_info(nafobj)


def get_colabels(minimicroportraits):

    colabs = []
    for k, v in minimicroportraits.items():
        colabs += v.colabels

    return colabs


def remove_duplicate_portraits(minimicroportraits):

    redundant_labels = get_colabels(minimicroportraits)
    updated_portraits = {}
    for k, v in minimicroportraits.items():
        if not k in redundant_labels:
            updated_portraits[k] = v
    return updated_portraits


def extract_sentence_level_portraits(nafobj):
    '''
    Goes through nafobject and extracts microportaits on sentence leven
    :param nafobj: nafobj of input file
    :return: dictionary of term_ids and their microportait on sentence level
    '''

    global dep_extractor
    minimicroportaits = {}
    dep_extractor = nafobj.get_dependency_extractor()
    for term in nafobj.get_terms():
        if term.get_pos() in target_pos:
            term_portrait = extract_sentence_portrait(nafobj, term)
            minimicroportaits[term.get_id()] = term_portrait
    sentence_level_portraits = remove_duplicate_portraits(minimicroportaits)

    return sentence_level_portraits


def create_output(slportraits, prefix, outputfile):


    portraits = set()
    for k, v in slportraits.items():
        mptid = prefix + k
        for label in v.labels:
            label = label.replace(';',',')
            portraits.add(mptid + ';label;' + label.encode('utf8') + '\n')
        for property in v.properties:
            property = property.replace(';',',')
            portraits.add(mptid + ';property;' + property.encode('utf8') + '\n')
        #activity consists of role,event
        for activity in v.activities:
            portraits.add(mptid + ';' + activity.encode('utf8') + '\n')
    myout = open(outputfile, 'w')
    for portrait in portraits:
        myout.write(portrait)
    myout.close()

def get_coreferences_from_naf(nafobj):
    '''
    Function that get all coreference relations from naf object
    :param nafobj: input naf
    :return: dictionary from term ids to list of terms they corefer with
    '''

    #FIXME: we want to match head only...we now take anything in the span....
    coref_dict = defaultdict(list)
    for coref in nafobj.get_corefs():
        if coref.get_type() == 'entity':
            corefering_ids = []
            for coref_span in coref.get_spans():
                for target in coref_span:
                    if target.is_head() is not None:
                        corefering_ids.append(target.get_id())
            for tid in corefering_ids:
                for coreftid in corefering_ids:
                    if not coreftid == tid:
                        coref_dict[tid].append(coreftid)

    return coref_dict


def retrieve_merge_candidates(my_coref_dict, sentence_level_portraits):
    '''
    Function that identifies which sentence level portraits may merge across sentences
    :param my_coref_dict: dictionary mapping each term id to all other term ids it corefers with
    :param sentence_level_portraits: dictionary of term id and its sentencel level portraits
    :return: list of term identifier keys fro mergreable portraits
    '''

    merge_candidates = []
    for tid, portrait in sentence_level_portraits.items():
        if tid in my_coref_dict:
            merge_candidates.append(tid)
        else:
            for colabel in portrait.get_colabels():
                if colabel in my_coref_dict:
                    merge_candidates.append(tid)
    return merge_candidates

def already_merging(tid1, tid2, to_merge):

    if tid1 in to_merge and tid2 in to_merge.get(tid1):
        return True
    elif tid2 in to_merge and tid1 in to_merge.get(tid2):
        return True
    else:
        for v in to_merge.values():
            if tid1 in v and tid2 in v:
                return True

    return False


def merge_coreference_portraits(nafobj, sentence_level_portraits):

    #1. get coreferences from naf (dict each term identifier to all its coreferences

    my_coref_dict = get_coreferences_from_naf(nafobj)
    to_merge = defaultdict(list)
    merge_candidates = retrieve_merge_candidates(my_coref_dict, sentence_level_portraits)
    for possible_merge in merge_candidates:
        merge_ids = [possible_merge] + sentence_level_portraits.get(possible_merge).get_colabels()
        merging_with = []
        for tid in merge_ids:
            if tid in my_coref_dict:
                merging_with += [tid] + my_coref_dict.get(tid)
        for candidate in merge_candidates:
            if not candidate == possible_merge:
                merge_ids = [candidate] + sentence_level_portraits.get(candidate).get_colabels()
                if len(set(merge_ids) & set(merging_with)) > 0:
                    if not already_merging(candidate, possible_merge, to_merge):
                        if candidate in to_merge:
                            to_merge[candidate].append(possible_merge)
                        else:
                            to_merge[possible_merge].append(candidate)

    merged = {}
    for k, v in to_merge.items():
        main_portrait = sentence_level_portraits.get(k)
        for merger in v:
            merge_portrait = sentence_level_portraits.get(merger)
            if merge_portrait is None:
                previously_merged = merged.get(merger)
                merge_portrait = sentence_level_portraits.get(previously_merged)
                merged[previously_merged] = k
                del sentence_level_portraits[previously_merged]
            else:
                del sentence_level_portraits[merger]

            main_portrait.labels += merge_portrait.labels
            main_portrait.properties += merge_portrait.properties
            main_portrait.activities += merge_portrait.activities
            main_portrait.colabels += merge_portrait.colabels
            merged[merger] = k



def extract_microportraits(inputfile, outputfile):
    '''
    Function that calls functions extracting components of microportraits and merges them
    :param inputfile: the input naf file
    :param outputfile: the output file in csv
    :return: None
    '''
    global target_pos

    nafobj = KafNafParser(inputfile)
    create_info_dicts(nafobj)
    sentence_level_portraits = extract_sentence_level_portraits(nafobj)
    merge_coreference_portraits(nafobj, sentence_level_portraits)
    prefix = inputfile.rstrip('.naf')
    create_output(sentence_level_portraits, prefix, outputfile)





def main(argv=None):


    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python extract_mps_from_naf.py article.naf microportraits.csv')
    else:
        extract_microportraits(argv[1], argv[2])


if __name__ == '__main__':
    main()
