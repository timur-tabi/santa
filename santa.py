#!/usr/bin/python

import sys
import os
import re
import smtplib
import datetime
import random
from optparse import OptionParser, OptionGroup

parser = OptionParser(usage="usage: %prog [options] files-to-upload ...")
parser.add_option("-s", dest="send", help="send emails and save results", action="store_true")
parser.add_option("-t", dest="test", help="send to Timur instead", action="store_true")
parser.add_option("-v", dest="view", help="view results", action="store_true")

(options, args) = parser.parse_args()

people = []
nomatch = []
lastyear = []
thisyear = []

def send_email(giver, recipient):
	global options

	if options.test:
		toaddr = 'Timur Tabi <timur@tabi.org>'
	else:
		toaddr = '%s <%s>' % (giver[0], giver[1])
	fromaddr = 'Secret Santa <santa@augsburger.org>'
	year = str(datetime.date.today().year)

	body = 'Hello ' + giver[0].split()[0] + ',\n' + \
		'\n' + \
		'This year, you will be giving a Christmas gift to:\n' + \
		'\n' + \
		'\t\t' + recipient[0] + '\n'

	msg = 'To: ' + toaddr + '\n' + \
		'From: santa@augsburger.org\n' + \
		'Subject: Christmas ' + year + ' Secret Santa\n' + \
		'Content-type: text/plain\n' + \
		'\n' + \
		body

	print 'Sending email to', toaddr
	server = smtplib.SMTP('smtp-server.austin.rr.com')
	server.sendmail('santa@augsburger.org', toaddr, msg)
	server.quit()

def send_emails():
	for match in thisyear:
		send_email(match[0], match[1])

def get_names():
	global people

	filename = "people.txt"

	f = open(filename)
	lines = f.readlines()
	f.close

	for line in lines:
		(name, email) = line.split(',');
		people.append([name.strip(), email.strip()])

def find_person(name):
	for person in people:
		if name == person[0]:
			return person;

def read_lastyear():
	global lastyear

	filename = str(datetime.date.today().year - 1) + '.txt'

	f = open(filename)
	lines = f.readlines()
	f.close

	for line in lines:
		(giver, recipient) = line.split(',');
		giver = find_person(giver.strip())
		recipient = find_person(recipient.strip())
		lastyear.append([giver, recipient])

def read_nomatch():
	filename = "nomatch.txt"

	f = open(filename)
	lines = f.readlines()
	f.close

	for line in lines:
		(one, two) = line.split(',');
		one = find_person(one.strip())
		two = find_person(two.strip())
		nomatch.append([one, two])

def valid():
	global thisyear
	global lastyear
	global nomatch

	for match in thisyear:
		# Check for people giving gifts to themselves
		# This can happen because we just shuffle the lists
		if match[0] == match[1]:
			return False

		# Check for people who shoult not give gifts to each other (e.g. spouses)
		for no in nomatch:
			if match[0] == no[0] and match[1] == no[1]:
				return False
			if match[0] == no[1] and match[1] == no[0]:
				return False

		for last in lastyear:
			# Reject if the giver and recipient are the same as last year
			if match[0] == last[0] and match[1] == last[1]:
				return False
			# Reject if the giver and recipient are swapped from last year
			if match[0] == last[1] and match[1] == last[0]:
				return False

		# Check for pairs of people who just give each other gifts
		for match2 in thisyear:
			if match[0] == match2[1] and match[1] == match2[0]:
				return False

	return True

def find_santas():
	global thisyear
	global people

	while True:
		giver = people[:]
		recipient = people[:]
		random.shuffle(giver)
		random.shuffle(recipient)
		thisyear = zip(giver, recipient)
		if valid():
			break

def save_thisyear():
	global thisyear

	filename = str(datetime.date.today().year) + '.txt'

	f = open(filename, 'w')
	for match in thisyear:
		f.write('%s,%s\n' % (match[0][0], match[1][0]))
	f.close()

get_names()
read_nomatch()
read_lastyear()
find_santas()

if options.view:
	for match in thisyear:
		print match

if options.send:
	send_emails()
	save_thisyear()
