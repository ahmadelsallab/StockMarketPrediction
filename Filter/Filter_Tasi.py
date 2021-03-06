'''
Created on Aug 6, 2014

@author: ASALLAB
'''
from DatasetBuilder.DatasetBuilder import DatasetBuilder
from LanguageModel.LanguageModel import LanguageModel   
from FeaturesExtractor.FeaturesExtractor import FeaturesExtractor
from Classifier.Classifier import Classifier
import os

class Filter(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        :type self:
        '''
        # Start the DatasetBuilder
        #-------------------------
        # Configurations file xml of the dataset builder
        configFileDatasetBuilder = os.path.join('DatasetBuilder','Configurations','Configurations.xml')
               
        # The serialization file to save the dataset
        datasetSerializationFile = os.path.join('DatasetBuilder','Output', 'dataset.bin')
               
        # The XLSX file name for train set
        xlsxTrainFileName = os.path.join('DatasetBuilder','Input','train')
        
        
        # Initialize the DatasetBuilder from serialization file
        datasetBuilder = DatasetBuilder(configFileDatasetBuilder, [], datasetSerializationFile)
        
        datasetBuilder.trainSet = datasetBuilder.GetDatasetFromXLSXFile(xlsxTrainFileName)
                
        
        # Configurations file xml of the language model
        configFileLanguageModel_lexicon = os.path.join('LanguageModel', 'Configurations', 'Configurations-lexicon.xml')
        configFileLanguageModel_Tasi = os.path.join('LanguageModel', 'Configurations', 'Configurations-Tasi.xml')
        stopWordsFileName = os.path.join('LanguageModel', 'Input', 'stop_words.txt')
        linksDBFile = os.path.join('LanguageModel', 'Output', 'links_database.txt')
        # The serialization file to save the model
        languageModelSerializationFile = os.path.join('LanguageModel', 'Output', 'language_model.bin')
        
        # Start the LanguageModel:
        
        # Initialize the LanguageModel_Lexicon
        self.languageModel_lexicon = LanguageModel(configFileLanguageModel_lexicon, stopWordsFileName, languageModelSerializationFile, linksDBFile, datasetBuilder.trainSet)
        self.languageModel_lexicon.BuildLanguageModel()

         # Initialize the LanguageModel_Tasi
        self.languageModel_Tasi = LanguageModel(configFileLanguageModel_Tasi, stopWordsFileName, languageModelSerializationFile, linksDBFile, datasetBuilder.trainSet)
        self.languageModel_Tasi.BuildLanguageModel()
        
        # Configurations file xml of the features extractor
        configFileFeaturesExtractor_Lexicon = os.path.join('FeaturesExtractor', 'Configurations', 'Configurations-lexicon.xml')
        configFileFeaturesExtractor_Tasi = os.path.join('FeaturesExtractor', 'Configurations', 'Configurations-Tasi.xml')
        # The serialization file to save the features
        trainFeaturesSerializationFile = os.path.join('FeaturesExtractor', 'Output', 'train_features.bin')
        trainLabelsSerializationFile = os.path.join('FeaturesExtractor', 'Output', 'train_labels.bin')
        
        # Start the FeaturesExtractor:
        #-----------------------------    
        # Initialize the FeaturesExtractor _ Lexicon
        trainFeaturesExtractor_Lexicon = FeaturesExtractor(configFileFeaturesExtractor_Lexicon, trainFeaturesSerializationFile, trainLabelsSerializationFile, self.languageModel_lexicon, datasetBuilder.trainSet)
        trainFeaturesExtractor_Lexicon.ExtractNumTfFeatures()

        # Initialize the FeaturesExtractor _ Tasi
        trainFeaturesExtractor_Tasi = FeaturesExtractor(configFileFeaturesExtractor_Tasi, trainFeaturesSerializationFile, trainLabelsSerializationFile, self.languageModel_Tasi, datasetBuilder.trainSet)
        trainFeaturesExtractor_Tasi.ExtractNumTfFeatures()

        # The serialization file to save the features
        configFileClassifier_Lexicon = os.path.join('Classifier', 'Configurations', 'Configurations-lexicon.xml')
        configFileClassifier_Tasi = os.path.join('Classifier', 'Configurations', 'Configurations-Tasi.xml')
        modelSerializationFile = os.path.join('Classifier', 'Output', 'classifier_model.bin')
    
        # Start the Classifier:
        #---------------------
        print(trainFeaturesExtractor_Tasi.labels[:4])
        print([i['label'] for i in trainFeaturesExtractor_Lexicon.dataSet[:4]])
        self.classifier_Lexicon = Classifier(configFileClassifier_Lexicon, modelSerializationFile,  trainFeaturesExtractor_Lexicon.features, trainFeaturesExtractor_Lexicon.labels, [], [])
        self.classifier_Tasi = Classifier(configFileClassifier_Tasi, modelSerializationFile, trainFeaturesExtractor_Tasi.features,
                        trainFeaturesExtractor_Tasi.labels, [],[])
        
        # Train
        self.classifier_Lexicon.Train()
        self.classifier_Tasi.Train()
        
    def Classify(self, text, stockName):
	
        testSet = []
        for t in text:
            testSet.append({'label' : '', 'text' : t})

        if stockName == 'Tasi':
            # Configurations file xml of the features extractor
            configFileFeaturesExtractor = os.path.join('FeaturesExtractor', 'Configurations', 'Configurations-Tasi.xml')
            testFeaturesExtractor = FeaturesExtractor(configFileFeaturesExtractor, None, None, self.languageModel_Tasi, testSet)
            testFeaturesExtractor.ExtractNumTfFeatures()
            self.classifier_Tasi.testFeatures = testFeaturesExtractor.features
            self.classifier_Tasi.testTargets = []
            for i in range(len(self.classifier_Tasi.testFeatures)):		
            	#self.classifier_Tasi.testTargets[i] = 1
                self.classifier_Tasi.testTargets.append(1)
            label, acc, val = self.classifier_Tasi.Test()
        else:
            configFileFeaturesExtractor = os.path.join('FeaturesExtractor', 'Configurations', 'Configurations-lexicon.xml')
            testFeaturesExtractor = FeaturesExtractor(configFileFeaturesExtractor, None, None, self.languageModel_lexicon, testSet)
            self.classifier_Lexicon.testFeatures = testFeaturesExtractor.features
            self.classifier_Lexicon.testTargets = []
            for i in range(len(self.classifier_Lexicon.testFeatures)):		
                self.classifier_Lexicon.testTargets[i] = 1
            label, acc, val = self.classifier_Lexicon.Test()

        
        return label
        
