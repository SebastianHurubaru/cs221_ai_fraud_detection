import csv, re, collections


class BayesNet:
    def __init__(self):
        self.countOfficers = collections.defaultdict(float)
        self.countPSC = collections.defaultdict(float)
        self.fraudulentCountOfficers = collections.defaultdict(float)
        self.fraudulentCountPSC = collections.defaultdict(float)

        self.locOfficer = collections.defaultdict(float)
        self.locPSC = collections.defaultdict(float)
        self.fraudulentLocOfficer = collections.defaultdict(float)
        self.fraudulentLocPSC = collections.defaultdict(float)

        self.numEntries = 0
        self.trainingSet = []
        self.model = None

    def processEntry(self, officers, officer_country, PSC, psc_country, label):
        self.numEntries += 1
        self.trainingSet.append((officers, officer_country, PSC, psc_country, label))

        for officer in officers:
            self.countOfficers[officer] += 1
            if label == "bad":
                self.fraudulentCountOfficers[officer] += 1

        for country in officer_country:
            self.locOfficer[country] += 1
            if label == "bad":
                self.fraudulentLocOfficer[country] += 1

        for psc in PSC:
            self.countPSC[psc] += 1
            if label == "bad":
                self.fraudulentCountPSC[psc] += 1

        for country in psc_country:
            self.locPSC[country] += 1
            if label == "bad":
                self.fraudulentLocPSC[country] += 1


    def finalizeParsing(self):
        maxCountOfficer = float(max(self.fraudulentCountOfficers.values()))
        for officer in self.fraudulentCountOfficers:
            self.fraudulentCountOfficers[officer] /= maxCountOfficer

        maxCountPSC = float(max(self.fraudulentCountPSC.values()))
        for psc in self.fraudulentCountPSC:
            self.fraudulentCountPSC[psc] /= maxCountPSC

        sumValues = sum(self.fraudulentLocOfficer.values())
        for country in self.fraudulentLocOfficer:
            self.fraudulentLocOfficer[country] /= sumValues

        sumValues = sum(self.fraudulentLocPSC.values())
        for country in self.fraudulentLocPSC:
            self.fraudulentLocPSC[country] /= sumValues

        self.maxOffLocScore = 0
        self.maxPSCLocScore = 0

        for i in self.trainingSet:
            score = 0
            for j in i[1]:
                score += self.fraudulentLocOfficer[j]
            if len(i[1]) != 0:
                score /= float(len(i[1]))
            else:
                score = 0
            if score > self.maxOffLocScore:
                self.maxOffLocScore = score

            score = 0
            for j in i[3]:
                score += self.fraudulentLocPSC[j]
            if len(i[3]) != 0:
                score /= float(len(i[3]))
            else:
                score = 0
            if score > self.maxPSCLocScore:
                self.maxPSCLocScore = score

    def discretize(self, val):
        if val > 0 and val < 0.25:
            return 0
        elif val < 0.50:
            return 1
        elif val < 0.75:
            return 2
        else:
            return 3

    def computeOS(self, officers):
        freq = 0
        for officer in officers:
            freq += 1 if self.fraudulentCountOfficers[officer] else 0

        return self.discretize(freq/float(len(officers))) if len(officers) else self.discretize(1/2.)

    def computePS(self, PSC):
        freq = 0
        for psc in PSC:
            freq += 1 if self.fraudulentCountPSC[psc] else 0

        return self.discretize(freq/float(len(PSC))) if len(PSC) else self.discretize(1/2.)


    def computeOCS(self, officer_countries):
        score = 0

        if len(officer_countries) == 0:
            return self.discretize(1/2.)
        for country in officer_countries:
            score = self.fraudulentLocOfficer[country]

        score = score/float(len(officer_countries))/self.maxOffLocScore
        return self.discretize(score)

    def computePCS(self, psc_countries):
        score = 0

        if len(psc_countries) == 0:
            return self.discretize(1/2.)

        for country in psc_countries:
            score = self.fraudulentLocOfficer[country]

        score = score/float(len(psc_countries))/self.maxPSCLocScore
        return self.discretize(score)

    def trainModel(self):
        #self.trainingSet.append((officers, officer_country, PSC, psc_country, label))
        self.model = collections.defaultdict(int)
        for i in self.trainingSet:
            x = self.computeOS(i[0])
            y = self.computePS(i[2])
            z = self.computeOCS(i[1])
            w = self.computePCS(i[3])
            label = i[4]

            self.model[((x, y, z, w), label)] += 1

    def infer(self, officers, officer_country, PSC, psc_country):
        x = self.computeOS(officers)
        y = self.computePS(PSC)
        z = self.computeOCS(officer_country)
        w = self.computePCS(psc_country)

        if self.model[((x, y, z, w), "bad")] + self.model[((x, y, z, w), "")] == 0:
            return 1/2.

        return self.model[((x, y, z, w), "bad")] / float(self.model[((x, y, z, w), '')] + self.model[((x, y, z, w), "bad")])



NUM_ENTRIES = 4200
PERSON_FIND_REGEXP = '(?<=name\": \")[^\"]*'
COUNTRY_FIND_REGEXP = '(?<=country\": \")[^\"]*'
regexp = re.compile(PERSON_FIND_REGEXP)
country_regexp = re.compile(COUNTRY_FIND_REGEXP)

newBayes = BayesNet()
with open('company.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    bad_num = 0
    good_num = 0
    flag = 0
    for row in csv_reader:
        if not flag:
            flag = 1
            continue

        if bad_num > NUM_ENTRIES and good_num > NUM_ENTRIES:
            break
        elif row[4] == "bad" and bad_num <= NUM_ENTRIES:
            bad_num += 1
        elif row[4] != "bad" and good_num <= NUM_ENTRIES:
            good_num += 1
        else:
            continue

        officer_data = row[2]
        psc_data = row[3]
        label = row[4]

        

        officers = regexp.findall(officer_data)
        officer_country = country_regexp.findall(officer_data)
        psc = regexp.findall(psc_data)
        psc_country = country_regexp.findall(psc_data)

        newBayes.processEntry(officers, officer_country, psc, psc_country, label)
        

newBayes.finalizeParsing()
newBayes.trainModel()
print newBayes.model
with open('company.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    bad_num = 0
    good_num = 0
    flag = 0
    counter = 0
    correct = 0
    for row in csv_reader:
        if not flag:
            flag = 1
            continue

        if row[4] == "bad" and bad_num <= NUM_ENTRIES:
            bad_num += 1
            continue
        elif row[4] != "bad" and good_num <= NUM_ENTRIES:
            good_num += 1
            continue

        officer_data = row[2]
        psc_data = row[3]
        label = row[4]

        counter += 1

        

        officers = regexp.findall(officer_data)
        officer_country = country_regexp.findall(officer_data)
        psc = regexp.findall(psc_data)
        psc_country = country_regexp.findall(psc_data)

        if newBayes.infer(officers, officer_country, psc, psc_country) > 0.5 and label == "bad":
            correct += 1
        elif newBayes.infer(officers, officer_country, psc, psc_country) < 0.5 and label != "bad":
            correct += 1

print counter
print correct / float(counter)