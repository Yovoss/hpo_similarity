""" class to test CalculateSimilarity class
"""

import os
import unittest

from hpo_similarity.ontology import Ontology
from hpo_similarity.similarity import CalculateSimilarity

class TestCalculateSimilarityPy(unittest.TestCase):
    """ class to test CalculateSimilarity
    """
    
    def setUp(self):
        """ construct a CalculateSimilarity object for unit tests
        """
        
        path = os.path.join(os.path.dirname(__file__), "data", "obo.txt")
        ontology = Ontology(path)
        graph = ontology.get_graph()
        
        self.hpo_terms = {
            "person_01": ["HP:0000924"],
            "person_02": ["HP:0000118", "HP:0002011"],
            "person_03": ["HP:0000707", "HP:0002011"]
        }
        
        self.hpo_graph = CalculateSimilarity(self.hpo_terms, graph)
        
    def test_setup(self):
        """ test that the class initialised correctly.
        
        Mainly I want to check that when the class initialised, it ran
        tally_hpo_terms() correctly. Check that the counts of the HPO terms
        used in the probands match what is expected.
        """
        
        self.assertEqual(self.hpo_graph.total_freq, 5)
        self.assertEqual(self.hpo_graph.hpo_counts["HP:0002011"], 2)
        self.assertEqual(self.hpo_graph.hpo_counts["HP:0000118"], 1)
        
        # Check that we get an error if we look for counts of a term that was
        # not used in the probands.
        with self.assertRaises(KeyError):
            self.assertEqual(self.hpo_graph.hpo_counts["HP:0000001"])
    
    def test_add_hpo(self):
        """ check that HPO counting works correctly
        """
        
        # check the baseline count for a term
        self.assertEqual(self.hpo_graph.hpo_counts["HP:0002011"], 2)
        
        # add a term, and check that the count for the term increases, along
        # with the total number of terms used
        self.hpo_graph.add_hpo("HP:0002011")
        self.assertEqual(self.hpo_graph.hpo_counts["HP:0002011"], 3)
        self.assertEqual(self.hpo_graph.total_freq, 6)
        
        # check that if we try to add a term that isn't in the HPO ontology, we
        # don't increment any counts
        self.hpo_graph.add_hpo("unknown_term")
        self.assertEqual(self.hpo_graph.total_freq, 6)
        
        # Check that if we add a term that currently doesn't have a tallied
        # count then the term getes inserted correctly, and the counts increment
        # appropriately.
        with self.assertRaises(KeyError):
            self.assertEqual(self.hpo_graph.hpo_counts["HP:0000001"])
        
        self.hpo_graph.add_hpo("HP:0000001")
        self.assertEqual(self.hpo_graph.hpo_counts["HP:0000001"], 1)
        self.assertEqual(self.hpo_graph.total_freq, 7)
    
    def test_get_descendants(self):
        """ check that get_descendants works correctly
        """
        
        # check that a high-level node returns the expected set of nodes
        self.assertEqual(self.hpo_graph.get_descendants("HP:0000118"), \
            set(['HP:0000707', 'HP:0002011', 'HP:0000924']))
        
        # check that a terminal node doesn't have any descendants
        self.assertEqual(self.hpo_graph.get_descendants("HP:0000924"), \
            set([]))
    
    def test_get_ancestors(self):
        """ check that get_ancestors works correctly
        """
        
        # check that we get an appropriate set of ancestor tersm for a termina
        # node
        self.assertEqual(self.hpo_graph.get_ancestors("HP:0000924"), \
            set(['HP:0000001', 'HP:0000118', 'HP:0000924']))
        
        # check that even the top node returns itself as a ancestor node
        self.assertEqual(self.hpo_graph.get_ancestors("HP:0000001"), \
            set(['HP:0000001']))
    
    def test_find_common_ancestors(self):
        """ check that find_common_ancestors works correctly
        """
        
        # check that two terms on different arms only return their common
        # ancestors
        self.assertEqual(self.hpo_graph.find_common_ancestors('HP:0000924', \
            'HP:0000707'), set(["HP:0000001", "HP:0000118"]))
        
        # check that two identical terms return their list of ancestors
        self.assertEqual(self.hpo_graph.find_common_ancestors('HP:0000707', \
            'HP:0000707'), set(["HP:0000001", "HP:0000118", "HP:0000707"]))
        
        # check that if one of the two terms is not in the HPO graqph, then we
        # return an empty set
        self.assertEqual(self.hpo_graph.find_common_ancestors('HP:9999999', \
            'HP:0000707'), set([]))
