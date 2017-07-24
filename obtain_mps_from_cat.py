    import sys
import os
import csv
from collections import defaultdict
from lxml import etree




def get_tokens(cattree):

    tid2token = {}
    for token in cattree.findall('token'):
        tid = token.get('t_id')
        tid2token[tid] = token.text
    
    return tid2token

def get_markable_span(markable):
    
    span = []
    for tanch in markable.findall('token_anchor'):
        span.append(tanch.get('t_id'))
    
    return span

def get_specific_markables(markables, label):

    mid2span = {}
    for markable in markables.findall(label):
        mid = markable.get('m_id')
        span = get_markable_span(markable)
        mid2span[mid] = span
    
    return mid2span

def get_markables(cattree):

    markables = cattree.find('Markables')
    activities = get_specific_markables(markables, 'ACTIVITY')
    labels = get_specific_markables(markables, 'LABEL')
    properties = get_specific_markables(markables, 'PROPERTY')

    return activities, labels, properties

def get_specific_relations(relations, relname, refers_to):

    source2target = defaultdict(list)
    for relation in relations.findall(relname):
        for source in relation.findall('source'):
            sourceid = source.get('m_id')
            for target in relation.findall('target'):
                target_id = target.get('m_id')
                refid = refers_to.get(target_id)
                if not refid is None:
                    source2target[sourceid].append(refid)
                else:
                    refid = refers_to.get(sourceid)
                    if not refid is None:
                        source2target[target_id].append(refid)
                    else:
                        print(target_id, relation.get('r_id'))
    return source2target


def get_roles(relations, refers_to):

    roles = defaultdict(list)
    for role in relations.findall('HAS_ROLE'):
        rolename = role.get('Specific_role')
        sources = []
        for source in role.findall('source'):
            sourcelabel = refers_to.get(source.get('m_id'))
            if not sourcelabel is None:
                sources.append(sourcelabel)
            else:
                print(source.get('m_id'), role.get('r_id'))
        info = [sources, rolename]
        for target in role.findall('target'):
            roles[target.get('m_id')].append(info)
    return roles


def get_references(relations):

    has_references = defaultdict(list)
    for reference in relations.findall('REFERS_TO'):
        refid = reference.get('r_id')
        for source in reference.findall('source'):
            has_references[refid].append(source.get('m_id'))
        for target in reference.findall('target'):
            has_references[refid].append(target.get('m_id'))
    return has_references


def turn_hasref_into_refers_to(has_references):

    refers_to = {}
    to_merge = defaultdict(list)
    for refid, refs in has_references.items():
        for ref in refs:
            if ref in refers_to:
                oldref = refers_to.get(ref)
                if not oldref == refid:
                    to_merge[oldref].append(refid)
                    to_merge[refid].append(oldref)
            refers_to[ref] = refid
    if len(to_merge) > 0:
        print('Implement to merge algorithm now')
    return refers_to



def get_refers_to_relations(relations):

    has_references = get_references(relations)
    refers_to = turn_hasref_into_refers_to(has_references)
    
    return refers_to

def get_relations(cattree):

    relations = cattree.find('Relations')
    #dictionary that maps label markables to their reference relation
    refers_to = get_refers_to_relations(relations)
    #TODO: make a function that merges refers_to relations that have corresponding referents
    #dictionary that maps property to the refers_to property
    applies_to = get_specific_relations(relations, 'APPLIES_TO', refers_to)
    #dictionary refers_to maps sources and targets to the reference id
    #roles (source = [[targets,info]])
    roles = get_roles(relations, refers_to)

    return refers_to, applies_to, roles


def create_description(tokids, tid2token):

    description = ''
    for tid in tokids:
        description += tid2token.get(tid) + ' '
    return description.rstrip()


def get_mp_labels(refers_to, labels, tid2token):

    mps = defaultdict(list)
    for mid, rid in refers_to.items():
        tokids = labels.get(mid)
        if len(tokids) > 0:
            description = create_description(tokids, tid2token)
            mps[rid].append(['label',description])
    return mps


def add_properties(mps, properties, applies_to, tid2token):

    for mid, rids in applies_to.items():
        tokids = properties.get(mid)
        if len(tokids) > 0:
            for rid in rids:
                description = create_description(tokids, tid2token)
                mps[rid].append(['property',description])

def add_activities(mps, activities, roles, tid2token):
    
    for mid, info in roles.items():
        tokids = activities.get(mid)
        if len(tokids) > 0:
            for role in info:
                for rid in role[0]:
                    description = create_description(tokids, tid2token)
                    mps[rid].append([role[1], description])




def get_mps_from_cat(inputfile):

    parser = etree.XMLParser(ns_clean=True)
    cattree = etree.parse(inputfile, parser)
    tid2token = get_tokens(cattree)
    activities, labels, properties = get_markables(cattree)
    refers_to, applies_to, roles = get_relations(cattree)

    mps = get_mp_labels(refers_to, labels, tid2token)
    add_properties(mps, properties, applies_to, tid2token)
    add_activities(mps, activities, roles, tid2token)

    return mps



def obtain_mps(inputfile, outputfile):

    mps = get_mps_from_cat(inputfile)
    csvfile = open(outputfile, 'w')
    csvwriter = csv.writer(csvfile, delimiter=';')
    for mp, descriptions in mps.items():
        for description in descriptions:
            description.insert(0, mp)
            csvwriter.writerow(description)






def main(argv=None):
    
    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python obtain_mps_from_cat.py inputfile.xml outputfile.csv')
    else:
        obtain_mps(argv[1], argv[2])



if __name__ == '__main__':
    main()
