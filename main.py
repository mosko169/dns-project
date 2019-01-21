import dns.resolver
import csv


def resolve(resolver, domain):
    return resolver.query(domain)

def main():
    resolver = dns.resolver.Resolver()
    # use this when running from resolver
    #resolver.nameservers = ["127.0.0.1"]

    answers = []
    with open(r"majestic_million.csv", "r", encoding='UTF-8') as domains_file:
        next(domains_file)
        reader = csv.reader(domains_file)
        for domain_entry in reader:
            domain = domain_entry[2]
            answers.append(resolver.query(domain))



if __name__ == '__main__':
    main()