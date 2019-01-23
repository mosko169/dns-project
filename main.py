import dns.resolver
import csv
import traceback


NS_QUERY = "NS"


class AAnswer:
    def __init__(self, name, ip_addr):
        self.name = name
        self.ip_addr = ip_addr

    def __str__(self):
        return "name: " + self.name + " ip: " + self.ip_addr


class NSAnswer:
    def __init__(self, domain, name_servers, glue_records):
        self.domain = domain
        self.name_servers = name_servers
        self.glue_records = glue_records

    def __str__(self):
        answer_str = "domain: " + self.domain
        answer_str += "\nname servers: \n"
        answer_str += '\n'.join(self.name_servers)
        answer_str += "\nglue records: \n"
        answer_str+= '\n'.join([str(glue_record) for glue_record in self.glue_records])
        return answer_str


def parse_a_record(a_record):
    name = a_record.name.to_text()
    ipAddr = a_record.items[0].to_text()
    return AAnswer(name, ipAddr)


def parse_answer(domain, answer):
    nameservers = [entry.to_text() for entry in answer]
    glue_records = [parse_a_record(a_record) for a_record in answer.response.additional]
    return NSAnswer(domain, nameservers, glue_records)


def query_domains(domains):
    resolver = dns.resolver.Resolver()
    # use this when running from resolver
    #resolver.nameservers = ["127.0.0.1"]
    answers = []
    for domain in domains:
        try:
            answer = resolver.query(domain, NS_QUERY)
            answers.append(parse_answer(domain, answer))
        except Exception as e:
            traceback.print_exc()
            print("FAILED TO QUERY DOMAIN " + domain + " ERROR: " + str(e))

    return answers

def parse_domains_file(file_path):
    domains = []
    with open(file_path, "r", encoding='UTF-8') as domains_file:
        next(domains_file)
        reader = csv.reader(domains_file)
        for domain_entry in reader:
            try:
                domains.append(domain_entry[2])
            except Exception as e:
                continue
    return domains


def main():
    domains = ["google.com", "facebook.com", "microsoft.com"]
    answers = query_domains(domains)
    for answer in answers:
        print("************\n\n")
        print(answer)

if __name__ == '__main__':
    main()